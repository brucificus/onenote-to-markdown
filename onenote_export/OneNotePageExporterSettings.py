import dataclasses


@dataclasses.dataclass
class OneNotePageExporterSettings:
    pages_remove_onenote_footer: bool = True
