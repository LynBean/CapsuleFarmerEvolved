
from pathlib import Path

DATA_DIR_PATH = Path("./data")

def makePath(pathLike: str=None) -> Path:
    """
    Creates a Path object from the given filename and directory name
    """
    if pathLike is None:
        return DATA_DIR_PATH.absolute().resolve()

    return DATA_DIR_PATH.joinpath(pathLike).absolute().resolve()

def isDocker() -> bool:
    return Path("/.dockerenv").exists()