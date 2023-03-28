from typing import Union

from markdown_dom.PandocExtensionActivationMap import PandocExtensionActivationMap
from markdown_dom.PandocFormat import PandocFormat


class PandocFormatAndExtensions:
    def __init__(self, format: PandocFormat, extensions: Union[PandocExtensionActivationMap, str]):
        if format not in PandocFormat:
            raise ValueError(f"Invalid format: {format}")
        if isinstance(extensions, PandocExtensionActivationMap):
            if extensions.format != format:
                self._output_format_extensions = extensions.clone_with_new_format(format)
            else:
                self._output_format_extensions = extensions.clone()
        elif extensions is None:
            self._output_format_extensions = PandocExtensionActivationMap(format=format)
        elif isinstance(extensions, str):
            self._output_format_extensions = PandocExtensionActivationMap.from_str(extensions, format=format)
        else:
            raise ValueError(f"Invalid extensions: {extensions}")

        self._extensions = self._output_format_extensions

    @property
    def format(self) -> PandocFormat:
        return self._extensions.format

    @property
    def extensions(self) -> str:
        return str(self._extensions)

    def __str__(self) -> str:
        return f'{self.format}{self.extensions}'
