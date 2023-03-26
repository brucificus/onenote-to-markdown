import pathlib
import shutil
import tempfile
from contextlib import contextmanager
from typing import ContextManager

from .Pathlike import Pathlike


@contextmanager
def temporary_file_path(suffix='', prefix='tmp', dir: Pathlike = None):
    with TemporaryFilePath(suffix, prefix, dir) as path:
        yield path


class TemporaryFilePath(ContextManager[pathlib.Path]):
    def __init__(self, suffix='', prefix='tmp', dir: Pathlike = None):
        self._suffix = suffix
        self._prefix = prefix
        self._temp_dir = pathlib.Path(dir) if dir is str \
            else dir if isinstance(dir, pathlib.Path) \
            else pathlib.Path(str(dir)) if dir \
            else pathlib.Path(tempfile.gettempdir())

    _tempfile_path: pathlib.Path

    def __enter__(self):
        tempfile_name_candidates = tempfile._get_candidate_names()
        for _ in range(tempfile.TMP_MAX):
            tempfile_path_without_suffix = (self._temp_dir / pathlib.Path(self._prefix + next(tempfile_name_candidates)))
            self._tempfile_path = tempfile_path_without_suffix.with_suffix(self._suffix)
            if not self._tempfile_path.exists():
                break
        if self._tempfile_path.exists():
            raise RuntimeError(f"Failed to find unique name for temporary file in {self._temp_dir}")
        return self._tempfile_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._tempfile_path.exists():
            if self._tempfile_path.is_dir():
                shutil.rmtree(self._tempfile_path)
            else:
                self._tempfile_path.unlink(missing_ok=True)
