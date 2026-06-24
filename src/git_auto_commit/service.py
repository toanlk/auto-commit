from __future__ import annotations

import logging
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable


class GitAutoCommitError(Exception):
    """Raised when the auto-commit workflow cannot proceed."""


@dataclass(frozen=True)
class AutoCommitConfig:
    repo_path: Path
    interval_seconds: int = 60
    remote: str = "origin"
    branch: str = "main"
    commit_message_template: str = "Auto commit {timestamp}"
    push_when_clean: bool = False

    def render_commit_message(self, now: datetime | None = None) -> str:
        timestamp = (now or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        return self.commit_message_template.format(timestamp=timestamp)


def run_git_command(repo_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )


def ensure_git_repository(repo_path: Path) -> None:
    if not repo_path.exists():
        raise GitAutoCommitError(f"Repository path does not exist: {repo_path}")

    result = run_git_command(repo_path, "rev-parse", "--is-inside-work-tree")
    if result.returncode != 0 or result.stdout.strip() != "true":
        stderr = result.stderr.strip() or "Not a git repository."
        raise GitAutoCommitError(stderr)


def has_staged_changes(repo_path: Path) -> bool:
    result = run_git_command(repo_path, "diff", "--cached", "--quiet")
    return result.returncode == 1


def stage_all_changes(repo_path: Path) -> None:
    result = run_git_command(repo_path, "add", ".")
    if result.returncode != 0:
        stderr = result.stderr.strip() or "git add failed."
        raise GitAutoCommitError(stderr)


def commit_changes(config: AutoCommitConfig, now: datetime | None = None) -> bool:
    if not has_staged_changes(config.repo_path):
        return False

    message = config.render_commit_message(now=now)
    result = run_git_command(config.repo_path, "commit", "-m", message)
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "git commit failed."
        raise GitAutoCommitError(stderr)
    return True


def push_changes(config: AutoCommitConfig) -> None:
    result = run_git_command(config.repo_path, "push", config.remote, config.branch)
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "git push failed."
        raise GitAutoCommitError(stderr)


def run_cycle(
    config: AutoCommitConfig,
    logger: logging.Logger,
    now: datetime | None = None,
) -> bool:
    ensure_git_repository(config.repo_path)
    stage_all_changes(config.repo_path)
    committed = commit_changes(config, now=now)

    if committed:
        logger.info("Created commit and pushing to %s/%s.", config.remote, config.branch)
        push_changes(config)
        return True

    if config.push_when_clean:
        logger.info("No staged changes; pushing anyway to %s/%s.", config.remote, config.branch)
        push_changes(config)
    else:
        logger.info("No changes detected; skipping commit and push.")

    return False


def run_loop(
    config: AutoCommitConfig,
    logger: logging.Logger,
    sleep_fn: Callable[[int], None] = time.sleep,
) -> None:
    while True:
        run_cycle(config, logger)
        logger.info("Sleeping for %s seconds.", config.interval_seconds)
        sleep_fn(config.interval_seconds)
