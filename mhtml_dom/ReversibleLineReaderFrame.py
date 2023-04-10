from typing import IO, Tuple

from mhtml_dom.ReadLineMemo import ReadLineMemo


class ReversibleLineReaderFrame:
    def __init__(self, file: IO[bytes], encoding: str, consume_eof: bool = False):
        self._file = file
        self._encoding = encoding
        self._file_starting_position = self._file.tell()
        self._committed_lines_read = (ReadLineMemo(
            length=0,
            ending_file_position=self._file_starting_position,
        ),)
        self._uncommitted_lines_read = ()
        self._consume_eof = consume_eof

    def _create_memo(self) -> ReadLineMemo:
        previous_memo = self._uncommitted_lines_read[-1] if self._uncommitted_lines_read else self._committed_lines_read[-1]

        ending_file_position = self._file.tell()
        length = ending_file_position - previous_memo.ending_file_position

        return ReadLineMemo(
            length=length,
            ending_file_position=ending_file_position,
        )

    def readline(self) -> str:
        previous_memo = self._uncommitted_lines_read[-1] if self._uncommitted_lines_read else self._committed_lines_read[-1]
        self._file.seek(previous_memo.ending_file_position)

        line_bytes = self._file.readline()
        line = line_bytes.decode(self._encoding, errors='replace')

        if line_bytes or self._consume_eof:
            self._uncommitted_lines_read = self._uncommitted_lines_read + (self._create_memo(),)
        return line

    @property
    def committed_lines_read(self) -> Tuple[ReadLineMemo, ...]:
        return self._committed_lines_read[1:]

    @property
    def file_starting_position(self) -> int:
        return self._file_starting_position

    @property
    def uncommitted_lines_read(self) -> Tuple[ReadLineMemo, ...]:
        return self._uncommitted_lines_read

    @property
    def committed_bytes_read_count(self) -> int:
        return self._committed_lines_read[-1].ending_file_position - self._file_starting_position

    @property
    def committed_file_position(self) -> int:
        return self._committed_lines_read[-1].ending_file_position

    @property
    def uncommitted_bytes_read_count(self) -> int:
        if not self._uncommitted_lines_read:
            return 0
        return self._uncommitted_lines_read[-1].ending_file_position - self._committed_lines_read[-1].ending_file_position

    @property
    def uncommitted_file_position(self) -> int:
        if not self._uncommitted_lines_read:
            return self._committed_lines_read[-1].ending_file_position
        return self._uncommitted_lines_read[-1].ending_file_position

    def commit_advancement(self, lines_ago: int = 0):
        lines_ago = abs(lines_ago)
        if lines_ago > len(self._uncommitted_lines_read):
            raise ValueError('Cannot commit advancement that far back')

        if not self._uncommitted_lines_read:
            return

        cutoff = len(self._uncommitted_lines_read) - lines_ago
        newly_committed_memos = tuple(self._uncommitted_lines_read[:cutoff])
        self._committed_lines_read = self._committed_lines_read + newly_committed_memos
        self._uncommitted_lines_read = self._uncommitted_lines_read[cutoff:]

    def __exit__(self, exc_type, exc_val, exc_tb):
        commit_memo = self._committed_lines_read[-1]
        self._file.seek(commit_memo.ending_file_position)
        del self._file
