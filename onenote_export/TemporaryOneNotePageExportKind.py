from enum import Enum, unique


@unique
class TemporaryOneNotePageExportKind(str, Enum):
    PDF = 'pdf'
    DOCX = 'docx'
    MHTML = 'mht'
