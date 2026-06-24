param(
    [Parameter(Mandatory = $true)]
    [string]$RepoPath,

    [string]$TaskName = "GitAutoCommitPush",
    [string]$Branch = "main",
    [string]$Remote = "origin",
    [int]$IntervalSeconds = 60,
    [string]$RunnerCommand = "poetry",
    [string[]]$RunnerPrefixArgs = @()
)

if (-not (Test-Path $RepoPath)) {
    throw "Repository path does not exist: $RepoPath"
}

if ($IntervalSeconds -lt 60) {
    throw "IntervalSeconds must be at least 60 for Windows Task Scheduler."
}

if ([System.IO.Path]::IsPathRooted($RunnerCommand)) {
    $runnerExecutable = $RunnerCommand
} else {
    $resolvedRunner = Get-Command $RunnerCommand -ErrorAction SilentlyContinue
    if (-not $resolvedRunner) {
        throw "Runner command was not found: $RunnerCommand"
    }

    $runnerExecutable = $resolvedRunner.Source
}

function Quote-TaskArgument {
    param([string]$Value)

    if ($Value -match '[\s"]') {
        return '"' + ($Value -replace '"', '\"') + '"'
    }

    return $Value
}

$taskArguments = @($RunnerPrefixArgs) + @(
    "run",
    "git-auto-commit",
    "--repo",
    $RepoPath,
    "--interval",
    $IntervalSeconds.ToString(),
    "--branch",
    $Branch,
    "--remote",
    $Remote
)

$taskActionArgs = ($taskArguments | ForEach-Object { Quote-TaskArgument $_ }) -join " "
$action = New-ScheduledTaskAction -Execute $runnerExecutable -Argument $taskActionArgs -WorkingDirectory $RepoPath

$startTime = (Get-Date).AddMinutes(1)
$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At $startTime `
    -RepetitionInterval (New-TimeSpan -Seconds $IntervalSeconds) `
    -RepetitionDuration ([TimeSpan]::MaxValue)

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Automatically git add, commit, and push changes for $RepoPath" `
    -Force
