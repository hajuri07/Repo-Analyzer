import re
import shutil
import tempfile
from pathlib import Path

import git

GITHUB_URL = re.compile(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?(?:\.git)?$")


def clone_repository(repo_url: str) -> str:
    """Clone one public GitHub repository into an isolated OS temp directory."""
    if not GITHUB_URL.fullmatch(repo_url):
        raise ValueError("Use a public HTTPS GitHub repository URL.")
    destination = Path(tempfile.mkdtemp(prefix="repo-review-"))
    try:
        git.Repo.clone_from(repo_url.removesuffix("/").removesuffix(".git"), str(destination), depth=1, single_branch=True)
    except git.exc.GitCommandError as exc:
        shutil.rmtree(destination, ignore_errors=True)
        raise RuntimeError("GitHub could not clone this repository. Confirm it is public and exists.") from exc
    return str(destination)


def remove_cloned_repository(repo_path: str) -> None:
    shutil.rmtree(repo_path, ignore_errors=True)
