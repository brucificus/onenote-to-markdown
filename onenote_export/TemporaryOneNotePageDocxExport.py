import subprocess

from onenote import OneNotePage
from onenote_export.Pathlike import Pathlike
from onenote_export.TemporaryOneNotePageExportFile import TemporaryOneNotePageExportFile
from onenote_export.TemporaryOneNotePageExportKind import TemporaryOneNotePageExportKind


class TemporaryOneNotePageDocxExport(TemporaryOneNotePageExportFile):
    def __init__(self, page: OneNotePage, dir: Pathlike = None, subprocess_run: subprocess.run = subprocess.run):
        super().__init__(page, TemporaryOneNotePageExportKind.DOCX, dir)
        self._subprocess_run = subprocess_run

    def run_pandoc_conversion_to_markdown(self, output_md_path: Pathlike):
        if self._tempfile_path is None:
            raise RuntimeError("TemporaryOneNotePageDocxExport must be entered before calling run_pandoc_conversion_to_markdown")

        pandoc_command = [
            'pandoc',
            '-i', str(self.tempfile_path),
            '-o', str(output_md_path),
            '-t', 'markdown-simple_tables-multiline_tables-grid_tables',
            '--wrap=none',
        ]
        return self._subprocess_run(pandoc_command, check=True)
