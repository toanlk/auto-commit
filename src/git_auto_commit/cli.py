from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from git_auto_commit.service import AutoCommitConfig, GitAutoCommitError, run_cycle, run_loop


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Automatically git add, commit, and push a repository on a fixed interval."
    )
    parser.add_argument("--repo", default=".", help="Path to the git repository.")
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Seconds between sync cycles in loop mode.",
    )
    parser.add_argument("--remote", default="origin", help="Remote name to push to.")
    parser.add_argument("--branch", default="main", help="Branch name to push to.")
    parser.add_argument(
        "--message-template",
        default="Auto commit {timestamp}",
        help="Commit message template. Supports {timestamp}.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single sync cycle and exit.",
    )
    parser.add_argument(
        "--push-when-clean",
        action="store_true",
        help="Push even when no new commit was created.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logger = logging.getLogger("git-auto-commit")

    config = AutoCommitConfig(
        repo_path=Path(args.repo).resolve(),
        interval_seconds=args.interval,
        remote=args.remote,
        branch=args.branch,
        commit_message_template=args.message_template,
        push_when_clean=args.push_when_clean,
    )

    try:
        if args.once:
            run_cycle(config, logger)
        else:
            run_loop(config, logger)
    except GitAutoCommitError as exc:
        logger.error("%s", exc)
        return 1
    except KeyboardInterrupt:
        logger.info("Stopped by user.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
