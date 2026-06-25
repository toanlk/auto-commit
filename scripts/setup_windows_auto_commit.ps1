param(
    [string]$RepoPath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$TaskName = "GitAutoCommitPush",
    [string]$Branch = "master",
    [string]$Remote = "origin",
    [int]$IntervalSeconds = 60
)

if (-not (Test-Path $RepoPath)) {
    throw "Repository path does not exist: $RepoPath"
}

if ($IntervalSeconds -lt 60) {
    throw "IntervalSeconds must be at least 60 for Windows Task Scheduler."
}

function Resolve-CommandPath {
    param([Parameter(Mandatory = $true)][string]$Name)

    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    return $null
}

$runnerCommand = $null
$runnerPrefixArgs = @()

$poetryCommand = Resolve-CommandPath -Name "poetry"
if ($poetryCommand) {
    $runnerCommand = $poetryCommand
} else {
    $pythonLauncher = Resolve-CommandPath -Name "py"
    if (-not $pythonLauncher) {
        $pythonLauncher = Resolve-CommandPath -Name "python"
    }

    if (-not $pythonLauncher) {
        throw "Python was not found. Install Python 3.11+ first."
    }

    & $pythonLauncher -m pip install poetry
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install Poetry."
    }

    $runnerCommand = $pythonLauncher
    $runnerPrefixArgs = @("-m", "poetry")
}

Push-Location $RepoPath
try {
    & $runnerCommand @runnerPrefixArgs install
    if ($LASTEXITCODE -ne 0) {
        throw "Poetry install failed."
    }
} finally {
    Pop-Location
}

& (Join-Path $PSScriptRoot "register_git_auto_commit_task.ps1") `
    -RepoPath (Resolve-Path $RepoPath).Path `
    -TaskName $TaskName `
    -Branch $Branch `
    -Remote $Remote `
    -IntervalSeconds $IntervalSeconds `
    -RunnerCommand $runnerCommand `
    -RunnerPrefixArgs $runnerPrefixArgs

if ($LASTEXITCODE -ne 0) {
    throw "Scheduled Task registration failed."
}
