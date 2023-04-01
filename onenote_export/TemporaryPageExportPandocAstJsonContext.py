import abc

from typing import Optional

from markdown_dom.PandocMarkdownDocumentImportSettings import PandocMarkdownDocumentImportSettings
from onenote_export.Pathlike import Pathlike


class TemporaryPageExportPandocAstJsonContext(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def create_default_import_settings(self) -> PandocMarkdownDocumentImportSettings:
        pass

    @abc.abstractmethod
    def create_pandoc_ast_json(self,
                               open_settings: PandocMarkdownDocumentImportSettings,
                               cworkdir: Optional[Pathlike] = None,
                               ) -> str:
        pass
