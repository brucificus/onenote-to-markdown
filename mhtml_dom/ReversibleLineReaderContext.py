from typing import IO

from mhtml_dom.ReversibleLineReaderFrame import ReversibleLineReaderFrame


class ReversibleLineReaderContext:
    def __init__(self, file: IO[bytes], encoding: str):
        self._file = file
        self._encoding = encoding
        self._frames = []

    def __enter__(self) -> ReversibleLineReaderFrame:
        frame = ReversibleLineReaderFrame(self._file, self._encoding)
        self._frames.insert(0, frame)
        return frame

    def __exit__(self, exc_type, exc_val, exc_tb):
        frame = self._frames.pop(0)
        frame.__exit__(exc_type, exc_val, exc_tb)
        del frame
