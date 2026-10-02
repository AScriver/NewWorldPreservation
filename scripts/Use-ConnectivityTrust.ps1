[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('Import','Remove')][string]$Action,
    [Parameter(Mandatory)][string]$CertificateDirectory
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$certificatePath = [IO.Path]::GetFullPath($CertificateDirectory)
$privatePrefix = (Join-Path $workspaceRoot 'private') + [IO.Path]::DirectorySeparatorChar
if (-not $certificatePath.StartsWith($privatePrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Only an ignored private probe certificate directory is allowed.' }
$manifest = Get-Content -LiteralPath (Join-Path $certificatePath 'certificate-manifest.json') -Raw | ConvertFrom-Json
$trustReceiptPath = Join-Path $certificatePath 'trust-receipt.json'
$trustEventsPath = Join-Path $certificatePath 'trust-events.jsonl'
$probeCa = [Security.Cryptography.X509Certificates.X509Certificate2]::CreateFromPem([IO.File]::ReadAllText((Join-Path $certificatePath 'ca.pem')))
$caSha256 = $probeCa.GetCertHashString([Security.Cryptography.HashAlgorithmName]::SHA256).ToLowerInvariant()
if ($caSha256 -cne $manifest.ca_sha256 -or $probeCa.Subject -notlike 'CN=NewWorldPreservation local probe *' -or $probeCa.HasPrivateKey) { throw 'Certificate identity mismatch or unexpected private key.' }
if ($probeCa.NotAfter.ToUniversalTime() -gt [DateTime]::UtcNow.AddDays(8) -or $probeCa.NotAfter.ToUniversalTime() -lt [DateTime]::UtcNow) { throw 'Expected a current short-lived probe CA.' }
$rootStore = [Security.Cryptography.X509Certificates.X509Store]::new('Root','CurrentUser')
try {
    $rootStore.Open([Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
    $existing = @($rootStore.Certificates | Where-Object { $_.Thumbprint -ceq $probeCa.Thumbprint })
    if ($Action -eq 'Import') {
        if (Test-Path -LiteralPath $trustReceiptPath) { throw 'Existing trust receipt; do not repeat an import or overwrite ownership evidence.' }
        if ($existing.Count -ne 0) { throw 'Certificate already present; do not claim ownership.' }
        # Journal ownership before changing only this exact CurrentUserRoot entry.
        $trustReceipt = [ordered]@{ schema = 1; timestamp_utc = [DateTime]::UtcNow.ToString('o'); store = 'CurrentUser\Root'; ca_sha256 = $caSha256; thumbprint = $probeCa.Thumbprint; preexisting_count = 0; import_attempted = $true }
        [IO.File]::WriteAllText($trustReceiptPath, ($trustReceipt | ConvertTo-Json), [Text.UTF8Encoding]::new($false))
        $rootStore.Add($probeCa)
    } else {
        $trustReceipt = Get-Content -LiteralPath $trustReceiptPath -Raw | ConvertFrom-Json
        if ($trustReceipt.store -cne 'CurrentUser\Root' -or $trustReceipt.thumbprint -cne $probeCa.Thumbprint -or $trustReceipt.ca_sha256 -cne $caSha256 -or $trustReceipt.preexisting_count -ne 0) { throw 'No matching owned trust receipt.' }
        if ($existing.Count -gt 1) { throw 'Ambiguous certificate entries; refuse bulk removal.' }
        if ($existing.Count -eq 1) { $rootStore.Remove($existing[0]) }
    }
    # Reopen rather than rely on the store's pre-mutation snapshot.
    $rootStore.Close()
    $rootStore.Open([Security.Cryptography.X509Certificates.OpenFlags]::ReadOnly)
    $readbackCount = @($rootStore.Certificates | Where-Object { $_.Thumbprint -ceq $probeCa.Thumbprint }).Count
    $expectedCount = if ($Action -eq 'Import') { 1 } else { 0 }
    if ($readbackCount -ne $expectedCount) { throw 'Exact certificate readback failed.' }
    $record = [ordered]@{ schema = 1; timestamp_utc = [DateTime]::UtcNow.ToString('o'); state = ('PROBE_CA_' + $Action.ToUpperInvariant() + '_COMPLETE'); store = 'CurrentUser\Root'; thumbprint = $probeCa.Thumbprint; ca_sha256 = $caSha256; readback_count = $readbackCount; other_certificates_modified = $false }
    $serialized = $record | ConvertTo-Json -Compress
    [IO.File]::AppendAllText($trustEventsPath, $serialized + "`n", [Text.UTF8Encoding]::new($false))
    $serialized
} finally { $rootStore.Dispose(); $probeCa.Dispose() }
