import subprocess
from functools import cache
from typing import Tuple, Set
from .PandocFormat import *

import pypandoc


@cache
def _pandoc_available_extensions_list(format: PandocFormat = None) -> Tuple[Tuple[bool, str], ...]:
    pandoc_path = pypandoc.get_pandoc_path()
    arg_suffix = f"={format}" if format else ""
    pandoc_list_extensions_result = subprocess.run([pandoc_path, f"--list-extensions{arg_suffix}"], capture_output=True, text=True)
    extensions = pandoc_list_extensions_result.stdout.splitlines()
    extensions = [extension.strip() for extension in extensions]
    extensions = [extension for extension in extensions if extension]
    extensions = [(extension.startswith("+"), extension[1:]) for extension in extensions]
    return tuple(extensions)


def _create_type_PandocExtension(**extras) -> type[enum.Enum]:
    bases = (enum.Enum,)
    new_type_name = "PandocExtension"

    all_formats = tuple(f.value for f in PandocFormat)
    all_extension_values: Set[str] = set()
    for f in all_formats + (None,):
        all_extension_values.update([v for (k, v) in _pandoc_available_extensions_list(format=f)])

    classdict = enum.EnumMeta.__prepare__(new_type_name, bases)
    for ext in all_extension_values:
        classdict[ext] = ext
    for key, value in extras.items():
        classdict[key] = value
    return enum.unique(enum.EnumMeta(new_type_name, bases, classdict))


PandocExtension = _create_type_PandocExtension()
