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

$toolRepoPath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

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
    "--once",
    "--branch",
    $Branch,
    "--remote",
    $Remote
)

$taskActionArgs = ($taskArguments | ForEach-Object { Quote-TaskArgument $_ }) -join " "
$intervalIso = "PT{0}S" -f $IntervalSeconds
$taskDescription = "Automatically git add, commit, and push changes for $RepoPath"

function Escape-XmlValue {
    param([string]$Value)

    return [System.Security.SecurityElement]::Escape($Value)
}

$taskXml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>$(Escape-XmlValue $taskDescription)</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
      <Repetition>
        <Interval>$intervalIso</Interval>
        <Duration>P9999D</Duration>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
    </BootTrigger>
  </Triggers>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>$(Escape-XmlValue $runnerExecutable)</Command>
      <Arguments>$(Escape-XmlValue $taskActionArgs)</Arguments>
      <WorkingDirectory>$(Escape-XmlValue $toolRepoPath)</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

Register-ScheduledTask `
    -TaskName $TaskName `
    -Xml $taskXml `
    -Force
