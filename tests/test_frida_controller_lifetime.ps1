Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$controllerPath = Join-Path $workspaceRoot 'scripts\Invoke-FridaPrivateTrial.ps1'
$parseTokens = $null
$parseErrors = $null
$controllerAst = [System.Management.Automation.Language.Parser]::ParseFile(
    $controllerPath,[ref]$parseTokens,[ref]$parseErrors)
if (@($parseErrors).Count -ne 0) { throw 'Controller does not parse.' }
$definitions = @($controllerAst.FindAll({
    param($candidateNode)
    $candidateNode -is [System.Management.Automation.Language.FunctionDefinitionAst]
},$true))
foreach ($functionName in @('Publish-StopRequest','Get-TrialLifetimeArguments','Wait-OwnedDispatch',
                            'Get-CurrentRegistrationTrialArguments','Assert-CurrentRegistrationTrialPreflight')) {
    $selected = @($definitions | Where-Object { $_.Name -ceq $functionName })
    if ($selected.Count -ne 1) { throw 'Expected one isolated lifecycle function.' }
    . ([scriptblock]::Create($selected[0].Extent.Text))
}
$source = [IO.File]::ReadAllText($controllerPath)
$registrationPreflightCall = $source.IndexOf('Assert-CurrentRegistrationTrialPreflight -Manifest $manifest')
$firstFirewallMutation = $source.IndexOf('New-NetFirewallRule -Name')
$firstHostsMutation = $source.IndexOf("'-Action','Prepare'")
$firstChildStart = $source.IndexOf("Start-OwnedChild -Name 'https-v4'")
if ($registrationPreflightCall -lt 0 -or $registrationPreflightCall -ge $firstFirewallMutation -or
    $registrationPreflightCall -ge $firstHostsMutation -or $registrationPreflightCall -ge $firstChildStart) { throw 'Current registration preflight follows resource setup.' }
if ($source.IndexOf('$dtlsArguments += $registrationArguments') -lt 0 -or
    $source.IndexOf('$dtlsArguments += $registrationArguments') -ge $source.IndexOf("Start-OwnedChild -Name 'dtls'")) { throw 'Current registration selection is not forwarded to DTLS.' }
if ($source.IndexOf('$dtlsArguments += $registrationArguments') -le $firstChildStart -or
    @([regex]::Matches($source,[regex]::Escape('$dtlsArguments += $registrationArguments'))).Count -ne 1 -or
    $source.Contains('$commonArguments += $registrationArguments') -or
    $source.Contains('$manifest.frida_dispatch + $registrationArguments')) { throw 'Current selection leaked outside the DTLS argument path.' }
