import os
import pathlib
from functools import lru_cache

from typing import Callable, Iterable, Optional


@lru_cache(maxsize=16)
def create_path_commonizer(example_paths: Iterable[str]) -> Optional[Callable[[str], pathlib.Path]]:
    example_paths = set(example_paths)
    if not example_paths:
        raise ValueError('No example paths provided')

    common_path_prefix_trim = 0

    paths_shared_prefix = os.path.commonprefix(list(example_paths))
    if not paths_shared_prefix:
        return None

    if os.sep in paths_shared_prefix:
        common_path_prefix_trim += len(paths_shared_prefix.rsplit(os.sep, 1)[0]) + len(os.sep)
    elif os.altsep and os.altsep in paths_shared_prefix:
        common_path_prefix_trim += len(paths_shared_prefix.rsplit(os.altsep, 1)[0]) + len(os.altsep)
    else:
        common_path_prefix_trim += len(paths_shared_prefix)

    assert \
        len(set(example_paths)) == len(set(p[common_path_prefix_trim:] for p in example_paths)), \
        'Not all paths are unique after trimming the common prefix'

    return lambda p: pathlib.Path(p[common_path_prefix_trim:])
