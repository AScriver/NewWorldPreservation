Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$scratchPath = Join-Path $workspaceRoot ('.scratch\rep-launch-lifecycle-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $scratchPath -ErrorAction Stop | Out-Null
$sourcePath = Join-Path $workspaceRoot 'scripts\Invoke-RepAnchorTrialWindow.ps1'
$parseTokens = $null
$parseDiagnostics = $null
$sourceAst = [Management.Automation.Language.Parser]::ParseFile($sourcePath,[ref]$parseTokens,[ref]$parseDiagnostics)
if ($parseDiagnostics.Count -gt 0) { throw 'Original function source has parser diagnostics.' }
$functionNames = @('Write-NewDurableJson','Read-OwnedProcessPath','Read-OwnedParentMetadata','Start-OwnedSerialLauncher','Stop-OwnedAnchorLauncher','Stop-OwnedTrialClient')
$functionNodes = @($sourceAst.FindAll({ param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] },$true))
foreach ($functionName in $functionNames) {
    $functionNode = @($functionNodes | Where-Object Name -eq $functionName)
    if ($functionNode.Count -ne 1) { throw "Expected exactly one AST function: $functionName" }
    . ([scriptblock]::Create($functionNode[0].Extent.Text))
}
$script:originalWrite = (Get-Command Write-NewDurableJson).ScriptBlock
$script:expectedClientHash = 'dff94b76032fdd528c936e9f9313dea1736ad5432d32cb068933b8a3d5ed8096'
$script:expectedLauncherHash = '5a9217fafb5656c0b72b516583287ca362c3e1a87e1b5b515ad64a6402b292ec'
$script:runPath = $null
$script:ownedClientPath = $null
$script:clientExecutable = Join-Path $scratchPath 'synthetic-client.exe'
$script:ownedLauncherObject = $null
$script:scenario = ''
$script:hashCalls = 0
$script:startCount = 0
$script:stopCount = 0
$script:launcherKilled = 0
$script:gameVisible = $false
$script:launcher = $null
$script:game = $null
$script:events = [Collections.Generic.List[string]]::new()
$script:observations = [Collections.Generic.List[object]]::new()

function New-FakeProcess {
    param([int]$ProcessId,[string]$ProcessName,[string]$Path)
    $fake = [pscustomobject]@{ Id=$ProcessId; ProcessName=$ProcessName; Path=$Path; StartTime=[DateTime]::UtcNow.AddSeconds(1); HasExited=$false }
    $fake | Add-Member -MemberType ScriptMethod -Name Kill -Value { $this.HasExited = $true; $script:launcherKilled++ }
    $fake | Add-Member -MemberType ScriptMethod -Name WaitForExit -Value { param([int]$Milliseconds) return [bool]$this.HasExited }
    return $fake
}
function Write-TrialWindowEvent {
    param([string]$State,[hashtable]$Details)
    $script:events.Add($State)
}
function Write-NewDurableJson {
    param([string]$Path,[object]$Value)
    if ($script:scenario -eq 'manifest_fault' -and $Path -like '*anchor-launch-manifest.json') { throw 'synthetic manifest write failure' }
    if ($script:scenario -eq 'identity_fault' -and $Path -eq $script:ownedClientPath) { throw 'synthetic owned-client write failure' }
    & $script:originalWrite -Path $Path -Value $Value
}
function Get-Process {
    [CmdletBinding()]
    param([string[]]$Name,[int]$Id)
    if ($PSBoundParameters.ContainsKey('Id')) {
        if ($script:gameVisible -and $Id -eq $script:game.Id) { return $script:game }
        return
    }
    if ($Name -contains 'Steam') { return [pscustomobject]@{ Id=99991; ProcessName='Steam' } }
    if ($script:gameVisible -and $Name -contains 'NewWorld') { return $script:game }
}
function Get-FileHash {
    [CmdletBinding()]
    param([string]$LiteralPath,[string]$Algorithm)
    if ($LiteralPath -like '*NewWorldLauncher.exe') { return [pscustomobject]@{ Hash=$script:expectedLauncherHash } }
    if ($LiteralPath -eq $script:clientExecutable) {
        $script:hashCalls++
        if ($script:scenario -eq 'disk_drift' -and $script:hashCalls -gt 1) { return [pscustomobject]@{ Hash=('0' * 64) } }
        return [pscustomobject]@{ Hash=$script:expectedClientHash }
    }
    throw 'Unexpected hash input'
}
function Get-CimInstance {
    [CmdletBinding()]
    param([string]$ClassName,[string]$Filter)
    if ($script:scenario -eq 'cim_empty') { return }
    if ($script:scenario -eq 'cim_no_parent') { return [pscustomobject]@{ Name='synthetic-no-parent' } }
    return [pscustomobject]@{ ParentProcessId=$script:launcher.Id }
}
function Start-Process {
    [CmdletBinding()]
    param([string]$FilePath,[string]$WorkingDirectory,[hashtable]$Environment,[string]$WindowStyle,[switch]$PassThru)
    $script:startCount++
    if ($script:scenario -eq 'stop_during_create') {
        [IO.File]::WriteAllText((Join-Path $script:runPath 'stop.request'),'stop')
        $script:stopDuringCreateReturned = $true
    }
    $script:launcher = New-FakeProcess -ProcessId (50000 + $script:startCount) -ProcessName 'NewWorldLauncher' -Path $FilePath
    if ($script:scenario -in @('stop_during_create','disk_drift','identity_fault','path_throws','cim_empty','cim_no_parent')) {
        $script:game = New-FakeProcess -ProcessId (60000 + $script:startCount) -ProcessName 'NewWorld' -Path $script:clientExecutable
        if ($script:scenario -eq 'path_throws') {
            $script:game.PSObject.Properties.Remove('Path')
            $script:game | Add-Member -MemberType ScriptProperty -Name Path -Value { throw [System.Management.Automation.PropertyNotFoundException]::new('synthetic protected Path accessor') }
        }
        $script:gameVisible = $true
    }
    return $script:launcher
}
function Stop-Process {
    [CmdletBinding()]
    param([int]$Id)
    if ($Id -ne $script:game.Id) { throw 'Synthetic stop targeted an unexpected process.' }
    $script:stopCount++
    $script:game.HasExited = $true
    $script:gameVisible = $false
}

