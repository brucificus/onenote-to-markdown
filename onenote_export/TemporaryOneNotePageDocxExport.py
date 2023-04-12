import pathlib
import zipfile

from typing import Optional, Callable, Sequence

from markdown_dom.PandocMarkdownDocumentImportSettings import PandocMarkdownDocumentImportSettings
from onenote import OneNotePage
from onenote_export.PageExportAssetExtraction import PageExportAssetExtraction
from onenote_export.Pathlike import Pathlike
from onenote_export.TemporaryOneNotePageExportFile import TemporaryOneNotePageExportFile
from onenote_export.TemporaryOneNotePageExportKind import TemporaryOneNotePageExportKind
from onenote_export.TemporaryPageExportPandocAstJsonContext import TemporaryPageExportPandocAstJsonContext
from onenote_export.temporary_file import TemporaryFilePath


class TemporaryOneNotePageDocxExport(TemporaryPageExportPandocAstJsonContext, PageExportAssetExtraction, TemporaryOneNotePageExportFile):
    def __init__(self, page: OneNotePage, dir: Pathlike = None):
        super().__init__(page, TemporaryOneNotePageExportKind.DOCX, dir)

    @staticmethod
    def create_default_import_settings(self) -> PandocMarkdownDocumentImportSettings:
        return PandocMarkdownDocumentImportSettings.create_default_for_onenote_docx()

    def create_pandoc_ast_json(self,
                               open_settings: PandocMarkdownDocumentImportSettings = PandocMarkdownDocumentImportSettings.create_default_for_onenote_docx(),
                               cworkdir: Optional[Pathlike] = None,
                               ) -> str:
        if not self._tempfile_path:
            raise Exception("Cannot create MarkdownDocument when TemporaryOneNotePageExportFile is not active.")
        if not self._tempfile_path.exists():
            raise FileNotFoundError(f"File {self._tempfile_path} does not exist")
        if not isinstance(open_settings, PandocMarkdownDocumentImportSettings):
            raise TypeError(f"open_settings must be an instance of PandocMarkdownDocumentImportSettings, not {type(open_settings)}")

        pandoc_ast_json = open_settings.execute_convert_docx_file_to_pandoc_ast_json_str(
            input_docx_path=self._tempfile_path,
            cworkdir=cworkdir,
        )
        return pandoc_ast_json

    def extract_assets_to(self,
                          target_dir: Pathlike,
                          map_extraction_path: Optional[Callable[[pathlib.Path], Optional[pathlib.Path]]] = None,
                          ) -> Sequence[pathlib.Path]:
        """
        Extracts assets from the page export to the target directory.
        :param target_dir: The directory to extract assets to.
        :param map_extraction_path: A function that takes a path to an asset and returns the path to which the asset should be extracted. If None, the asset will not be extracted.
        :return: The paths to the extracted assets.
        """
        if not self._tempfile_path:
            raise Exception("Cannot create MarkdownDocument when TemporaryOneNotePageExportFile is not active.")
        if not self._tempfile_path.exists():
            raise FileNotFoundError(f"File {self._tempfile_path} does not exist")
        if isinstance(target_dir, str):
            target_dir = pathlib.Path(target_dir)
        if not isinstance(target_dir, pathlib.Path):
            raise TypeError(f"target_dir must be an instance of pathlib.Path or str, not {type(target_dir)}")

        extracted_files = ()

        with zipfile.ZipFile(self._tempfile_path, 'r') as zip_ref:
            for asset_file in zip_ref.infolist():
                if asset_file.filename.startswith('word/media/'):
                    asset_file_relative_path = pathlib.Path(asset_file.filename.replace('word/', ''))
                    if map_extraction_path is not None:
                        asset_file_relative_path = map_extraction_path(asset_file_relative_path)

                    if asset_file_relative_path:
                        asset_file_target_path = target_dir / asset_file_relative_path
                        asset_file_target_path.mkdir(parents=True, exist_ok=True)
                        if asset_file_target_path.exists():
                            with zip_ref.open(asset_file) as asset_file_source:
                                with asset_file_target_path.open('w+b') as asset_file_target:
                                    asset_file_target.write(asset_file_source.read())
                        else:
                            with TemporaryFilePath() as temp_dir_path:
                                temp_dir_path.mkdir()
                                temp_file_path = pathlib.Path(zip_ref.extract(asset_file, temp_dir_path))
                                temp_file_path.rename(asset_file_target_path)

                        asset_file_target_path = asset_file_target_path.relative_to(target_dir)
                        extracted_files += (asset_file_target_path,)

        return extracted_files
