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
    branch: str | None = None
    commit_message_template: str = "Auto commit {timestamp}"
    push_when_clean: bool = False
    filelist_limit: int = 5

    def render_commit_message(
        self,
        now: datetime | None = None,
        summary: "DiffSummary | None" = None,
    ) -> str:
        timestamp = (now or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        summary = summary or DiffSummary()
        return self.commit_message_template.format(
            timestamp=timestamp,
            files=summary.files_label,
            stats=summary.stats_label,
            summary=summary.combined_label,
            filelist=summary.filelist_label(self.filelist_limit),
        )


@dataclass(frozen=True)
class DiffSummary:
    file_count: int = 0
    insertions: int = 0
    deletions: int = 0
    filenames: tuple[str, ...] = ()

    @property
    def files_label(self) -> str:
        if self.file_count == 0:
            return "no files"
        noun = "file" if self.file_count == 1 else "files"
        return f"{self.file_count} {noun}"

    @property
    def stats_label(self) -> str:
        return f"+{self.insertions} -{self.deletions}"

    @property
    def combined_label(self) -> str:
        if self.file_count == 0:
            return "no changes"
        return f"{self.files_label} ({self.stats_label})"

    def filelist_label(self, limit: int) -> str:
        if not self.filenames:
            return ""
        if limit <= 0 or len(self.filenames) <= limit:
            return ", ".join(self.filenames)
        shown = ", ".join(self.filenames[:limit])
        return f"{shown} (+{len(self.filenames) - limit} more)"


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


def summarize_staged_changes(repo_path: Path) -> DiffSummary:
    names = run_git_command(repo_path, "diff", "--cached", "--name-only")
    filenames: tuple[str, ...] = ()
    if names.returncode == 0:
        filenames = tuple(line for line in names.stdout.splitlines() if line.strip())

    shortstat = run_git_command(repo_path, "diff", "--cached", "--shortstat")
    insertions = 0
    deletions = 0
    file_count = len(filenames)
    if shortstat.returncode == 0:
        text = shortstat.stdout.strip()
        for token, target in (("insertion", "ins"), ("deletion", "del")):
            for part in text.split(","):
                part = part.strip()
                if token in part:
                    number = part.split()[0]
                    if number.isdigit():
                        if target == "ins":
                            insertions = int(number)
                        else:
                            deletions = int(number)

    return DiffSummary(
        file_count=file_count,
        insertions=insertions,
        deletions=deletions,
        filenames=filenames,
    )


def commit_changes(config: AutoCommitConfig, now: datetime | None = None) -> bool:
    if not has_staged_changes(config.repo_path):
        return False

    summary = summarize_staged_changes(config.repo_path)
    message = config.render_commit_message(now=now, summary=summary)
    result = run_git_command(config.repo_path, "commit", "-m", message)
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "git commit failed."
        raise GitAutoCommitError(stderr)
    return True


def get_current_branch(repo_path: Path) -> str:
    result = run_git_command(repo_path, "branch", "--show-current")
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "Could not determine current branch."
        raise GitAutoCommitError(stderr)

    branch = result.stdout.strip()
    if not branch:
        raise GitAutoCommitError("Could not determine current branch. Use --branch when in detached HEAD.")
    return branch


def resolve_push_branch(config: AutoCommitConfig) -> str:
    return config.branch or get_current_branch(config.repo_path)


def pull_changes(config: AutoCommitConfig, branch: str | None = None) -> None:
    branch = branch or resolve_push_branch(config)
    result = run_git_command(
        config.repo_path, "pull", "--rebase", config.remote, branch,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "git pull failed."
        raise GitAutoCommitError(stderr)


def abort_rebase(repo_path: Path) -> None:
    run_git_command(repo_path, "rebase", "--abort")


def push_changes(config: AutoCommitConfig, branch: str | None = None) -> None:
    branch = branch or resolve_push_branch(config)
    result = run_git_command(config.repo_path, "push", config.remote, branch)
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "git push failed."
        raise GitAutoCommitError(stderr)


def run_cycle(
    config: AutoCommitConfig,
    logger: logging.Logger,
    now: datetime | None = None,
) -> bool:
    ensure_git_repository(config.repo_path)
    branch = resolve_push_branch(config)

    stage_all_changes(config.repo_path)
    committed = commit_changes(config, now=now)

    logger.info("Pulling from %s/%s.", config.remote, branch)
    try:
        pull_changes(config, branch=branch)
    except GitAutoCommitError as exc:
        logger.error("Pull failed, aborting rebase: %s", exc)
        abort_rebase(config.repo_path)
        raise

    if committed:
        logger.info("Created commit and pushing to %s/%s.", config.remote, branch)
        push_changes(config, branch=branch)
        return True

    if config.push_when_clean:
        logger.info("No staged changes; pushing anyway to %s/%s.", config.remote, branch)
        push_changes(config, branch=branch)
    else:
        logger.info("No changes detected; skipping commit and push.")

    return False


def run_loop(
    config: AutoCommitConfig,
    logger: logging.Logger,
    sleep_fn: Callable[[int], None] = time.sleep,
) -> None:
    while True:
        try:
            run_cycle(config, logger)
        except GitAutoCommitError as exc:
            logger.error("Cycle failed: %s", exc)
        logger.info("Sleeping for %s seconds.", config.interval_seconds)
        sleep_fn(config.interval_seconds)
