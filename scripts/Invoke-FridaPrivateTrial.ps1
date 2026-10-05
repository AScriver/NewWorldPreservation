[CmdletBinding()]
param([Parameter(Mandatory)][string]$RunDirectory)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$runPath = [IO.Path]::GetFullPath($RunDirectory)
$privateRoot = Join-Path $workspaceRoot 'private\frida-trials'
if ((Split-Path -Parent $runPath) -ine $privateRoot -or (Split-Path -Leaf $runPath) -notmatch '^run-[A-Za-z0-9_-]+$') { throw 'One direct private/frida-trials/run-* directory required.' }
if ((Get-Item -LiteralPath $runPath).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Run directory must not redirect.' }
trap {
    $startupRecord = @{ schema=1; timestamp_utc=[DateTimeOffset]::UtcNow.ToString('o'); failure_type=$_.Exception.GetType().Name; line=$_.InvocationInfo.ScriptLineNumber; message=$_.Exception.Message; phase='uncaught controller admission/receipt failure; examine containment events for resource state' }
    [IO.File]::WriteAllText((Join-Path $runPath 'controller-admission-error.json'),($startupRecord | ConvertTo-Json),[Text.UTF8Encoding]::new($false))
    exit 1
}
$principal = [Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Windows elevation is required for owned firewall/hosts changes.' }
$manifestPath = Join-Path $runPath 'trial-inputs.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.run_directory -ine $runPath -or $manifest.schema -ne 1) { throw 'Run manifest identity mismatch.' }
$admission = Get-Content -LiteralPath (Join-Path $runPath 'admission.json') -Raw | ConvertFrom-Json
$clientRun = $runPath
if ($admission.PSObject.Properties.Name -contains 'staged_copy_run') {
    if ($admission.staged_copy_run -notmatch '^run-[A-Za-z0-9_-]+$') { throw 'Invalid copy owner run.' }
    $clientRun = Join-Path $privateRoot $admission.staged_copy_run
}
$clientDirectory = Join-Path $clientRun 'client'
if ($manifest.PSObject.Properties.Name -contains 'client_directory') {
    if ($manifest.client_directory -ine $clientDirectory) { throw 'Client copy selection mismatch.' }
}
foreach ($directoryPath in @($clientRun,$clientDirectory,(Join-Path $clientDirectory 'Bin64'))) {
    if ((Get-Item -LiteralPath $directoryPath).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Client copy must not redirect.' }
}
foreach ($binding in $manifest.files) {
    if ((Get-FileHash -LiteralPath $binding.path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $binding.sha256) { throw 'Trial input changed; no admission.' }
}
$validator = 'C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1'
$hostsScript = Join-Path $PSScriptRoot 'Set-ConnectivityHosts.ps1'
$requiredBindings = @($PSCommandPath,$hostsScript,$manifest.frida_dispatch,(Join-Path $runPath 'admission.json'),(Join-Path $runPath 'stage-complete.json'),(Join-Path $clientDirectory 'Bin64\NewWorld.exe'),(Join-Path $PSScriptRoot 'frida_client_trial.py'),(Join-Path $PSScriptRoot 'frida_trial_observer.js'),(Join-Path $PSScriptRoot 'dtls_transport_probe.py'),(Join-Path $workspaceRoot 'research\upstream\first-light\tools\client-hooks\frida_dtls_trust_patch.js'))
if ($manifest.PSObject.Properties.Name -contains 'application_contract') {
    $requiredBindings += Join-Path $PSScriptRoot 'carrier_registration_probe.py'
    $requiredBindings += Join-Path $workspaceRoot 'research\upstream\first-light\server\rep_responder.py'
    $requiredBindings += Join-Path $workspaceRoot 'research\upstream\aeternum-world\Tools\nw_capture\decode_dtls_ledger.py'
    $requiredBindings += Join-Path $workspaceRoot 'requirements-dev.lock'
    if ($manifest.PSObject.Properties.Name -contains 'heartbeat_15d') {
        if ($manifest.heartbeat_15d -isnot [bool]) { throw 'Heartbeat admission must be an explicit boolean.' }
        if ($manifest.heartbeat_15d) {
            $requiredBindings += Join-Path $workspaceRoot 'research\upstream\first-light\server\javelin\heartbeat_15d.py'
        }
    }
    if ($manifest.PSObject.Properties.Name -contains 'self_ident_default') {
        if ($manifest.self_ident_default -isnot [bool]) { throw 'Default actor admission must be an explicit boolean.' }
        if ($manifest.self_ident_default) {
            if ($manifest.PSObject.Properties.Name -notcontains 'heartbeat_15d' -or -not $manifest.heartbeat_15d -or $manifest.PSObject.Properties.Name -notcontains 'registration_server_version' -or $manifest.registration_server_version -cne '[RETAIL].Javelin.1.400.6031.6004151') { throw 'Default actor candidate requires the owned version and heartbeat.' }
            $requiredBindings += Join-Path $PSScriptRoot 'current_self_ident_default.py'
            $requiredBindings += Join-Path $workspaceRoot 'research\evidence\current-self-ident-default-contract.json'
            $mappingPaths = @((Join-Path $clientDirectory 'typeindex.json'),'C:\Program Files (x86)\Steam\steamapps\common\New World\typeindex.json')
            foreach ($mappingPath in $mappingPaths) {
                if ((Get-FileHash -LiteralPath $mappingPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne 'f1e2385f333455a0524ed92ff2a3cb1c66824b1949462d0d12e9f9c06c82be75') { throw 'Owned type mapping changed; no default actor admission.' }
                $requiredBindings += $mappingPath
            }
        }
    }
    if ($manifest.PSObject.Properties.Name -contains 'spawn_point_notification') {
        if ($manifest.spawn_point_notification -isnot [bool]) { throw 'Spawn-point notification admission must be an explicit boolean.' }
        if ($manifest.spawn_point_notification) {
            if ($manifest.PSObject.Properties.Name -notcontains 'self_ident_default' -or -not $manifest.self_ident_default) { throw 'Spawn-point notification requires the current default actor candidate.' }
            $requiredBindings += Join-Path $PSScriptRoot 'current_spawn_point.py'
        }
    }
    if ($manifest.PSObject.Properties.Name -contains 'world_activation') {
        if ($manifest.world_activation -isnot [bool]) { throw 'World activation admission must be an explicit boolean.' }
        if ($manifest.world_activation) {
            if ($manifest.PSObject.Properties.Name -notcontains 'spawn_point_notification' -or -not $manifest.spawn_point_notification) { throw 'World activation requires the current spawn notification.' }
            $requiredBindings += Join-Path $PSScriptRoot 'current_world_activation.py'
            $requiredBindings += Join-Path $workspaceRoot 'research\evidence\current-world-activation-contract.json'
            $mapAssetPath = Join-Path $clientDirectory 'assets\levels\newworld_vitaeeterna\level.pak'
            if ((Get-Item -LiteralPath $mapAssetPath).Attributes -band [IO.FileAttributes]::ReparsePoint -or (Get-FileHash -LiteralPath $mapAssetPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne '2a951aae4be9ce83baebee88d6b64875af249641e51de2f38f35541126ee09b9') { throw 'Owned map asset changed; no world activation admission.' }
            $requiredBindings += $mapAssetPath
        }
    }
    if ($manifest.PSObject.Properties.Name -notcontains 'compression_dependency_files' -or @($manifest.compression_dependency_files).Count -eq 0) { throw 'Pinned compression dependency bindings required.' }
    $compressionPackageRoot = Join-Path $workspaceRoot '.venv\Lib\site-packages'
    foreach ($compressionFile in $manifest.compression_dependency_files) {
        $compressionPath = [IO.Path]::GetFullPath($compressionFile)
        if (-not $compressionPath.StartsWith($compressionPackageRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Compression dependency must belong to the project environment.' }
        $requiredBindings += $compressionPath
    }
    if ($manifest.PSObject.Properties.Name -contains 'registration_server_version') {
        if ($manifest.registration_server_version -cne '[RETAIL].Javelin.1.400.6031.6004151' -or $manifest.PSObject.Properties.Name -notcontains 'registration_server_version_receipt') { throw 'Only the pinned owned-image server-version candidate is admitted.' }
        $versionEvidencePath = [IO.Path]::GetFullPath($manifest.registration_server_version_receipt)
        if (-not $versionEvidencePath.StartsWith($privateRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase) -or (Get-Item -LiteralPath $versionEvidencePath).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Owned-image version evidence must remain private and unredirected.' }
        $versionEvidence = Get-Content -LiteralPath $versionEvidencePath -Raw | ConvertFrom-Json
        $ownedImageHash = (Get-FileHash -LiteralPath (Join-Path $clientDirectory 'Bin64\NewWorld.exe') -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($versionEvidence.mode -cne 'owned-image-static-version-literal-check' -or $versionEvidence.image_sha256 -cne $ownedImageHash -or $versionEvidence.ascii_ids -cnotcontains $manifest.registration_server_version) { throw 'Owned-image server-version literal not established.' }
        $requiredBindings += $versionEvidencePath
    }
}
foreach ($requiredBinding in $requiredBindings) {
    if (@($manifest.files | Where-Object { $_.path -ieq $requiredBinding }).Count -ne 1) { throw 'Mandatory trial input missing or duplicated in bindings.' }
}
& $validator -Path $hostsScript | Out-Null
& $validator -Path $manifest.frida_dispatch | Out-Null
$hostsPath = Join-Path $env:SystemRoot 'System32\drivers\etc\hosts'
$journalPath = Join-Path $runPath 'hosts-journal'
$eventsPath = Join-Path $runPath 'containment-events.jsonl'
if ((Test-Path -LiteralPath $eventsPath) -or (Test-Path -LiteralPath (Join-Path $runPath 'stop.request'))) { throw 'One attempt per run; preserve prior receipt.' }
$ownedChildren = [Collections.Generic.List[Diagnostics.Process]]::new()
$childRecords = [Collections.Generic.List[object]]::new()
$rulePlans = [Collections.Generic.List[object]]::new()
$hostsPrepared = $false
$failure = $null
$cleanupFailure = $null
$runnerLock = $null
$beforeHostsHash = (Get-FileHash -LiteralPath $hostsPath -Algorithm SHA256).Hash.ToLowerInvariant()
$caPemText = [IO.File]::ReadAllText((Join-Path $manifest.certificates 'ca.pem'))
$caDerBytes = [Convert]::FromBase64String(($caPemText -replace '-----BEGIN CERTIFICATE-----|-----END CERTIFICATE-----|\s',''))
$caCertificate = [Security.Cryptography.X509Certificates.X509Certificate2]::new($caDerBytes)
$caThumbprint = $caCertificate.Thumbprint
$beforeRoots = @(Get-ChildItem Cert:\CurrentUser\Root | Where-Object { $_.Thumbprint -ceq $caThumbprint }).Count
if ($beforeRoots -ne 1 -or $caCertificate.NotAfter.ToUniversalTime() -le [DateTime]::UtcNow.AddMinutes(10)) { throw 'Existing retained current-user CA required; no trust store changes in this procedure.' }
function Write-Event {
    param([string]$State,[object]$Details)
    [IO.File]::AppendAllText($eventsPath,(@{ state=$State; timestamp_utc=[DateTimeOffset]::UtcNow.ToString('o'); details=$Details } | ConvertTo-Json -Depth 7 -Compress)+"`n",[Text.UTF8Encoding]::new($false))
}
function Write-NewJson {
    param([string]$FilePath,[object]$Value)
    $recordStream = [IO.File]::Open($FilePath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
    try { $encoded = [Text.UTF8Encoding]::new($false).GetBytes(($Value | ConvertTo-Json -Depth 8)); $recordStream.Write($encoded,0,$encoded.Length); $recordStream.Flush($true) } finally { $recordStream.Dispose() }
}
function Get-OwnedRule {
    param([object]$Plan,[string]$Store='PersistentStore')
    $foundRules = @(Get-NetFirewallRule -PolicyStore $Store -Name $Plan.name -ErrorAction SilentlyContinue)
    if ($foundRules.Count -eq 0) { return $null }
    if ($foundRules.Count -ne 1 -or $foundRules[0].Group -cne $manifest.rule_group -or $foundRules[0].Description -cne $runPath) { throw 'Firewall ownership conflict; preserve rule.' }
    $applications = @($foundRules[0] | Get-NetFirewallApplicationFilter)
    if ($applications.Count -ne 1 -or $applications[0].Program -ine $Plan.program) { throw 'Firewall program conflict; preserve rule.' }
    return $foundRules[0]
}
function Start-OwnedChild {
    param([string]$Name,[string]$Executable,[string[]]$NativeArguments)
    if (Test-Path -LiteralPath (Join-Path $runPath 'stop.request')) { throw 'Admission closed.' }
    $startInfo = [Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName=$Executable
    $startInfo.UseShellExecute=$false
    $startInfo.CreateNoWindow=$true
    $startInfo.WorkingDirectory=$workspaceRoot
    $startInfo.Environment.Remove('SSL_CERT_FILE') | Out-Null
    $startInfo.Environment.Remove('SSL_CERT_DIR') | Out-Null
    if ($Executable -ieq $manifest.protocol_python) { $startInfo.Environment['PYTHONPATH']=$manifest.protocol_packages }
    foreach ($nativeArgument in $NativeArguments) { $startInfo.ArgumentList.Add($nativeArgument) }
    $child = [Diagnostics.Process]::Start($startInfo)
    # Retain the Process (and its kernel handle) before any fallible publication.
    $ownedChildren.Add($child)
    $null = $child.Handle
    $childRecords.Add(@{ name=$Name; process_id=$child.Id; start_time_utc=$child.StartTime.ToUniversalTime().ToString('o'); path=$Executable })
    Write-NewJson -FilePath (Join-Path $runPath ($Name+'-owner.json')) -Value $childRecords[$childRecords.Count-1]
    return $child
}
function Read-InstalledState {
    $stage = Get-Content -LiteralPath (Join-Path $runPath 'stage-complete.json') -Raw | ConvertFrom-Json
    $states = @()
    foreach ($boundFile in @($stage.source,$stage.launcher)) {
        $actualHash = (Get-FileHash -LiteralPath $boundFile.path -Algorithm SHA256).Hash.ToLowerInvariant()
        $states += @{ path=$boundFile.path; sha256=$actualHash; unchanged=($actualHash -ceq $boundFile.sha256) }
    }
    if (@($states | Where-Object { -not $_.unchanged }).Count -ne 0 -or (Test-Path -LiteralPath (Join-Path (Split-Path -Parent $stage.source.path) 'steam_appid.txt'))) { throw 'Installed source changed; preserve evidence.' }
    if ((Get-AuthenticodeSignature -LiteralPath $stage.source.path).Status -ne 'Valid' -or (Get-AuthenticodeSignature -LiteralPath $stage.launcher.path).Status -ne 'Valid') { throw 'Installed signature changed.' }
    $steamManifestText = [IO.File]::ReadAllText($stage.steam_manifest.path)
    $appidMatch = [regex]::Match($steamManifestText,'"appid"\s+"(\d+)"')
    $buildMatch = [regex]::Match($steamManifestText,'"buildid"\s+"(\d+)"')
    if ($appidMatch.Groups[1].Value -cne '1063730' -or $buildMatch.Groups[1].Value -cne '22469132') { throw 'Installed Steam app/build changed; preserve evidence.' }
    $manifestHash = (Get-FileHash -LiteralPath $stage.steam_manifest.path -Algorithm SHA256).Hash.ToLowerInvariant()
    $states += @{ path=$stage.steam_manifest.path; sha256=$manifestHash; unchanged=($manifestHash -ceq $stage.steam_manifest.sha256); appid='1063730'; buildid='22469132'; preserved=$true; change_cause='unknown when metadata differs' }
    return $states
}
try {
    if (@(Get-Process -Name NewWorld,NewWorldLauncher -ErrorAction SilentlyContinue).Count -ne 0) { throw 'Preserve preexisting game/launcher.' }
    if (@(Get-Process -Name Steam -ErrorAction SilentlyContinue).Count -eq 0) { throw 'Existing legitimate Steam session required.' }
    if (@(Get-NetFirewallProfile | Where-Object { $_.Enabled -ne $true }).Count -ne 0) { throw 'Firewall profiles must already be enabled.' }
    if (@(Get-NetTCPConnection -LocalPort 443 -State Listen -ErrorAction SilentlyContinue).Count -ne 0 -or @(Get-NetUDPEndpoint -LocalPort 64003 -ErrorAction SilentlyContinue).Count -ne 0) { throw 'Preserve existing listeners; trial ports unavailable.' }
    $null = Read-InstalledState
    $requiredPrograms = @($manifest.protocol_python,(Get-Command pwsh -ErrorAction Stop).Source,$manifest.frida_python,$manifest.runtime_base_python,(Join-Path $clientDirectory 'Bin64\NewWorld.exe'))
    $requiredPrograms = @($requiredPrograms | Sort-Object -Unique)
    $requiredPrograms += @(Get-ChildItem -LiteralPath $clientDirectory -Recurse -File -Filter '*.exe' | ForEach-Object { $_.FullName })
    foreach ($requiredProgram in $requiredPrograms) {
        if (@($manifest.contained_programs | Where-Object { $_ -ieq $requiredProgram }).Count -ne 1) { throw 'Required trial image absent/duplicated in containment manifest.' }
    }
    Write-Event 'TRIAL_PREFLIGHT_PASSED' @{ retained_root_count=$beforeRoots; hosts_before_sha256=$beforeHostsHash; installed_intact=$true; user_authorization='2026-10-04 direct Frida startup and runtime trust changes'; steam_not_modified=$true }
    $remoteAddresses = @('0.0.0.0-127.0.0.0','127.0.0.2-255.255.255.255','::2-ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
    $programIndex = 0
    foreach ($programPath in $manifest.contained_programs) {
        $programIndex++
        $plan = @{ name=($manifest.rule_group+'-'+$programIndex); program=$programPath }
        if ($null -ne (Get-OwnedRule $plan)) { throw 'Fresh rule names required.' }
        $rulePlans.Add($plan)
    }
    Write-NewJson -FilePath (Join-Path $runPath 'firewall-ownership.json') -Value @{ rule_group=$manifest.rule_group; plans=@($rulePlans); remote_addresses=$remoteAddresses }
    foreach ($plan in $rulePlans) {
        $null = New-NetFirewallRule -Name $plan.name -DisplayName $plan.name -Group $manifest.rule_group -Description $runPath -Direction Outbound -Action Block -Enabled True -Profile Any -Program $plan.program -Protocol Any -RemoteAddress $remoteAddresses -PolicyStore PersistentStore
        $activeRule = Get-OwnedRule -Plan $plan -Store ActiveStore
        if ($null -eq $activeRule -or [string]$activeRule.Enabled -ne 'True' -or [string]$activeRule.Direction -ne 'Outbound' -or [string]$activeRule.Action -ne 'Block' -or [string]$activeRule.Profile -ne 'Any') { throw 'Effective firewall scope readback failed.' }
        $addressFilter = $activeRule | Get-NetFirewallAddressFilter
        $portFilter = $activeRule | Get-NetFirewallPortFilter
        if ([string]$portFilter.Protocol -ne 'Any' -or @(Compare-Object -ReferenceObject $remoteAddresses -DifferenceObject @($addressFilter.RemoteAddress)).Count -ne 0) { throw 'Effective firewall address/protocol readback failed.' }
    }
    Write-Event 'LOOPBACK_CONTAINMENT_CONFIGURED' @{ programs=$manifest.contained_programs; readback='ActiveStore configuration; no packet capture'; external_children='Job Object disallows children; Frida child gating also rejects them'; existing_steam='unmodified licensing broker outside job; no game endpoints intentionally contacted' }
    & $validator -Path $hostsScript -Execute -ArgumentList @('-Action','Prepare','-JournalDirectory',$journalPath,'-EndpointProfile','TokenServices') | Out-Null
    $hostsPrepared=$true
    & $validator -Path $hostsScript -Execute -ArgumentList @('-Action','Apply','-JournalDirectory',$journalPath,'-EndpointProfile','TokenServices') | Out-Null
    foreach ($endpointName in @('d2c74t4zimux3r.cloudfront.net','tokenservice.amazongames.com','prod.newworld.com')) {
        $resolved = @([Net.Dns]::GetHostAddresses($endpointName) | ForEach-Object { $_.ToString() })
        if ($resolved.Count -eq 0 -or @($resolved | Where-Object { $_ -notin @('127.0.0.1','::1') }).Count -ne 0) { throw 'Non-loopback resolver result; no launch.' }
    }
    $pythonExecutable = $manifest.protocol_python
    $commonArguments = @('--certificates',$manifest.certificates,'--descriptor',$manifest.descriptor,'--duration','360','--case','token-loopback','--observe-local-socket-owner')
    $ipv4Child = Start-OwnedChild -Name 'https-v4' -Executable $pythonExecutable -NativeArguments (@((Join-Path $PSScriptRoot 'queue_contract_probe.py'))+$commonArguments+@('--bind','127.0.0.1','--port','443','--log',(Join-Path $runPath 'https-v4.jsonl')))
    $ipv6Child = Start-OwnedChild -Name 'https-v6' -Executable $pythonExecutable -NativeArguments (@((Join-Path $PSScriptRoot 'queue_contract_probe.py'))+$commonArguments+@('--bind','::1','--port','443','--log',(Join-Path $runPath 'https-v6.jsonl')))
    $dtlsArguments = @((Join-Path $PSScriptRoot 'dtls_transport_probe.py'),'--certificates',$manifest.certificates,'--log',(Join-Path $runPath 'dtls.jsonl'),'--port','64003','--duration','360','--chain','full')
    if ($manifest.PSObject.Properties.Name -contains 'application_contract') {
        if ($manifest.application_contract -cne 'carrier-register') { throw 'Unknown application contract; no game admission.' }
        $dtlsArguments[0] = Join-Path $PSScriptRoot 'carrier_registration_probe.py'
        $dtlsArguments += @('--first-light',(Join-Path $workspaceRoot 'research\upstream\first-light'))
        if ($manifest.PSObject.Properties.Name -contains 'registration_server_version') {
            $dtlsArguments += @('--server-version',$manifest.registration_server_version)
        }
        if ($manifest.PSObject.Properties.Name -contains 'heartbeat_15d' -and $manifest.heartbeat_15d) {
            $dtlsArguments += '--heartbeat-15d'
        }
        if ($manifest.PSObject.Properties.Name -contains 'self_ident_default' -and $manifest.self_ident_default) {
            $dtlsArguments += '--self-ident-default'
        }
        if ($manifest.PSObject.Properties.Name -contains 'spawn_point_notification' -and $manifest.spawn_point_notification) {
            $dtlsArguments += '--spawn-point-notification'
        }
        if ($manifest.PSObject.Properties.Name -contains 'world_activation' -and $manifest.world_activation) {
            $dtlsArguments += '--world-activation'
        }
    }
    $dtlsChild = Start-OwnedChild -Name 'dtls' -Executable $pythonExecutable -NativeArguments $dtlsArguments
    $readyDeadline = [DateTime]::UtcNow.AddSeconds(20)
    do {
        if (@($ownedChildren | Where-Object { $_.HasExited }).Count -ne 0) { throw 'Owned service exited before admission.' }
        $tcpListeners = @(Get-NetTCPConnection -LocalPort 443 -State Listen -ErrorAction SilentlyContinue)
        $udpListeners = @(Get-NetUDPEndpoint -LocalPort 64003 -ErrorAction SilentlyContinue)
        $ready = @($tcpListeners | Where-Object { $_.LocalAddress -ceq '127.0.0.1' -and $_.OwningProcess -eq $ipv4Child.Id }).Count -eq 1 -and @($tcpListeners | Where-Object { $_.LocalAddress -ceq '::1' -and $_.OwningProcess -eq $ipv6Child.Id }).Count -eq 1 -and @($udpListeners | Where-Object { $_.LocalAddress -ceq '127.0.0.1' -and $_.OwningProcess -eq $dtlsChild.Id }).Count -eq 1
        if (-not $ready) { Start-Sleep -Milliseconds 200 }
    } while (-not $ready -and [DateTime]::UtcNow -lt $readyDeadline)
    Write-Event 'LISTENER_OWNER_READBACK' @{ tcp=@($tcpListeners | Select-Object LocalAddress,LocalPort,OwningProcess); udp=@($udpListeners | Select-Object LocalAddress,LocalPort,OwningProcess); expected=@{ ipv4=$ipv4Child.Id; ipv6=$ipv6Child.Id; dtls=$dtlsChild.Id }; admitted=$ready }
    if (-not $ready -or $tcpListeners.Count -ne 2 -or $udpListeners.Count -ne 1) { throw 'Exact owned loopback listener readback failed.' }
    Write-Event 'PRIVATE_ENDPOINTS_READY' @{ https_v4=$ipv4Child.Id; https_v6=$ipv6Child.Id; dtls=$dtlsChild.Id; no_application_protocol_invented=$true }
    $fridaChild = Start-OwnedChild -Name 'frida-dispatch' -Executable (Get-Command pwsh -ErrorAction Stop).Source -NativeArguments @('-NoLogo','-NoProfile','-File',$manifest.frida_dispatch)
    $deadline = [DateTime]::UtcNow.AddSeconds(320)
    while (-not $fridaChild.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        if (Test-Path -LiteralPath (Join-Path $runPath 'stop.request')) { break }
        if ($ipv4Child.HasExited -or $ipv6Child.HasExited -or $dtlsChild.HasExited) { throw 'Service exited during trial.' }
        Start-Sleep -Milliseconds 250
    }
    if (-not $fridaChild.WaitForExit(15000)) { throw 'Frida dispatch did not close after bounded lifetime/stop; retain containment.' }
    Write-Event 'FRIDA_DISPATCH_FINISHED' @{ exit_code=$fridaChild.ExitCode; source='owned dispatch exit; hook and DTLS outcomes in separate logs' }
} catch {
    $failure=@{ type=$_.Exception.GetType().Name; line=$_.InvocationInfo.ScriptLineNumber; message=$_.Exception.Message }
    Write-Event 'TRIAL_FAILED' $failure
} finally {
    try {
        [IO.File]::WriteAllText((Join-Path $runPath 'stop.request'),"close admission`n")
        # Give Frida's retained game job owner time to terminate before stopping services.
        $dispatchRecords = @($childRecords | Where-Object { $_.name -ceq 'frida-dispatch' })
        if ($dispatchRecords.Count -eq 1) {
            $dispatchObject = @($ownedChildren | Where-Object { $_.Id -eq $dispatchRecords[0].process_id })[0]
            if (-not $dispatchObject.WaitForExit(15000)) { throw 'Live Frida owner; keep hosts/firewall.' }
        }
        # Python holds this open before admission until its game job has closed.
        # Exclusive sharing also prevents a delayed/orphaned runner entering while
        # containment is released; stop.request remains after this handle closes.
        $runnerLock = [IO.File]::Open((Join-Path $runPath 'runner.lock'),[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
        if (@(Get-Process -Name NewWorld,NewWorldLauncher -ErrorAction SilentlyContinue).Count -ne 0) { throw 'Game remains or appeared outside owned job; retain containment. Do not stop unrelated processes.' }
        foreach ($child in $ownedChildren) {
            if (-not $child.HasExited) { $child.Kill(); if (-not $child.WaitForExit(10000)) { throw 'Owned child remains; retain containment.' } }
        }
        if (@(Get-NetTCPConnection -LocalPort 443 -State Listen -ErrorAction SilentlyContinue).Count -ne 0 -or @(Get-NetUDPEndpoint -LocalPort 64003 -ErrorAction SilentlyContinue).Count -ne 0) { throw 'Listener remains; retain containment.' }
        $installedState = Read-InstalledState
        if ($hostsPrepared) { & $validator -Path $hostsScript -Execute -ArgumentList @('-Action','Restore','-JournalDirectory',$journalPath,'-EndpointProfile','TokenServices') | Out-Null }
        foreach ($plan in $rulePlans) {
            $ownedRule = Get-OwnedRule -Plan $plan
            if ($null -ne $ownedRule) { $ownedRule | Remove-NetFirewallRule -ErrorAction Stop }
            if ($null -ne (Get-OwnedRule -Plan $plan) -or $null -ne (Get-OwnedRule -Plan $plan -Store ActiveStore)) { throw 'Owned firewall rule remains.' }
        }
        $afterHostsHash = (Get-FileHash -LiteralPath $hostsPath -Algorithm SHA256).Hash.ToLowerInvariant()
        $afterRoots = @(Get-ChildItem Cert:\CurrentUser\Root | Where-Object { $_.Thumbprint -ceq $caThumbprint }).Count
        if ($afterRoots -ne $beforeRoots) { throw 'Retained trust state changed externally.' }
        Write-NewJson -FilePath (Join-Path $runPath 'cleanup.json') -Value @{ schema=1; timestamp_utc=[DateTimeOffset]::UtcNow.ToString('o'); game_absent=$true; owned_children_stopped=$true; ports_closed=$true; firewall_rules_absent=$true; hosts_before_sha256=$beforeHostsHash; hosts_after_sha256=$afterHostsHash; hosts_byte_exact=($afterHostsHash -ceq $beforeHostsHash); retained_root_count=$afterRoots; trust_store_modified=$false; installed=$installedState; staged_copy_retained_ignored=$true }
        Write-Event 'TRIAL_CLEANUP_COMPLETE' @{ hosts_byte_exact=($afterHostsHash -ceq $beforeHostsHash); retained_root_count=$afterRoots; installed_binaries_unchanged=$true; steam_manifest_unchanged=$installedState[-1].unchanged; runtime_changes_disposed_by_process_exit=$true }
    } catch {
        $cleanupFailure=@{ type=$_.Exception.GetType().Name; line=$_.InvocationInfo.ScriptLineNumber; message=$_.Exception.Message }
        Write-Event 'CLEANUP_BLOCKED_RETAIN_CONTAINMENT' $cleanupFailure
    }
    Write-NewJson -FilePath (Join-Path $runPath 'controller-result.json') -Value @{ schema=1; timestamp_utc=[DateTimeOffset]::UtcNow.ToString('o'); failure=$failure; cleanup_failure=$cleanupFailure }
    if ($null -ne $runnerLock) { $runnerLock.Dispose() }
}
if ($null -ne $failure -or $null -ne $cleanupFailure) { exit 1 }
