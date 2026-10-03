Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-AnchorBytesHash {
    param([Parameter(Mandatory)][byte[]]$Image)
    return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($Image)).ToLowerInvariant()
}

function Get-AnchorOutsideHash {
    param([byte[]]$Image, [int]$Offset, [int]$Capacity)
    if ($Offset -lt 0 -or $Capacity -le 0 -or $Offset + $Capacity -gt $Image.Length) { throw 'Invalid interval.' }
    $hasher = [Security.Cryptography.IncrementalHash]::CreateHash([Security.Cryptography.HashAlgorithmName]::SHA256)
    try {
        $hasher.AppendData($Image, 0, $Offset)
        $hasher.AppendData($Image, $Offset + $Capacity, $Image.Length - $Offset - $Capacity)
        return [Convert]::ToHexString($hasher.GetHashAndReset()).ToLowerInvariant()
    } finally { $hasher.Dispose() }
}

function Get-AnchorImageState {
    param([byte[]]$CurrentImage, [byte[]]$StockImage, [byte[]]$CandidateImage, [int]$Offset, [int]$Capacity)
    if ($CurrentImage.Length -ne $StockImage.Length -or $StockImage.Length -ne $CandidateImage.Length) { throw 'Image length changed; refuse overwrite.' }
    $outsideHash = Get-AnchorOutsideHash -Image $StockImage -Offset $Offset -Capacity $Capacity
    if ((Get-AnchorOutsideHash -Image $CandidateImage -Offset $Offset -Capacity $Capacity) -cne $outsideHash) { throw 'Candidate changes bytes outside anchor interval.' }
    if ((Get-AnchorOutsideHash -Image $CurrentImage -Offset $Offset -Capacity $Capacity) -cne $outsideHash) { throw 'Unrecognized outside-interval modification; refuse overwrite.' }
    $currentHash = Get-AnchorBytesHash -Image $CurrentImage
    if ($currentHash -ceq (Get-AnchorBytesHash -Image $StockImage)) { return 'stock' }
    if ($currentHash -ceq (Get-AnchorBytesHash -Image $CandidateImage)) { return 'candidate' }
    for ($byteIndex = $Offset; $byteIndex -lt $Offset + $Capacity; $byteIndex++) {
        if ($CurrentImage[$byteIndex] -ne $StockImage[$byteIndex] -and $CurrentImage[$byteIndex] -ne $CandidateImage[$byteIndex]) { throw 'Unrecognized anchor-region content; refuse overwrite.' }
    }
    return 'interrupted_interval_write'
}

function Write-AnchorTransactionEvent {
    param([string]$Path, [string]$State, [hashtable]$Metadata)
    $record = [ordered]@{ schema=1; timestamp_utc=[DateTimeOffset]::UtcNow.ToString('o'); state=$State; metadata=$Metadata }
    $recordBytes = [Text.UTF8Encoding]::new($false).GetBytes(($record | ConvertTo-Json -Depth 5 -Compress) + "`n")
    $eventStream = [IO.FileStream]::new($Path, [IO.FileMode]::Append, [IO.FileAccess]::Write, [IO.FileShare]::Read)
    try { $eventStream.Write($recordBytes, 0, $recordBytes.Length); $eventStream.Flush($true) } finally { $eventStream.Dispose() }
}

function Set-AnchorImageInterval {
    param(
        [Parameter(Mandatory)][string]$TargetPath,
        [Parameter(Mandatory)][byte[]]$StockImage,
        [Parameter(Mandatory)][byte[]]$CandidateImage,
        [Parameter(Mandatory)][int]$Offset,
        [Parameter(Mandatory)][int]$Capacity,
        [Parameter(Mandatory)][ValidateSet('Apply','Restore')][string]$Action,
        [Parameter(Mandatory)][string]$EventPath
    )
    # Exclusive target handle prevents a concurrent updater/user write between guard and mutation.
    $targetStream = [IO.FileStream]::new($TargetPath, [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    try {
        if ($targetStream.Length -ne $StockImage.Length) { throw 'Target length mismatch.' }
        $currentImage = [byte[]]::new($StockImage.Length)
        $targetStream.ReadExactly($currentImage, 0, $currentImage.Length)
        $imageState = Get-AnchorImageState -CurrentImage $currentImage -StockImage $StockImage -CandidateImage $CandidateImage -Offset $Offset -Capacity $Capacity
        if ($Action -ceq 'Apply' -and $imageState -cne 'stock') { throw 'Apply requires exact stock image; restore interrupted/applied state first.' }
        $desiredImage = if ($Action -ceq 'Apply') { $CandidateImage } else { $StockImage }
        $desiredHash = Get-AnchorBytesHash -Image $desiredImage
        Write-AnchorTransactionEvent -Path $EventPath -State ('ANCHOR_' + $Action.ToUpperInvariant() + '_WRITE_INTENT') -Metadata @{ prior_image_state=$imageState; expected_image_sha256=$desiredHash; offset=$Offset; capacity=$Capacity }
        # ONLY the pinned interval is written, not an executable replacement or signature change.
        $targetStream.Position = $Offset
        $targetStream.Write($desiredImage, $Offset, $Capacity)
        $targetStream.Flush($true)
        $targetStream.Position = 0
        $targetStream.ReadExactly($currentImage, 0, $currentImage.Length)
        if ((Get-AnchorBytesHash -Image $currentImage) -cne $desiredHash) { throw 'Post-write full-image identity mismatch; retain containment.' }
        Write-AnchorTransactionEvent -Path $EventPath -State ('ANCHOR_' + $Action.ToUpperInvariant() + '_HASH_VERIFIED') -Metadata @{ image_sha256=$desiredHash; target_handle_exclusive=$true; process_memory_written=$false }
        return $desiredHash
    } finally { $targetStream.Dispose() }
}

Export-ModuleMember -Function Get-AnchorBytesHash, Get-AnchorOutsideHash, Get-AnchorImageState, Set-AnchorImageInterval, Write-AnchorTransactionEvent
