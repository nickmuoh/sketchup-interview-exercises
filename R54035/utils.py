import sys
from pathlib import Path

def add_repo_to_path(curr_path: Path):
    """
    Adds the current directory and the repository root to sys.path for module imports.
    """
    if curr_path is None:
        raise ValueError("path argument is required")

    cwd = curr_path.resolve().parent
    repo_root = cwd.parent

    for p in (cwd, repo_root):
        p_str = str(p)

        if p_str not in sys.path:
            sys.path.insert(0, p_str)

    return cwd, repo_root
