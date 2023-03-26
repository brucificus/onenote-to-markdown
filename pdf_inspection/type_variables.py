from typing import Union, TypeVar, List, Dict, Any, Tuple, TypedDict

from fitz import fitz


T = TypeVar('T')

fitzShapelike = Union[fitz.Point, fitz.Rect, fitz.Quad]

fitzDrawingsEntryItems = List[Tuple[str, fitzShapelike, int]]


class fitzDrawingsEntry(TypedDict):
    items: fitzDrawingsEntryItems
    type: str
    even_odd: bool
    fill_opacity: float
    closePath: bool
    fill: Tuple[float, float, float]
    rect: fitz.Rect
    seqno: int
    color: Any
    width: int
    lineCap: int
    lineJoin: int
    dashes: str
    stroke_opacity: float


fitzDrawings = List[fitzDrawingsEntry]

fitzImagesEntryRest = Tuple[Any, ...]

fitzImagesEntryRaw = Tuple[int, *fitzImagesEntryRest]

fitzImagesEntryResolved = Tuple[fitz.Pixmap, *fitzImagesEntryRest]
