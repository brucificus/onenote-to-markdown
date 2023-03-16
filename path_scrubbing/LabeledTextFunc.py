import dataclasses
from typing import Callable


@dataclasses.dataclass
class LabeledTextFunc:
    def __init__(self, label: str, func: Callable[[str], str]):
        self._label = label
        self._func = func

    def __str__(self):
        return f'{self._label}: {self._func}'

    def __call__(self, value: str) -> str:
        return self._func(value)
