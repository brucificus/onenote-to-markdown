import re
from functools import cache
from typing import Dict, Optional, Union

from markdown_dom.PandocExtension import PandocExtension, _pandoc_available_extensions_list
from markdown_dom.PandocFormat import PandocFormat


class PandocExtensionActivationMap(Dict[PandocExtension, Optional[bool]]):
    def __init__(self, value: Optional[Union[str, Dict[PandocExtension, Optional[bool]]]] = None,
                 format: Optional[PandocFormat] = None) -> object:
        super().__init__()
        self._format = format
        if isinstance(value, PandocExtensionActivationMap):
            value = str(value)
        if isinstance(value, (dict, str)):
            self.update(value)
        elif value is not None:
            raise ValueError(f"Invalid value: {value}")

    @property
    def format(self) -> Optional[PandocFormat]:
        return self._format

    def clone(self) -> 'PandocExtensionActivationMap':
        return PandocExtensionActivationMap(value=self, format=self._format)

    def clone_with_new_format(self, new_format: Optional[PandocFormat], omit_current_defaults: bool = False, elide_unsupported_extensions: bool = False) -> 'PandocExtensionActivationMap':
        new_map = PandocExtensionActivationMap(format=new_format)

        if self._format != new_format and not omit_current_defaults:
            for default_value, extension in _pandoc_available_extensions_list(format=self._format):
                new_map[extension] = default_value

        new_map.update(self, elide_unsupported_extensions=elide_unsupported_extensions)

        return new_map

    def __setitem__(self, key: PandocExtension, value: Optional[bool]):
        if not isinstance(key, PandocExtension) and str(key) not in PandocExtension.__members__:
            raise ValueError(f"Invalid key: {key}")
        if not isinstance(key, PandocExtension):
            key = PandocExtension.__members__[str(key)]
        if not isinstance(value, bool) and value is not None:
            raise ValueError(f"Invalid value: {value}")
        if self._format and not self._is_supported_for_format(key, self._format):
            raise ValueError(f"Extension {key} is not available for format {self._format}")
        super().__setitem__(key, value)

    def __getitem__(self, key: PandocExtension) -> Optional[bool]:
        if not isinstance(key, PandocExtension) and str(key) not in PandocExtension.__members__:
            raise ValueError(f"Invalid key: {key}")
        if not isinstance(key, PandocExtension):
            key = PandocExtension.__members__[str(key)]
        if not super().__contains__(key):
            if self._format:
                super().__setitem__(key, self._default_value_for_format(key, self._format))
            else:
                super().__setitem__(key, None)
        return super().__getitem__(key)

    def __missing__(self, key: PandocExtension) -> Optional[bool]:
        return self[key]

    def __contains__(self, item):
        if not isinstance(item, PandocExtension) and str(item) not in PandocExtension.__members__:
            raise ValueError(f"Invalid key: {item}")
        if not isinstance(item, PandocExtension):
            item = PandocExtension.__members__[str(item)]
        if not super().__contains__(item):
            if self._format:
                super().__setitem__(item, self._default_value_for_format(item, self._format))
            else:
                super().__setitem__(item, None)
        return super().__contains__(item)

    def update(self, other: Union[Dict[PandocExtension, Optional[bool]], str], elide_unsupported_extensions: bool = False):
        if isinstance(other, str):
            other = PandocExtensionActivationMap.from_str(other)
        if isinstance(other, PandocExtensionActivationMap) and other._format == self._format:
            super().update(other)
            return
        if not isinstance(other, dict):
            raise ValueError(f"Invalid value: {other}")
        for key, value in other.items():
            if not isinstance(key, PandocExtension) and str(key) not in PandocExtension.__members__:
                raise ValueError(f"Invalid key: {key}")
            if not isinstance(key, PandocExtension):
                key = PandocExtension.__members__[str(key)]
            if not isinstance(value, bool) and value is not None:
                raise ValueError(f"Invalid value: {value}")
            if self._format and not self._is_supported_for_format(key, self._format):
                if elide_unsupported_extensions:
                    continue
                raise ValueError(f"Extension {key} is not available for format {self._format}")

            super().__setitem__(key, value)

    def __str__(self, omit_format_defaults: bool = True) -> str:
        def include_part(extension: PandocExtension, value: Optional[bool]) -> bool:
            if self._format and omit_format_defaults:
                return value != self._default_value_for_format(extension, self._format)
            return value is not None

        parts = ((self[extension], extension) for extension in self if include_part(extension, self[extension]))
        parts = sorted(parts, key=lambda part: part[1].value)
        parts = ((f"+{extension.name}" if enabled else f"-{extension.name}") for enabled, extension in parts)
        result = "".join(parts)
        return result

    @staticmethod
    @cache
    def _is_supported_for_format(extension: PandocExtension, format: Optional[PandocFormat]) -> bool:
        return any(True for e in _pandoc_available_extensions_list(format) if e[1] == extension.value)

    @staticmethod
    @cache
    def _default_value_for_format(extension: PandocExtension, format: Optional[PandocFormat]) -> Optional[bool]:
        for enabled, ext in _pandoc_available_extensions_list(format):
            if ext == extension:
                return enabled
        if not PandocExtensionActivationMap._is_supported_for_format(extension, format):
            raise ValueError(f"Extension {extension} is not supported for format {format}")
        return None

    @classmethod
    def from_str(cls, extensions_str: str, format: Optional[PandocFormat] = None) -> 'PandocExtensionActivationMap':
        result = cls(format=format)
        parts = re.findall(r'\s*?([+-][\w_]+)\s*?', extensions_str)
        parts = [p.strip() for p in parts if p]

        for part in parts:
            if part.startswith("+"):
                result[part[1:]] = True
            elif part.startswith("-"):
                result[part[1:]] = False
            else:
                raise ValueError(f"Invalid extension part: {part}")
        return result
