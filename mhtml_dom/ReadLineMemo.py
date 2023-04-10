from dataclasses import dataclass


@dataclass
class ReadLineMemo:
    length: int
    ending_file_position: int