function Assert-Condition {
    param([bool]$Condition,[string]$Message)
    if (-not $Condition) { throw $Message }
}
function Reset-Case {
    param([string]$CaseName)
    $script:scenario = $CaseName
    $script:runPath = Join-Path $scratchPath ($CaseName + '-' + [Guid]::NewGuid().ToString('N'))
    $null = New-Item -ItemType Directory -Path $script:runPath
    $script:ownedClientPath = Join-Path $script:runPath 'owned-client.json'
    $script:ownedLauncherObject = $null
    $script:hashCalls = 0
    $script:startCount = 0
    $script:stopCount = 0
    $script:launcherKilled = 0
    $script:gameVisible = $false
    $script:launcher = $null
    $script:game = $null
    $script:stopDuringCreateReturned = $false
    $script:events.Clear()
}
function Record-Case {
    param([string]$CaseName,[string]$Outcome)
    $script:observations.Add([ordered]@{
        case=$CaseName; outcome=$Outcome; start_calls=$script:startCount; stop_calls=$script:stopCount
        launcher_kills=$script:launcherKilled; launcher_retained=($null -ne $script:ownedLauncherObject)
        launcher_manifest=(Test-Path -LiteralPath (Join-Path $script:runPath 'anchor-launch-manifest.json'))
        owned_client_identity=(Test-Path -LiteralPath $script:ownedClientPath)
        game_visible=$script:gameVisible; events=@($script:events)
    })
}

Reset-Case 'deadline_past'
Start-OwnedSerialLauncher -Deadline ([DateTime]::UtcNow.AddSeconds(-1))
Assert-Condition ($script:startCount -eq 0) 'Deadline past created process.'
Record-Case 'deadline_past' 'admission_closed_no_process'

Reset-Case 'stop_before_admission'
[IO.File]::WriteAllText((Join-Path $script:runPath 'stop.request'),'stop')
Start-OwnedSerialLauncher -Deadline ([DateTime]::UtcNow.AddSeconds(10))
Assert-Condition ($script:startCount -eq 0) 'Stop-before-admission created process.'
Record-Case 'stop_before_admission' 'admission_closed_no_process'

Reset-Case 'stop_during_create'
Start-OwnedSerialLauncher -Deadline ([DateTime]::UtcNow.AddSeconds(10))
Assert-Condition ($script:stopDuringCreateReturned -and (Test-Path -LiteralPath (Join-Path $script:runPath 'anchor-launch-manifest.json'))) 'Stop during factory prevented ownership manifest.'
$published = Get-Content -LiteralPath (Join-Path $script:runPath 'anchor-launch-manifest.json') -Raw | ConvertFrom-Json -DateKind String
Assert-Condition ($published.original_launcher_process_id -eq $script:launcher.Id -and $published.original_launcher_start_time_utc -eq $script:launcher.StartTime.ToUniversalTime().ToString('o') -and $published.run_directory -eq $script:runPath) 'Manifest did not bind this launch and run.'
Stop-OwnedAnchorLauncher
Stop-OwnedTrialClient
Assert-Condition ($script:launcherKilled -eq 1 -and $script:stopCount -eq 1 -and -not $script:gameVisible) 'Stop during factory cleanup failed.'
Record-Case 'stop_during_create' 'manifest_published_then_owned_cleanup'

Reset-Case 'manifest_fault'
$caught = $false
try { Start-OwnedSerialLauncher -Deadline ([DateTime]::UtcNow.AddSeconds(10)) } catch { $caught = $_.Exception.Message -like '*synthetic manifest write failure*' }
Assert-Condition ($caught -and $script:ownedLauncherObject -eq $script:launcher) 'Manifest failure lost created launcher object.'
Stop-OwnedAnchorLauncher
Assert-Condition ($script:launcherKilled -eq 1) 'Manifest failure did not kill retained launcher.'
Record-Case 'manifest_fault' 'retained_launcher_killed_after_write_failure'

