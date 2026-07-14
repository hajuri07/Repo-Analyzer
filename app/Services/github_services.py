import re
import uuid
from pathlib import Path

import git


def clone_repository(repo_url: str) -> str:
    # Its validating the url hehe 
    if not re.match(r"^(https://|git@)github\.com[:/].+", repo_url):
        raise ValueError("Must be a valid GitHub repository URL.")

    # extracting the repo name
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")

    # Create the temp directory if it doesn't exist
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    # Create a unique folder for this analysis
    unique_folder = uuid.uuid4().hex
    local_path = temp_dir / unique_folder

    try:
        # Shallow clone (latest commit only)
        git.Repo.clone_from(
            repo_url,
            str(local_path),
            depth=1
        )
    except git.exc.GitCommandError as e:
        raise RuntimeError(f"Git clone failed: {e.stderr}")

    return str(local_path)