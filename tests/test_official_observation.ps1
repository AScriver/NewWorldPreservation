[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
Import-Module (Join-Path $workspaceRoot 'scripts\OfficialObservation.psm1') -Force
function Assert-ObservationTest { param([bool]$Condition,[string]$Name) if (-not $Condition) { throw $Name } }
$baseTime = [datetime]::Parse('2026-10-06T19:00:00Z').ToUniversalTime()
$fixtureProcess = [pscustomobject]@{ Id = 123; Path = 'C:\Synthetic\NewWorld.exe'; StartTime = $baseTime.AddSeconds(1) }
$matched = Get-OfficialProcessIdentity -Process $fixtureProcess -ExpectedPath 'C:\Synthetic\NewWorld.exe' -NotBeforeUtc $baseTime
Assert-ObservationTest ($matched.state -eq 'matched' -and $matched.process_id -eq 123) 'Exact image/start must match.'
$wrongImage = Get-OfficialProcessIdentity -Process $fixtureProcess -ExpectedPath 'C:\Different\NewWorld.exe' -NotBeforeUtc $baseTime
Assert-ObservationTest ($wrongImage.state -eq 'different_image') 'Same name is not target identity.'
$stale = Get-OfficialProcessIdentity -Process $fixtureProcess -ExpectedPath $fixtureProcess.Path -NotBeforeUtc $baseTime.AddSeconds(2)
Assert-ObservationTest ($stale.state -eq 'preexisting_process') 'Cold collection must reject preexisting process.'
$inaccessible = Get-OfficialProcessIdentity -Process ([pscustomobject]@{ Path = $null }) -ExpectedPath $fixtureProcess.Path -NotBeforeUtc $baseTime
Assert-ObservationTest ($inaccessible.state -eq 'identity_unavailable') 'Denied metadata must be reported.'
$publicFixture = [pscustomobject]@{ ProcessId=123; Name='NewWorld.exe'; CreationDate=$baseTime }
Assert-ObservationTest (Test-OfficialPublicProcessCorrelation -Metadata $publicFixture -ExpectedProcessId 123 -ExpectedStartUtc $baseTime) 'Public PID/name/creation time correlation must match.'
Assert-ObservationTest (-not (Test-OfficialPublicProcessCorrelation -Metadata $publicFixture -ExpectedProcessId 124 -ExpectedStartUtc $baseTime)) 'Different PID must refuse.'
Assert-ObservationTest (-not (Test-OfficialPublicProcessCorrelation -Metadata $publicFixture -ExpectedProcessId 123 -ExpectedStartUtc $baseTime.AddSeconds(1))) 'Reused PID must refuse.'
$tcpFixtures = @(
    [pscustomobject]@{ LocalPort=1234; RemoteAddress='203.0.113.1'; RemotePort=443; State='Established'; Secret='MUST_NOT_EXPORT' },
    [pscustomobject]@{ LocalPort=1235; RemoteAddress='1234@secret'; RemotePort=443; State='Established' },
    [pscustomobject]@{ LocalPort=1236; RemoteAddress='203.0.113.2'; RemotePort=443; State='MUST_NOT_EXPORT' }
)
$udpFixtures = @([pscustomobject]@{ LocalPort=1237; LocalAddress='PRIVATE_OWN_IP'; Secret='MUST_NOT_EXPORT' })
$records = @(ConvertTo-OfficialSocketMetadata -Tcp $tcpFixtures -Udp $udpFixtures)
Assert-ObservationTest ($records.Count -eq 2) 'Only valid TCP and local UDP metadata must survive.'
$serialized = $records | ConvertTo-Json -Depth 8
Assert-ObservationTest ($serialized -notmatch 'MUST_NOT_EXPORT|PRIVATE_OWN_IP|203\.0\.113\.1') 'Unexpected fields/identifiers must not serialize.'
Assert-ObservationTest ($records[1].remote_endpoint -eq 'unavailable') 'UDP binding is not remote/DTLS proof.'
$scratchDirectory = Join-Path $workspaceRoot ('.scratch\official-mock-' + [guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $scratchDirectory
$hostsFixture = Join-Path $scratchDirectory 'hosts-fixture.txt'
try {
    [IO.File]::WriteAllText($hostsFixture, '# ignored amazongames.com' + [Environment]::NewLine + '127.0.0.1 example.amazongames.com')
    $guard = Test-OfficialObservationEnvironment -HostsPath $hostsFixture
    Assert-ObservationTest (-not $guard.ready -and $guard.game_hosts_mapping_count -eq 1) 'Existing game redirect must refuse ordinary observation.'
    Assert-ObservationTest (-not (($guard | ConvertTo-Json) -match 'example.amazongames.com')) 'Routing receipt must not copy hosts lines.'
    Write-Output 'Official observation synthetic process/socket/privacy/routing checks passed (12 assertions).'
} finally {
    Remove-Item -LiteralPath $hostsFixture -Force
    Remove-Item -LiteralPath $scratchDirectory
}