$registrationTestRoot = Join-Path $workspaceRoot ('.scratch\registration285-controller-'+[Guid]::NewGuid().ToString('N'))
if (-not ([IO.Path]::GetFullPath($registrationTestRoot)).StartsWith(([IO.Path]::GetFullPath((Join-Path $workspaceRoot '.scratch')))+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Registration test path escaped scratch ownership.' }
$null = New-Item -ItemType Directory -Path $registrationTestRoot
try {
    $bodyPath = Join-Path $registrationTestRoot 'body with spaces.bin'
    [IO.File]::WriteAllBytes($bodyPath,[byte[]]::new(18))
    $bodyDigest = (Get-FileHash -LiteralPath $bodyPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $pythonPath = (Get-Command python -ErrorAction Stop).Source
    $manifestObject = [pscustomobject]@{
        current_registration=$true; application_contract='carrier-register'
        current_request_type_index=0; current_response_type_index=4294967295
        current_response_body=$bodyPath; current_response_body_sha256=$bodyDigest
        protocol_python=$pythonPath; protocol_packages=(Join-Path $workspaceRoot '.venv\Lib\site-packages')
        files=@()
    }
    $registrationArguments = @(Get-CurrentRegistrationTrialArguments -Manifest $manifestObject -WorkspaceRoot $workspaceRoot)
    if (($registrationArguments -join '|') -cne "--current-request-type-index|0|--current-response-type-index|4294967295|--current-response-body|$bodyPath|--current-response-body-sha256|$bodyDigest") { throw 'Selected registration arguments changed.' }
    $paths = @($pythonPath,$bodyPath) + @('private_current_registration_trial.py',
        'current_registration_request_body.py','current_registration_request_stream.py',
        'current_registration_request_receive.py','current_registration_response_body.py',
        'current_registration_response_record.py' | ForEach-Object { Join-Path $workspaceRoot (Join-Path 'scripts' $_) })
    $manifestObject.files = @($paths | ForEach-Object { [pscustomobject]@{path=$_;sha256=(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant()} })
    Assert-CurrentRegistrationTrialPreflight -Manifest $manifestObject -RegistrationArguments $registrationArguments -ScriptRoot (Join-Path $workspaceRoot 'scripts')
    $manifestObject | Add-Member -NotePropertyName registration_server_version -NotePropertyValue '[RETAIL].Javelin.1.400.6031.6004151'
    $manifestObject | Add-Member -NotePropertyName registration_server_version_receipt -NotePropertyValue (Join-Path $registrationTestRoot 'owned-version.json')
    foreach ($stageName in @('heartbeat_15d','self_ident_default','spawn_point_notification',
                            'world_activation','context_gate_observer','self_ident_current_length')) {
        $manifestObject | Add-Member -NotePropertyName $stageName -NotePropertyValue $true
    }
    $bootstrapArguments = @(Get-CurrentRegistrationTrialArguments -Manifest $manifestObject -WorkspaceRoot $workspaceRoot)
    if (($bootstrapArguments -join '|') -cne ($registrationArguments -join '|')) { throw 'Current bootstrap changed the literal BODY selection.' }
    Assert-CurrentRegistrationTrialPreflight -Manifest $manifestObject -RegistrationArguments $bootstrapArguments -ScriptRoot (Join-Path $workspaceRoot 'scripts')
    foreach ($stageName in @('registration_server_version','registration_server_version_receipt',
                            'heartbeat_15d','self_ident_default','spawn_point_notification',
                            'world_activation','context_gate_observer','self_ident_current_length')) {
        $manifestObject.PSObject.Properties.Remove($stageName)
    }
    if (-not $source.Contains('if ($manifest.PSObject.Properties.Name -contains ''registration_server_version'')') -or
        -not $source.Contains('if ($manifest.PSObject.Properties.Name -contains ''world_activation'')') -or
        -not $source.Contains('if ($manifest.PSObject.Properties.Name -contains ''self_ident_current_length'')')) { throw 'Downstream version, map or length guards missing.' }
    foreach ($invalidNumber in @(-1,4294967296,1.5,$true)) {
        $manifestObject.current_request_type_index = $invalidNumber
        try { $null = Get-CurrentRegistrationTrialArguments -Manifest $manifestObject -WorkspaceRoot $workspaceRoot; throw 'Invalid JSON selector accepted.' }
        catch { if ($_.Exception.Message -ceq 'Invalid JSON selector accepted.') { throw } }
    }
    $manifestObject.current_request_type_index = 0
    $manifestObject.current_registration = $false
    try { $null = Get-CurrentRegistrationTrialArguments -Manifest $manifestObject -WorkspaceRoot $workspaceRoot; throw 'Disabled profile accepted ancillary inputs.' }
    catch { if ($_.Exception.Message -ceq 'Disabled profile accepted ancillary inputs.') { throw } }
    $manifestObject.current_registration = $true
    $manifestObject.current_response_body_sha256 = $null
    try { $null = Get-CurrentRegistrationTrialArguments -Manifest $manifestObject -WorkspaceRoot $workspaceRoot; throw 'Partial current profile accepted.' }
    catch { if ($_.Exception.Message -ceq 'Partial current profile accepted.') { throw } }
    $manifestObject.current_response_body_sha256 = $bodyDigest
    $manifestObject.current_registration = 'true'
    try { $null = Get-CurrentRegistrationTrialArguments -Manifest $manifestObject -WorkspaceRoot $workspaceRoot; throw 'Nonboolean current selection accepted.' }
    catch { if ($_.Exception.Message -ceq 'Nonboolean current selection accepted.') { throw } }
    $manifestObject.current_registration = $true
    # Execute the actual creation-admission statements in isolation. No controller,
    # client, routing or service starts. Only the mapping hash read is modeled here;
    # Python canonical preparation and the private proposal verify real mapping bytes.
    $creationStart = $source.IndexOf('$creationArguments = @()')
    $creationEnd = $source.IndexOf('foreach ($requiredBinding in $requiredBindings)')
    if ($creationStart -lt 0 -or $creationEnd -le $creationStart -or $creationEnd -ge $firstHostsMutation) { throw 'Creation admission moved after resources.' }
    $controllerScriptRoot = Split-Path -Parent $controllerPath
    # Scriptblock-created code has no file-backed PSScriptRoot. Supply the same
    # directory under a task variable; leave the admission expressions unchanged.
    $creationAdmission = [scriptblock]::Create($source.Substring($creationStart,$creationEnd-$creationStart).Replace('$PSScriptRoot','$controllerScriptRoot'))
    $clientDirectory = Join-Path $registrationTestRoot 'synthetic-client'
    $null = New-Item -ItemType Directory -Path $clientDirectory
    $mappingPath = Join-Path $clientDirectory 'typeindex.json'
    [IO.File]::WriteAllText($mappingPath,'synthetic hash-boundary model only')
    $characterPath = Join-Path $registrationTestRoot 'character.json'
    [IO.File]::WriteAllText($characterPath,'{}')
    $characterDigest = (Get-FileHash -LiteralPath $characterPath -Algorithm SHA256).Hash.ToLowerInvariant()
    function Get-FileHash {
        param([string]$LiteralPath,[string]$Algorithm)
        if ($LiteralPath -ieq $mappingPath) { return [pscustomobject]@{Hash='f1e2385f333455a0524ed92ff2a3cb1c66824b1949462d0d12e9f9c06c82be75'} }
        Microsoft.PowerShell.Utility\Get-FileHash -LiteralPath $LiteralPath -Algorithm $Algorithm
    }
    try {
        $creationSelection = @{
            player_creation_candidate=$true; trial_character_path=$characterPath
            trial_character_sha256=$characterDigest; type_index_path=$mappingPath
            delivery_mode='resource-index'; trial_known_empty_occupancy=$true
            registration_server_version='[RETAIL].Javelin.1.400.6031.6004151'
            heartbeat_15d=$true; self_ident_default=$true; self_ident_current_length=$true
            spawn_point_notification=$true; world_activation=$true; context_gate_observer=$true
        }
        foreach ($selectedName in $creationSelection.Keys) {
            $manifestObject | Add-Member -NotePropertyName $selectedName -NotePropertyValue $creationSelection[$selectedName]
        }
        $manifest = $manifestObject
        $requiredBindings = @()
        . $creationAdmission
        $joinedArguments = @(Get-CurrentRegistrationTrialArguments -Manifest $manifest -WorkspaceRoot $workspaceRoot)
        if (($joinedArguments -join '|') -cne ($registrationArguments -join '|') -or
            ($creationArguments -join '|') -cne "--trial-character|$characterPath|--trial-character-sha256|$characterDigest|--trial-known-empty-occupancy" -or
            $requiredBindings -notcontains $characterPath -or $requiredBindings -notcontains $mappingPath) { throw 'Current creation lost independent BODY/identity bindings.' }
        Assert-CurrentRegistrationTrialPreflight -Manifest $manifest -RegistrationArguments $joinedArguments -ScriptRoot (Join-Path $workspaceRoot 'scripts')
        foreach ($selectedName in $creationSelection.Keys) {
            $savedValue = $manifest.$selectedName
            $manifest.PSObject.Properties.Remove($selectedName)
            try { . $creationAdmission; throw 'Incomplete selected creation admitted.' }
            catch { if ($_.Exception.Message -ceq 'Incomplete selected creation admitted.') { throw } }
            $manifest | Add-Member -NotePropertyName $selectedName -NotePropertyValue $savedValue
        }
        foreach ($badSelection in @($false,'true',1)) {
            $manifest.player_creation_candidate = $badSelection
            try { . $creationAdmission; throw 'Invalid creation selection admitted ancillary inputs.' }
            catch { if ($_.Exception.Message -ceq 'Invalid creation selection admitted ancillary inputs.') { throw } }
        }
        $manifest.player_creation_candidate = $true
        $manifest.trial_character_sha256 = '0'*64
        try { . $creationAdmission; throw 'Stale character admitted.' }
        catch { if ($_.Exception.Message -ceq 'Stale character admitted.') { throw } }
        $manifest.trial_character_sha256 = $characterDigest
        $manifest | Add-Member -NotePropertyName trial_occupied_low64 -NotePropertyValue @('2')
        try { . $creationAdmission; throw 'Conflicting occupancy admitted.' }
        catch { if ($_.Exception.Message -ceq 'Conflicting occupancy admitted.') { throw } }
        $manifest.PSObject.Properties.Remove('trial_occupied_low64')
    } finally {
        Remove-Item -LiteralPath 'Function:\Get-FileHash'
        foreach ($selectedName in $creationSelection.Keys) { $manifestObject.PSObject.Properties.Remove($selectedName) }
    }
    $manifestObject.application_contract = 'other'
    try { $null = Get-CurrentRegistrationTrialArguments -Manifest $manifestObject -WorkspaceRoot $workspaceRoot; throw 'Wrong contract accepted.' }
    catch { if ($_.Exception.Message -ceq 'Wrong contract accepted.') { throw } }
    $manifestObject.application_contract = 'carrier-register'
    foreach ($mutation in @('missing','duplicate','stale')) {
        $savedBindings = $manifestObject.files
        if ($mutation -ceq 'missing') { $manifestObject.files = @($savedBindings | Where-Object { $_.path -ine $bodyPath }) }
        if ($mutation -ceq 'duplicate') { $manifestObject.files = @($savedBindings) + $savedBindings[1] }
        if ($mutation -ceq 'stale') { $manifestObject.files = @($savedBindings | ForEach-Object { if ($_.path -ieq $pythonPath) { [pscustomobject]@{path=$_.path;sha256=('0'*64)} } else { $_ } }) }
        try { Assert-CurrentRegistrationTrialPreflight -Manifest $manifestObject -RegistrationArguments $registrationArguments -ScriptRoot (Join-Path $workspaceRoot 'scripts'); throw 'Invalid selected binding accepted.' }
        catch { if ($_.Exception.Message -ceq 'Invalid selected binding accepted.') { throw } }
        $manifestObject.files = $savedBindings
    }
    $savedBindings = $manifestObject.files
    $manifestObject.files = @($savedBindings | ForEach-Object { if ($_.path -ieq $bodyPath) { [pscustomobject]@{path=$_.path;sha256=('0'*64)} } else { $_ } })
    try { Assert-CurrentRegistrationTrialPreflight -Manifest $manifestObject -RegistrationArguments $registrationArguments -ScriptRoot (Join-Path $workspaceRoot 'scripts'); throw 'Different bound BODY digest accepted.' }
    catch { if ($_.Exception.Message -ceq 'Different bound BODY digest accepted.') { throw } }
    $manifestObject.files = $savedBindings
    [IO.File]::WriteAllBytes($bodyPath,[byte[]]::new(17))
    try { Assert-CurrentRegistrationTrialPreflight -Manifest $manifestObject -RegistrationArguments $registrationArguments -ScriptRoot (Join-Path $workspaceRoot 'scripts'); throw 'Changed BODY accepted.' }
    catch { if ($_.Exception.Message -ceq 'Changed BODY accepted.') { throw } }
    $changedDigest = (Get-FileHash -LiteralPath $bodyPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $manifestObject.current_response_body_sha256 = $changedDigest
    $changedArguments = @(Get-CurrentRegistrationTrialArguments -Manifest $manifestObject -WorkspaceRoot $workspaceRoot)
    $manifestObject.files = @($savedBindings | ForEach-Object { if ($_.path -ieq $bodyPath) { [pscustomobject]@{path=$_.path;sha256=$changedDigest} } else { $_ } })
    try { Assert-CurrentRegistrationTrialPreflight -Manifest $manifestObject -RegistrationArguments $changedArguments -ScriptRoot (Join-Path $workspaceRoot 'scripts'); throw 'Verifier accepted noncanonical BODY.' }
    catch { if ($_.Exception.Message -ceq 'Verifier accepted noncanonical BODY.') { throw } }
    Write-Output 'Current registration controller preflight: selected arguments, bindings, metadata, profile refusals and ordering passed.'
} finally {
    Remove-Item -LiteralPath $registrationTestRoot -Recurse
}
if (-not $source.Contains("NWP_TRIAL_CONTROLLER_PID") -or
    -not $source.Contains("NWP_TRIAL_CONTROLLER_CREATED_FILETIME") -or
    -not $source.Contains('StartTime.ToUniversalTime().ToFileTimeUtc()') -or
    -not $source.Contains("private_trial_lifetime.py")) { throw 'Controller identity or required binding missing.' }
$scratchRoot = Join-Path $workspaceRoot '.scratch\trial-lifetime-implementer'
$null = New-Item -ItemType Directory -Path $scratchRoot -Force
$testRunPath = Join-Path $scratchRoot ('fake-'+[Guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $testRunPath
if (-not $testRunPath.StartsWith($scratchRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Fake test path escaped scratch ownership.' }
function New-FakeDispatch {
    param([bool]$InitiallyExited)
    $fakeDispatch = [pscustomobject]@{ HasExited=$InitiallyExited; WaitCalls=0; StopWasPresent=$false }
    Add-Member -InputObject $fakeDispatch -MemberType ScriptMethod -Name WaitForExit -Value {
        param([int]$WaitMilliseconds)
        $this.WaitCalls++
        $this.StopWasPresent = Test-Path -LiteralPath $script:expectedStopPath -PathType Leaf
        return $this.StopWasPresent -and $WaitMilliseconds -eq 15000
    }
    return $fakeDispatch
}
try {
    $manualPath = Join-Path $testRunPath 'manual.request'
    $timedPath = Join-Path $testRunPath 'timed.request'
    $manualArguments = @(Get-TrialLifetimeArguments -ManualLifetime $true -StopPath $manualPath)
    $timedArguments = @(Get-TrialLifetimeArguments -ManualLifetime $false -StopPath $manualPath)
    if (($manualArguments -join '|') -cne "--until-stopped|$manualPath") { throw 'Manual arguments mismatch.' }
    if (($timedArguments -join '|') -cne '--duration|360') { throw 'Timed arguments mismatch.' }

    $script:expectedStopPath = $timedPath
    $finishedDispatch = New-FakeDispatch -InitiallyExited $true
    Wait-OwnedDispatch -Dispatch $finishedDispatch -Services @() -ManualLifetime $false -StopPath $timedPath
    if (-not $finishedDispatch.StopWasPresent -or $finishedDispatch.WaitCalls -ne 1) { throw 'Timed dispatch waited before stop publication.' }

    [IO.File]::WriteAllText($manualPath,"user requested`n")
    $script:expectedStopPath = $manualPath
    $stoppedDispatch = New-FakeDispatch -InitiallyExited $false
    Wait-OwnedDispatch -Dispatch $stoppedDispatch -Services @() -ManualLifetime $true -StopPath $manualPath
    if (-not $stoppedDispatch.StopWasPresent -or $stoppedDispatch.WaitCalls -ne 1 -or
        [IO.File]::ReadAllText($manualPath) -cne "user requested`n") { throw 'Manual stop was not retained before wait.' }

    $faultPath = Join-Path $testRunPath 'fault.request'
    $script:expectedStopPath = $faultPath
    $faultDispatch = New-FakeDispatch -InitiallyExited $false
    try {
        Wait-OwnedDispatch -Dispatch $faultDispatch -Services @([pscustomobject]@{HasExited=$true}) -ManualLifetime $true -StopPath $faultPath
        throw 'Service fault was accepted.'
    } catch {
        if ($_.Exception.Message -cne 'Service exited during trial.') { throw }
    }
    if (-not (Test-Path -LiteralPath $faultPath -PathType Leaf) -or $faultDispatch.WaitCalls -ne 0) { throw 'Fault failed to publish stop before cleanup.' }
    if (-not $source.Contains('$ManualLifetime -or [DateTime]::UtcNow -lt $dispatchDeadline')) { throw 'Manual wait still has the timed deadline.' }
    Write-Output 'Controller lifetime fake handles: manual, timed and fault cases passed.'
} finally {
    foreach ($ownedName in @('manual.request','timed.request','fault.request')) {
        $ownedPath = Join-Path $testRunPath $ownedName
        if (Test-Path -LiteralPath $ownedPath -PathType Leaf) { Remove-Item -LiteralPath $ownedPath }
    }
    Remove-Item -LiteralPath $testRunPath
}
