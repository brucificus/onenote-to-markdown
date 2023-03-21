import pathlib
import tempfile
from contextlib import contextmanager

from .Pathlike import Pathlike


@contextmanager
def temporary_file_path(suffix='', prefix='tmp', dir: Pathlike = None):
    temp_dir = pathlib.Path(dir) if dir is str\
        else dir if isinstance(dir, pathlib.Path)\
        else pathlib.Path(str(dir)) if dir\
        else pathlib.Path(tempfile.gettempdir())
    tempfile_name_candidates = tempfile._get_candidate_names()
    tempfile_path: pathlib.Path
    for _ in range(tempfile.TMP_MAX):
        tempfile_path = (temp_dir / pathlib.Path(prefix + next(tempfile_name_candidates))).with_suffix(suffix)
        if not tempfile_path.exists():
            break
    if tempfile_path.exists():
        raise RuntimeError(f"Failed to find unique name for temporary file in {temp_dir}")
    try:
        yield tempfile_path
    finally:
        if tempfile_path.exists():
            if tempfile_path.is_dir():
                tempfile_path.rmdir()
            else:
                tempfile_path.unlink(missing_ok=True)
