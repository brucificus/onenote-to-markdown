import os
from functools import reduce


def os_paths_support_character(character: str) -> bool:
    is_windows = os.name == 'nt'
    if is_windows:
        if '"' in character:
            return False
        if '*' in character:
            return False
        elif '/' in character:
            return False
        elif ':' in character:
            return False
        elif '<' in character:
            return False
        elif '>' in character:
            return False
        elif '?' in character:
            return False
        elif '\\' in character:
            return False
        elif '|' in character:
            return False
    if isinstance(character, str):
        if not os.path.supports_unicode_filenames:
            any_unicode = reduce(lambda x, y: x or y, map(lambda x: x in character, map(chr, range(0, 0x110000))))
            if any_unicode:
                return False
    try:
        os.path.exists(character)
        return True
    except ValueError:
        return False
