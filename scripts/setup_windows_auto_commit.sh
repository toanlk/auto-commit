#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

TASK_NAME="${TASK_NAME:-GitAutoCommitPush}"
BRANCH="${BRANCH:-main}"
REMOTE="${REMOTE:-origin}"
INTERVAL_SECONDS="${INTERVAL_SECONDS:-60}"
POETRY_COMMAND="${POETRY_COMMAND:-poetry}"

if [[ "${INTERVAL_SECONDS}" -lt 60 ]]; then
    echo "INTERVAL_SECONDS must be at least 60." >&2
    exit 1
fi

if command -v cygpath >/dev/null 2>&1; then
    WINDOWS_REPO_PATH="$(cygpath -w "${REPO_DIR}")"
elif pwd -W >/dev/null 2>&1; then
    WINDOWS_REPO_PATH="$(cd "${REPO_DIR}" && pwd -W)"
else
    echo "This script must run from Git Bash or an environment with cygpath/pwd -W." >&2
    exit 1
fi

if ! command -v "${POETRY_COMMAND}" >/dev/null 2>&1; then
    if command -v py >/dev/null 2>&1; then
        py -m pip install poetry
    elif command -v python >/dev/null 2>&1; then
        python -m pip install poetry
    else
        echo "Python was not found. Install Python 3 first." >&2
        exit 1
    fi
fi

cd "${REPO_DIR}"
"${POETRY_COMMAND}" install

powershell.exe -ExecutionPolicy Bypass -File "${SCRIPT_DIR}/register_git_auto_commit_task.ps1" \
    -RepoPath "${WINDOWS_REPO_PATH}" \
    -TaskName "${TASK_NAME}" \
    -Branch "${BRANCH}" \
    -Remote "${REMOTE}" \
    -IntervalSeconds "${INTERVAL_SECONDS}" \
    -RunnerCommand "${POETRY_COMMAND}"
