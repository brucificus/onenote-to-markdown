import dataclasses
import re


@dataclasses.dataclass
class LabeledRegexSubstitution:
    def __init__(self, label: str, pattern: str, replacement: str, flags: int = 0):
        self._label = label
        self._pattern = re.compile(pattern, flags)
        self._replacement = replacement

    def __str__(self):
        return f'{self._label}: "{self._pattern}" -> "{self._replacement}"'

    def __call__(self, value: str) -> str:
        return re.sub(self._pattern, self._replacement, value)