Reset-Case 'disk_drift'
$caught = $false
try { Start-OwnedSerialLauncher -Deadline ([DateTime]::UtcNow.AddSeconds(10)) } catch { $caught = $_.Exception.Message -like '*Launcher/update changed candidate*' }
Assert-Condition ($caught -and (Test-Path -LiteralPath $script:ownedClientPath)) 'Disk drift occurred without owned identity publication.'
$driftIdentity = Get-Content -LiteralPath $script:ownedClientPath -Raw | ConvertFrom-Json -DateKind String
Assert-Condition ($driftIdentity.process_id -eq $script:game.Id -and $driftIdentity.installed_candidate_sha256_after_launch -eq ('0' * 64)) 'Drift identity did not bind game and changed hash.'
Stop-OwnedAnchorLauncher
Stop-OwnedTrialClient
Assert-Condition ($script:launcherKilled -eq 1 -and $script:stopCount -eq 1 -and -not $script:gameVisible) 'Disk drift owned-client cleanup failed.'
Record-Case 'disk_drift' 'identity_published_before_rejection_and_cleanup'

Reset-Case 'identity_fault'
$caught = $false
try { Start-OwnedSerialLauncher -Deadline ([DateTime]::UtcNow.AddSeconds(10)) } catch { $caught = $_.Exception.Message -like '*synthetic owned-client write failure*' }
Assert-Condition ($caught -and -not (Test-Path -LiteralPath $script:ownedClientPath)) 'Identity publication fault did not occur.'
Stop-OwnedAnchorLauncher
$cleanupCaught = $false
try { Stop-OwnedTrialClient } catch { $cleanupCaught = $_.Exception.Message -like '*no recorded owned identity*' }
Assert-Condition ($cleanupCaught -and $script:stopCount -eq 0 -and $script:gameVisible -and $script:launcherKilled -eq 1) 'Missing identity did not fail closed with game still visible.'
Record-Case 'identity_fault' 'launcher_killed_game_unclaimed_containment_must_remain'

Reset-Case 'path_throws'
Start-OwnedSerialLauncher -Deadline ([DateTime]::UtcNow.AddSeconds(10))
Assert-Condition ((Test-Path -LiteralPath $script:ownedClientPath) -and $script:events.Contains('OWNED_GAME_PATH_UNAVAILABLE')) 'Throwing game Path prevented startup identity or limitation event.'
$protectedIdentity = Get-Content -LiteralPath $script:ownedClientPath -Raw | ConvertFrom-Json -DateKind String
Assert-Condition ($protectedIdentity.process_id -eq $script:game.Id -and $protectedIdentity.live_path_verified -eq $false) 'Protected game Path was incorrectly treated as verified.'
Stop-OwnedAnchorLauncher
Stop-OwnedTrialClient
Assert-Condition ($script:launcherKilled -eq 1 -and $script:stopCount -eq 1 -and $script:events.Contains('OWNED_CLEANUP_PATH_UNAVAILABLE')) 'Throwing cleanup Path prevented PID/start-based owned cleanup.'
Record-Case 'path_throws' 'unavailable_path_logged_identity_and_cleanup_succeeded'

foreach ($caseName in @('cim_empty','cim_no_parent')) {
    Reset-Case $caseName
    Start-OwnedSerialLauncher -Deadline ([DateTime]::UtcNow.AddSeconds(10))
    Assert-Condition ((Test-Path -LiteralPath $script:ownedClientPath) -and $script:events.Contains('OWNED_GAME_PARENT_METADATA_UNAVAILABLE')) 'Missing CIM parent prevented identity or limitation event.'
    $missingParentIdentity = Get-Content -LiteralPath $script:ownedClientPath -Raw | ConvertFrom-Json -DateKind String
    Assert-Condition ($null -eq $missingParentIdentity.parent_process_id -and $missingParentIdentity.direct_parent_pid_matches_launcher -eq $false -and $missingParentIdentity.launcher_ancestry_verified -eq $false) 'Missing CIM parent was incorrectly attributed.'
    Stop-OwnedAnchorLauncher
    Stop-OwnedTrialClient
    Assert-Condition ($script:launcherKilled -eq 1 -and $script:stopCount -eq 1 -and -not $script:gameVisible) 'Missing CIM parent prevented owned cleanup.'
    Record-Case $caseName 'missing_parent_nullable_and_owned_cleanup_succeeded'
}

$sourceHash = (Microsoft.PowerShell.Utility\Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash.ToLowerInvariant()
$result = [ordered]@{ schema=1; source_sha256=$sourceHash; source_functions=$functionNames; environment='synthetic PowerShell mocks; no actual process launch'; checks=@($script:observations); all_passed=$true }
[IO.File]::WriteAllText((Join-Path $scratchPath 'results.json'),(($result | ConvertTo-Json -Depth 7) + "`n"),[Text.UTF8Encoding]::new($false))
$result | ConvertTo-Json -Depth 7
