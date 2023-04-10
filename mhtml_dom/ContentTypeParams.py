from typing import Dict, Iterable, Tuple, Optional


class ContentTypeParams(Dict[str, str]):
    def __init__(self, data: Iterable[Tuple[str, str]] = ()):
        super().__init__(data)

    @property
    def type(self) -> Optional[str]:
        return self['type'] if 'type' in self else None

    @property
    def charset(self) -> Optional[str]:
        return self['charset'] if 'charset' in self else None

    @property
    def boundary(self) -> Optional[str]:
        return self['boundary'] if 'boundary' in self else None

    def __str__(self):
        return '; '.join(f'{key}={value}' for key, value in self.items())

    def __repr__(self):
        return f'{self.__class__.__name__}(' + '; '.join(f'{key!r}={value!r}' for key, value in self.items()) + ')'

    def __eq__(self, other):
        if isinstance(other, ContentTypeParams):
            return super().__eq__(other)
        return False

    def __hash__(self):
        return hash(tuple(self.items()))
