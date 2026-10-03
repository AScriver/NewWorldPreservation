# Own-client, exact-build certificate-data trial only. Not a validation/EAC bypass.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('Apply','Restore')][string]$Action,
    [Parameter(Mandatory)][string]$CandidateJournal,
    [Parameter(Mandatory)][string]$RunDirectory
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'RepAnchorImageTransaction.psm1') -Force
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$privatePrefix = (Join-Path $workspaceRoot 'private\connectivity') + [IO.Path]::DirectorySeparatorChar
$journalPath = [IO.Path]::GetFullPath($CandidateJournal)
$runPath = [IO.Path]::GetFullPath($RunDirectory)
if (-not $journalPath.StartsWith($privatePrefix,[StringComparison]::OrdinalIgnoreCase) -or -not $runPath.StartsWith($privatePrefix,[StringComparison]::OrdinalIgnoreCase)) { throw 'Ignored owned candidate and run directories required.' }
if (-not (Test-Path -LiteralPath $runPath -PathType Container)) { throw 'Existing owned run required.' }
$journal = Get-Content -LiteralPath $journalPath -Raw | ConvertFrom-Json -DateKind String
$clientPath = 'C:\Program Files (x86)\Steam\steamapps\common\New World\Bin64\NewWorld.exe'
$stockHash = '8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e'
$candidateHash = 'dff94b76032fdd528c936e9f9313dea1736ad5432d32cb068933b8a3d5ed8096'
$anchorHash = '2c9f403d47318a0c1f801d5bc5ea11a33cef83612221248a0df8c5ca3e34bbeb'
if ($journal.state -cne 'prepared_offline_unapplied' -or $journal.source_path -ine $clientPath -or $journal.source_sha256 -cne $stockHash -or $journal.candidate_sha256 -cne $candidateHash -or $journal.image_size -ne 179204176 -or $journal.region_offset -ne 140045408 -or $journal.region_capacity -ne 1350 -or $journal.anchor_der_sha256 -cne $anchorHash -or $journal.anchor_pem_sha256 -cne '30bba23f8800ddad69f199c96746aec5eed7e5ce405e130206c630d516573b19') { throw 'Pinned candidate policy mismatch.' }
$candidateDirectory = Split-Path -Parent $journalPath
foreach ($artifactPath in @($journal.backup_path,$journal.candidate_path)) {
    if ((Split-Path -Parent ([IO.Path]::GetFullPath($artifactPath))) -ine $candidateDirectory -or -not (Test-Path -LiteralPath $artifactPath -PathType Leaf)) { throw 'Candidate artifact ownership conflict.' }
}
$stockImage = [IO.File]::ReadAllBytes($journal.backup_path)
$candidateImage = [IO.File]::ReadAllBytes($journal.candidate_path)
if ($stockImage.Length -ne 179204176 -or $candidateImage.Length -ne 179204176 -or (Get-AnchorBytesHash -Image $stockImage) -cne $stockHash -or (Get-AnchorBytesHash -Image $candidateImage) -cne $candidateHash) { throw 'Verified backup/candidate required.' }
if (@(Get-Process -Name NewWorld -ErrorAction SilentlyContinue).Count -ne 0) { throw 'No file writes while a game is running; keep containment.' }
$eventPath = Join-Path $runPath 'anchor-image-transaction.jsonl'
if ($Action -ceq 'Apply') {
    $retained = Get-Content -LiteralPath (Join-Path $workspaceRoot 'private\connectivity\retained-test-ca.json') -Raw | ConvertFrom-Json -DateKind String
    $caFile = Join-Path $retained.certificate_directory 'ca.pem'
    if ((Get-FileHash -LiteralPath $caFile -Algorithm SHA256).Hash.ToLowerInvariant() -cne $journal.anchor_pem_sha256) { throw 'Retained CA PEM changed.' }
    $approvedCa = [Security.Cryptography.X509Certificates.X509Certificate2]::CreateFromPem([IO.File]::ReadAllText($caFile))
    try {
        if ($approvedCa.GetCertHashString([Security.Cryptography.HashAlgorithmName]::SHA256).ToLowerInvariant() -cne $anchorHash -or $approvedCa.NotBefore.ToUniversalTime() -gt [DateTime]::UtcNow -or $approvedCa.NotAfter.ToUniversalTime() -lt [DateTime]::UtcNow -or @(Get-ChildItem Cert:\CurrentUser\Root | Where-Object Thumbprint -ceq $approvedCa.Thumbprint).Count -ne 1) { throw 'Same approved, active retained CA required.' }
    } finally { $approvedCa.Dispose() }
    $windowRows = @(Get-Content -LiteralPath (Join-Path $runPath 'trial-window.jsonl') | ConvertFrom-Json -DateKind String)
    if ($windowRows.Count -ne 2 -or $windowRows[-1].state -cne 'BOOTSTRAP_TRIAL_READY' -or ([DateTimeOffset]::UtcNow - [DateTimeOffset]::Parse($windowRows[-1].timestamp_utc)).TotalSeconds -gt 60) { throw 'Fresh ready containment required before mutation.' }
    $ownership = Get-Content -LiteralPath (Join-Path $runPath 'firewall-ownership.json') -Raw | ConvertFrom-Json -DateKind String
    $rules = @(Get-NetFirewallRule -PolicyStore ActiveStore -Name $ownership.rule_name -ErrorAction Stop)
    if ($rules.Count -ne 1 -or $rules[0].Group -cne $ownership.group -or $rules[0].Description -cne $runPath -or [string]$rules[0].Enabled -cne 'True' -or [string]$rules[0].Direction -cne 'Outbound' -or [string]$rules[0].Action -cne 'Block' -or [string]$rules[0].Profile -cne 'Any') { throw 'Effective rule ownership/scope mismatch.' }
    $applications = @($rules[0] | Get-NetFirewallApplicationFilter)
    $addresses = @($rules[0] | Get-NetFirewallAddressFilter)
    $ports = @($rules[0] | Get-NetFirewallPortFilter)
    $expectedAddresses = @('0.0.0.0-127.0.0.0','127.0.0.2-255.255.255.255','::2-ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
    if ($applications.Count -ne 1 -or $applications[0].Program -ine $clientPath -or $addresses.Count -ne 1 -or $ports.Count -ne 1 -or [string]$ports[0].Protocol -cne 'Any' -or @(Compare-Object $expectedAddresses @($addresses[0].RemoteAddress)).Count -ne 0 -or @(Get-NetFirewallProfile | Where-Object { $_.Enabled -ne $true }).Count -ne 0) { throw 'Effective non-loopback IPv4/IPv6 game guard required.' }
    foreach ($endpointName in @('d2c74t4zimux3r.cloudfront.net','tokenservice.amazongames.com','prod.newworld.com')) {
        $resolvedAddresses = @([Net.Dns]::GetHostAddresses($endpointName) | ForEach-Object { $_.ToString() })
        if ($resolvedAddresses.Count -eq 0 -or @($resolvedAddresses | Where-Object { $_ -notin @('127.0.0.1','::1') }).Count -ne 0) { throw 'Owned routing changed; no mutation.' }
    }
    $tcpListeners = @(Get-NetTCPConnection -LocalPort 443 -State Listen -ErrorAction Stop)
    $udpListeners = @(Get-NetUDPEndpoint -LocalPort 64003 -ErrorAction Stop)
    if ($tcpListeners.Count -ne 2 -or @($tcpListeners | Where-Object { $_.LocalAddress -notin @('127.0.0.1','::1') }).Count -ne 0 -or $udpListeners.Count -ne 1 -or $udpListeners[0].LocalAddress -cne '127.0.0.1') { throw 'Loopback-only responders required.' }
    $udpOwner = Get-Content -LiteralPath (Join-Path $runPath 'dtls-ownership.json') -Raw | ConvertFrom-Json -DateKind String
    if ($udpListeners[0].OwningProcess -ne $udpOwner.process_id -or (Get-Process -Id $udpOwner.process_id).StartTime.ToUniversalTime().ToString('o') -cne $udpOwner.start_time_utc) { throw 'Owned UDP responder mismatch.' }
    $signatureBefore = Get-AuthenticodeSignature -LiteralPath $clientPath
    if ([string]$signatureBefore.Status -cne 'Valid') { throw 'Original client signature is not valid.' }
    Write-AnchorTransactionEvent -Path $eventPath -State 'ANCHOR_APPLY_PRECONDITIONS_VERIFIED' -Metadata @{ journal_sha256=(Get-FileHash -LiteralPath $journalPath -Algorithm SHA256).Hash.ToLowerInvariant(); original_signature_status=[string]$signatureBefore.Status; game_absent=$true; effective_nonloopback_guard=$true; ca_reused=$true }
}
$resultHash = Set-AnchorImageInterval -TargetPath $clientPath -StockImage $stockImage -CandidateImage $candidateImage -Offset 140045408 -Capacity 1350 -Action $Action -EventPath $eventPath
$signatureAfter = Get-AuthenticodeSignature -LiteralPath $clientPath
Write-AnchorTransactionEvent -Path $eventPath -State ('ANCHOR_' + $Action.ToUpperInvariant() + '_SIGNATURE_READBACK') -Metadata @{ image_sha256=$resultHash; authenticode_status=[string]$signatureAfter.Status; launcher_or_eac_modified=$false; memory_written=$false }
if ($Action -ceq 'Restore' -and [string]$signatureAfter.Status -cne 'Valid') { throw 'Stock signature restoration unconfirmed; retain containment.' }
if ($Action -ceq 'Apply' -and [string]$signatureAfter.Status -ceq 'Valid') { throw 'Unexpected signature-valid candidate; do not attribute a trial.' }
[ordered]@{ timestamp_utc=[DateTimeOffset]::UtcNow.ToString('o'); state=('ANCHOR_' + $Action.ToUpperInvariant() + '_COMPLETE'); image_sha256=$resultHash; authenticode_status=[string]$signatureAfter.Status; interval_only=$true } | ConvertTo-Json
