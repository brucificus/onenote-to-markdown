import enum


@enum.unique
class PublishFormat(enum.Enum):
    """
    Specifies the format in which to export the page.
    See: https://learn.microsoft.com/en-us/office/client-developer/onenote/enumerations-onenote-developer-reference#publishformat
    """
    pfOneNote = 0
    pfOneNotePackage = 1
    pfMHTML = 2
    pfPDF = 3
    pfXPS = 4
    pfWord = 5
    pfEMF = 6
    pfHTML = 7
    pfOneNote2007 = 8
