Set-StrictMode -Version Latest

function Get-OfficialProcessIdentity {
    [CmdletBinding()]
    param([object]$Process, [string]$ExpectedPath, [datetime]$NotBeforeUtc)
    try {
        $candidatePath = $Process.Path
        $candidateStartUtc = $Process.StartTime.ToUniversalTime()
        if (-not $candidatePath) { return @{ state = 'identity_unavailable' } }
        if ($candidatePath -ine $ExpectedPath) { return @{ state = 'different_image' } }
        if ($candidateStartUtc -lt $NotBeforeUtc) { return @{ state = 'preexisting_process' } }
        return @{ state = 'matched'; process_id = [int]$Process.Id;
            start_utc = $candidateStartUtc.ToString('o'); start_ticks = $candidateStartUtc.Ticks }
    } catch { return @{ state = 'identity_unavailable' } }
}

function Test-OfficialPublicProcessCorrelation {
    [CmdletBinding()]
    param([object]$Metadata,[int]$ExpectedProcessId,[datetime]$ExpectedStartUtc)
    if ($null -eq $Metadata) { return $false }
    try {
        return ($Metadata.Name -ieq 'NewWorld.exe' -and [int]$Metadata.ProcessId -eq $ExpectedProcessId -and
            $Metadata.CreationDate.ToUniversalTime().Ticks -eq $ExpectedStartUtc.Ticks)
    } catch { return $false }
}

function ConvertTo-OfficialSocketMetadata {
    [CmdletBinding()]
    param([object[]]$Tcp = @(), [object[]]$Udp = @())
    $outputRecords = @()
    foreach ($connection in $Tcp) {
        $stateName = [string]$connection.State
        if ($stateName -notin @('SynSent','SynReceived','Established','FinWait1','FinWait2','CloseWait','Closing','LastAck','TimeWait','Closed','DeleteTcb')) { continue }
        $remoteIp = $null
        if (-not [Net.IPAddress]::TryParse([string]$connection.RemoteAddress, [ref]$remoteIp)) { continue }
        if ([int]$connection.RemotePort -lt 1 -or [int]$connection.RemotePort -gt 65535) { continue }
        $outputRecords += [ordered]@{ protocol = 'tcp'; local_port = [int]$connection.LocalPort;
            remote_address_family = [string]$remoteIp.AddressFamily; remote_address_retained = $false;
            remote_port = [int]$connection.RemotePort; socket_state = $stateName;
            classification = 'owned_socket_metadata'; interpretation = 'sampled_socket_not_tls_auth_schema_or_actor_proof' }
    }
    foreach ($endpoint in $Udp) {
        if ([int]$endpoint.LocalPort -lt 1 -or [int]$endpoint.LocalPort -gt 65535) { continue }
        $outputRecords += [ordered]@{ protocol = 'udp'; local_port = [int]$endpoint.LocalPort;
            classification = 'owned_local_udp_binding'; remote_endpoint = 'unavailable';
            interpretation = 'local_binding_not_datagram_dtls_carrier_or_actor_proof' }
    }
    return $outputRecords
}

function Test-OfficialObservationEnvironment {
    [CmdletBinding()]
    param([string]$HostsPath = "$env:WINDIR\System32\drivers\etc\hosts")
    $activeHostsLines = @(Get-Content -LiteralPath $HostsPath | Where-Object { $_ -notmatch '^\s*#' })
    $gameMappings = @($activeHostsLines | Where-Object { $_ -match '(?i)cloudfront\.net|amazonaws\.com|amazongames\.com|newworld' })
    $disallowedEnvironment = @('SSLKEYLOGFILE','HTTP_PROXY','HTTPS_PROXY','ALL_PROXY')
    $presentCount = 0
    foreach ($environmentName in $disallowedEnvironment) {
        if ([Environment]::GetEnvironmentVariable($environmentName, 'Process')) { $presentCount++ }
    }
    return @{ hosts_sha256 = (Get-FileHash -LiteralPath $HostsPath -Algorithm SHA256).Hash.ToLowerInvariant();
        game_hosts_mapping_count = $gameMappings.Count; disallowed_environment_count = $presentCount;
        ready = ($gameMappings.Count -eq 0 -and $presentCount -eq 0) }
}

Export-ModuleMember -Function Get-OfficialProcessIdentity,Test-OfficialPublicProcessCorrelation,ConvertTo-OfficialSocketMetadata,Test-OfficialObservationEnvironment
