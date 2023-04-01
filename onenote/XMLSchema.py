import enum


@enum.unique
class XMLSchema(enum.Enum):
    """
    Specifies the version of the OneNote XML schema to use.
    See: https://learn.microsoft.com/en-us/office/client-developer/onenote/enumerations-onenote-developer-reference#xmlschema-updated-for-onenote-2013
    """
    xs2007 = 0
    """References the OneNote 2007 schema."""

    xs2010 = 1
    """References the OneNote 2010 schema."""

    xs2013 = 2
    """References the OneNote 2013 schema."""

    # xsCurrent = 2
    # """References the schema of the current OneNote version. NOTE: We do not recommend using xsCurrent in most cases,
    # as it can cause compatibility issues with future versions of OneNote. Instead specify the version of the schema that
    # your app was built to handle, like xs2013."""
