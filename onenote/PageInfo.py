import enum


@enum.unique
class PageInfo(enum.Enum):
    """
    Specifies the type of information that GetPageContent will return with the page content.
    See: https://learn.microsoft.com/en-us/office/client-developer/onenote/enumerations-onenote-developer-reference#pageinfo-updated-for-onenote-2013
    """
    piBasic = 0
    """Returns only basic page content, without selection markup, file types for binary data objects and binary data
    objects. This is the standard value to pass."""

    piBinaryData = 1
    """Returns page content with no selection markup, but with all binary data."""

    piSelection = 2
    """Returns page content with selection markup, but no binary data."""

    piBinaryDataSelection = 3
    """Returns page content with selection markup and all binary data."""

    piFileType = 4
    """Returns page content with file type info for binary data objects."""

    piBinaryDataFileType = 5
    """Returns page content with file type info for binary data objects and binary data objects."""

    piSelectionFileType = 6
    """Returns page content with selection markup and file type info for binary data."""

    piAll = 7
    """Returns all page content."""
