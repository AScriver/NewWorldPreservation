[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$manifest = Get-Content -LiteralPath (Join-Path $workspaceRoot 'research\upstreams.json') -Raw | ConvertFrom-Json
$reference = $manifest.firstLight
$referenceRoot = Join-Path $workspaceRoot $reference.directory
$gitExecutable = (Get-Command git -ErrorAction Stop).Source
function Invoke-CheckedGit {
    param([string[]]$ArgumentList)
    $gitOutput = & $gitExecutable @ArgumentList
    if ($LASTEXITCODE -ne 0) { throw "Git command failed with exit code $LASTEXITCODE" }
    return $gitOutput
}
if (-not (Test-Path -LiteralPath $referenceRoot)) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $referenceRoot) | Out-Null
    # The fixture pin identifies the tested Windows checkout bytes (CRLF).
    Invoke-CheckedGit -ArgumentList @('clone', '--config', 'core.autocrlf=true', '--filter=blob:none', '--no-checkout', $reference.url, $referenceRoot) | Out-Null
    Invoke-CheckedGit -ArgumentList @('-C', $referenceRoot, 'sparse-checkout', 'init', '--no-cone') | Out-Null
    Invoke-CheckedGit -ArgumentList @('-C', $referenceRoot, 'checkout', '--detach', $reference.commit) | Out-Null
} else {
    $currentCommit = Invoke-CheckedGit -ArgumentList @('-C', $referenceRoot, 'rev-parse', 'HEAD')
    if ($currentCommit -ne $reference.commit) { throw 'Existing reference is not the pinned commit; it was left unchanged.' }
    $existingChanges = @(Invoke-CheckedGit -ArgumentList @('-C', $referenceRoot, 'status', '--porcelain'))
    if ($existingChanges.Count -ne 0) { throw 'Existing reference contains changes; it was left unchanged.' }
}
$currentRemote = Invoke-CheckedGit -ArgumentList @('-C', $referenceRoot, 'remote', 'get-url', 'origin')
if ($currentRemote -ne $reference.url) { throw 'Reference origin does not match the manifest; it was left unchanged.' }
$sparsePatterns = @(
    '/server/', '/docs/', '/tools/', '/analysis/', '/.github/', '/*.md', '/pyproject.toml', '/.gitignore',
    '/info/nw-login-safe-20260502-153840/messages-redacted.txt',
    '/info/nw-login-safe-20260502-153840/README.md',
    '/info/nw-login-safe-20260502-153840/redaction-report.txt'
)
Invoke-CheckedGit -ArgumentList (@('-C', $referenceRoot, 'sparse-checkout', 'set', '--no-cone') + $sparsePatterns) | Out-Null
$fixturePath = Join-Path $referenceRoot $reference.fixture
$fixtureHash = (Get-FileHash -LiteralPath $fixturePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($fixtureHash -ne $reference.fixtureSha256) { throw 'Redacted reference fixture hash mismatch.' }
$finalCommit = Invoke-CheckedGit -ArgumentList @('-C', $referenceRoot, 'rev-parse', 'HEAD')
$finalChanges = @(Invoke-CheckedGit -ArgumentList @('-C', $referenceRoot, 'status', '--porcelain'))
if ($finalCommit -ne $reference.commit -or $finalChanges.Count -ne 0) { throw 'Final reference identity/cleanliness check failed.' }
[pscustomobject]@{ State = 'REFERENCE_READY'; Commit = $finalCommit; FixtureSha256 = $fixtureHash; AssetsDownloaded = $false; ClientLaunched = $false }
