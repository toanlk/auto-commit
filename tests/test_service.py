from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from git_auto_commit.service import (
    AutoCommitConfig,
    GitAutoCommitError,
    commit_changes,
    ensure_git_repository,
    get_current_branch,
    run_cycle,
)


def make_completed_process(returncode: int, stdout: str = "", stderr: str = ""):
    class Result:
        def __init__(self) -> None:
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    return Result()


def test_render_commit_message_uses_timestamp() -> None:
    config = AutoCommitConfig(repo_path=Path("."), commit_message_template="Sync {timestamp}")
    rendered = config.render_commit_message(datetime(2026, 6, 23, 10, 11, 12))
    assert rendered == "Sync 2026-06-23 10:11:12"


def test_ensure_git_repository_raises_for_missing_path(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing"
    with pytest.raises(GitAutoCommitError):
        ensure_git_repository(missing_path)


def test_commit_changes_returns_false_when_index_clean() -> None:
    config = AutoCommitConfig(repo_path=Path("."))
    with patch(
        "git_auto_commit.service.run_git_command",
        side_effect=[make_completed_process(0)],
    ):
        assert commit_changes(config) is False


def test_run_cycle_commits_and_pushes() -> None:
    logger = logging.getLogger("test")
    config = AutoCommitConfig(repo_path=Path("."), remote="origin", branch="main")
    with patch(
        "git_auto_commit.service.run_git_command",
        side_effect=[
            make_completed_process(0, stdout="true\n"),
            make_completed_process(0),
            make_completed_process(0),
            make_completed_process(1),
            make_completed_process(0, stdout="[main abc] Auto commit"),
            make_completed_process(0, stdout="pushed"),
        ],
    ):
        changed = run_cycle(config, logger, now=datetime(2026, 6, 23, 10, 11, 12))

    assert changed is True


def test_run_cycle_pushes_current_branch_by_default() -> None:
    logger = logging.getLogger("test")
    config = AutoCommitConfig(repo_path=Path("."))
    with patch(
        "git_auto_commit.service.run_git_command",
        side_effect=[
            make_completed_process(0, stdout="true\n"),
            make_completed_process(0, stdout="develop\n"),
            make_completed_process(0),
            make_completed_process(0),
            make_completed_process(1),
            make_completed_process(0, stdout="[develop abc] Auto commit"),
            make_completed_process(0, stdout="pushed"),
        ],
    ) as runner:
        changed = run_cycle(config, logger, now=datetime(2026, 6, 23, 10, 11, 12))

    assert changed is True
    assert runner.call_args_list[-1].args == (Path("."), "push", "origin", "develop")


def test_get_current_branch_raises_for_detached_head() -> None:
    with patch(
        "git_auto_commit.service.run_git_command",
        return_value=make_completed_process(0, stdout=""),
    ):
        with pytest.raises(GitAutoCommitError, match="detached HEAD"):
            get_current_branch(Path("."))


def test_run_cycle_skips_push_when_clean() -> None:
    logger = logging.getLogger("test")
    config = AutoCommitConfig(repo_path=Path("."))
    with patch(
        "git_auto_commit.service.run_git_command",
        side_effect=[
            make_completed_process(0, stdout="true\n"),
            make_completed_process(0, stdout="main\n"),
            make_completed_process(0),
            make_completed_process(0),
            make_completed_process(0),
        ],
    ) as runner:
        changed = run_cycle(config, logger)

    assert changed is False
    assert runner.call_count == 5
