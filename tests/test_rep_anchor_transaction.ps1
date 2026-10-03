Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
Import-Module (Join-Path $workspaceRoot 'scripts\RepAnchorImageTransaction.psm1') -Force
$fixtureDirectory = Join-Path (Join-Path $workspaceRoot '.scratch\rep-anchor-trial') ('fixtures-' + [guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $fixtureDirectory
$stockImage = [byte[]](0..127)
$candidateImage = [byte[]]$stockImage.Clone()
for ($byteIndex = 32; $byteIndex -lt 48; $byteIndex++) { $candidateImage[$byteIndex] = 200 + $byteIndex - 32 }
$targetPath = Join-Path $fixtureDirectory 'synthetic-image.bin'
$eventPath = Join-Path $fixtureDirectory 'events.jsonl'
$checkCount = 0
function Assert-Condition {
    param([bool]$Condition, [string]$Description)
    if (-not $Condition) { throw $Description }
    $script:checkCount++
}
function Assert-Rejected {
    param([scriptblock]$Operation, [string]$Description)
    $didReject = $false
    try { & $Operation | Out-Null } catch { $didReject = $true }
    Assert-Condition -Condition $didReject -Description $Description
}
Assert-Condition -Condition ((Get-AnchorImageState -CurrentImage $stockImage -StockImage $stockImage -CandidateImage $candidateImage -Offset 32 -Capacity 16) -ceq 'stock') -Description 'Stock classification'
Assert-Condition -Condition ((Get-AnchorImageState -CurrentImage $candidateImage -StockImage $stockImage -CandidateImage $candidateImage -Offset 32 -Capacity 16) -ceq 'candidate') -Description 'Candidate classification'
$interruptedImage = [byte[]]$stockImage.Clone()
[Array]::Copy($candidateImage,32,$interruptedImage,32,7)
Assert-Condition -Condition ((Get-AnchorImageState -CurrentImage $interruptedImage -StockImage $stockImage -CandidateImage $candidateImage -Offset 32 -Capacity 16) -ceq 'interrupted_interval_write') -Description 'Partial interval classification'
$unrelatedImage = [byte[]]$candidateImage.Clone(); $unrelatedImage[0] = 255
Assert-Rejected -Operation { Get-AnchorImageState -CurrentImage $unrelatedImage -StockImage $stockImage -CandidateImage $candidateImage -Offset 32 -Capacity 16 } -Description 'Unrelated updater outside interval must be protected'
$unrecognizedImage = [byte[]]$candidateImage.Clone(); $unrecognizedImage[33] = 5
Assert-Rejected -Operation { Get-AnchorImageState -CurrentImage $unrecognizedImage -StockImage $stockImage -CandidateImage $candidateImage -Offset 32 -Capacity 16 } -Description 'Unknown inside interval must be protected'
Assert-Rejected -Operation { Get-AnchorImageState -CurrentImage $stockImage -StockImage $stockImage -CandidateImage $unrelatedImage -Offset 32 -Capacity 16 } -Description 'Candidate outside-interval mutation rejected'
[IO.File]::WriteAllBytes($targetPath,$stockImage)
$appliedHash = Set-AnchorImageInterval -TargetPath $targetPath -StockImage $stockImage -CandidateImage $candidateImage -Offset 32 -Capacity 16 -Action Apply -EventPath $eventPath
Assert-Condition -Condition ($appliedHash -ceq (Get-AnchorBytesHash -Image $candidateImage)) -Description 'Apply hash'
Assert-Rejected -Operation { Set-AnchorImageInterval -TargetPath $targetPath -StockImage $stockImage -CandidateImage $candidateImage -Offset 32 -Capacity 16 -Action Apply -EventPath $eventPath } -Description 'Apply against nonstock rejected'
$restoredHash = Set-AnchorImageInterval -TargetPath $targetPath -StockImage $stockImage -CandidateImage $candidateImage -Offset 32 -Capacity 16 -Action Restore -EventPath $eventPath
Assert-Condition -Condition ($restoredHash -ceq (Get-AnchorBytesHash -Image $stockImage)) -Description 'Restore hash'
[IO.File]::WriteAllBytes($targetPath,$interruptedImage)
$partialRestore = Set-AnchorImageInterval -TargetPath $targetPath -StockImage $stockImage -CandidateImage $candidateImage -Offset 32 -Capacity 16 -Action Restore -EventPath $eventPath
Assert-Condition -Condition ($partialRestore -ceq (Get-AnchorBytesHash -Image $stockImage)) -Description 'Partial interval recovery'
[IO.File]::WriteAllBytes($targetPath,$unrelatedImage)
Assert-Rejected -Operation { Set-AnchorImageInterval -TargetPath $targetPath -StockImage $stockImage -CandidateImage $candidateImage -Offset 32 -Capacity 16 -Action Restore -EventPath $eventPath } -Description 'Unexpected updater must not be overwritten'
Assert-Condition -Condition ((Get-AnchorBytesHash -Image ([IO.File]::ReadAllBytes($targetPath))) -ceq (Get-AnchorBytesHash -Image $unrelatedImage)) -Description 'Refusal preserves unexpected image'
[IO.File]::WriteAllBytes($targetPath,$stockImage)
$lockedStream = [IO.FileStream]::new($targetPath,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::None)
try { Assert-Rejected -Operation { Set-AnchorImageInterval -TargetPath $targetPath -StockImage $stockImage -CandidateImage $candidateImage -Offset 32 -Capacity 16 -Action Apply -EventPath $eventPath } -Description 'Existing exclusive lock must block transaction' } finally { $lockedStream.Dispose() }
$events = @(Get-Content -LiteralPath $eventPath | ConvertFrom-Json -DateKind String)
Assert-Condition -Condition ($events.Count -eq 6 -and @($events | Where-Object { -not $_.timestamp_utc }).Count -eq 0) -Description 'Intent/result state logs'
$resultJson = [ordered]@{ timestamp_utc=[DateTimeOffset]::UtcNow.ToString('o'); checks=$checkCount; fixture_directory=$fixtureDirectory; actual_client_mutated=$false; live_resources_touched=$false } | ConvertTo-Json
[IO.File]::WriteAllText((Join-Path $fixtureDirectory 'result.json'),$resultJson,[Text.UTF8Encoding]::new($false))
$resultJson
