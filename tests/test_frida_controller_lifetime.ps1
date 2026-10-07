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
foreach ($functionName in @('Publish-StopRequest','Get-TrialLifetimeArguments','Wait-OwnedDispatch')) {
    $selected = @($definitions | Where-Object { $_.Name -ceq $functionName })
    if ($selected.Count -ne 1) { throw 'Expected one isolated lifecycle function.' }
    . ([scriptblock]::Create($selected[0].Extent.Text))
}
$source = [IO.File]::ReadAllText($controllerPath)
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
