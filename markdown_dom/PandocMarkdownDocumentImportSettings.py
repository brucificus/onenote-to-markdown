import pathlib
from typing import Tuple, Optional

import pypandoc

from markdown_dom.PandocFormat import PandocFormat
from markdown_dom.PandocFormatAndExtensions import PandocFormatAndExtensions
from markdown_dom.PandocMarkdownDocumentExportSettings import default_extra_args_for_onenote_docx_to_obsidian_md, \
    default_output_format_and_extensions_for_onenote_docx_to_obsidian_md
from onenote_export.Pathlike import Pathlike


default_input_format_and_extensions_for_onenote_docx_to_ast_json = PandocFormatAndExtensions(
    format=PandocFormat.docx,
    extensions='+citations',
)
default_extra_args_for_onenote_docx_to_ast_json = (
    '--standalone',
    '--wrap=preserve',
    '--preserve-tabs',
    '--embed-resources',
)


default_input_format_and_extensions_for_obsidian_md_to_ast_json = PandocFormatAndExtensions(
    format=default_output_format_and_extensions_for_onenote_docx_to_obsidian_md.format,
    extensions=default_output_format_and_extensions_for_onenote_docx_to_obsidian_md.extensions,
)
default_extra_args_for_obsidian_md_to_ast_json = default_extra_args_for_onenote_docx_to_obsidian_md

default_input_format_and_extensions_for_onenote_html_to_ast_json = PandocFormatAndExtensions(
    format=PandocFormat.html,
    extensions='+task_lists',
)
default_extra_args_for_onenote_html_to_ast_json = default_extra_args_for_onenote_docx_to_obsidian_md


class PandocMarkdownDocumentImportSettings:
    def __init__(self,
                 input_format_and_extensions: PandocFormatAndExtensions,
                 extra_args: Tuple[str, ...] = (),
                 pandoc_path: str = pypandoc.get_pandoc_path()
                 ):
        if not isinstance(input_format_and_extensions, PandocFormatAndExtensions):
            raise TypeError(f'input_format_and_extensions must be of type PandocFormatAndExtensions, not {type(input_format_and_extensions)}')
        if not isinstance(extra_args, tuple):
            raise TypeError(f'extra_args must be of type tuple, not {type(extra_args)}')
        if not isinstance(pandoc_path, str):
            raise TypeError(f'pandoc_path must be of type str, not {type(pandoc_path)}')

        self._input_format_and_extensions = input_format_and_extensions
        self._extra_args = extra_args
        self._pandoc_path = pandoc_path

    @property
    def input_format(self) -> PandocFormat:
        return self._input_format_and_extensions.format

    @property
    def input_format_extensions(self) -> str:
        return self._input_format_and_extensions.extensions

    @property
    def extra_args(self) -> Tuple[str, ...]:
        return self._extra_args

    @property
    def pandoc_path(self) -> str:
        return self._pandoc_path

    def execute_convert_docx_file_to_pandoc_ast_json_str(self, input_docx_path: Pathlike, extra_args: Optional[Tuple[str, ...]] = None, cworkdir: Optional[Pathlike] = None) -> str:
        if not isinstance(input_docx_path, str) and not isinstance(input_docx_path, pathlib.Path):
            raise TypeError(f"input_docx_path must be a str or a pathlib.Path, not {type(input_docx_path)}")
        if extra_args is not None and not isinstance(extra_args, tuple):
            raise TypeError(f"extra_args must be a tuple, not {type(extra_args)}")
        if cworkdir is not None and not isinstance(cworkdir, str) and not isinstance(cworkdir, pathlib.Path):
            raise TypeError(f"cworkdir must be a str or a pathlib.Path, not {type(cworkdir)}")

        extra_args_to_use = self.extra_args
        if extra_args is not None:
            extra_args_to_use = extra_args_to_use + extra_args
        if cworkdir is pathlib.Path:
            cworkdir = str(cworkdir)

        result = pypandoc.convert_file(
            source_file=input_docx_path,
            format=str(self._input_format_and_extensions),
            to=str(PandocFormat.json),
            extra_args=extra_args_to_use,
            encoding='utf-8',
            cworkdir=cworkdir,
        )
        assert isinstance(result, str) and len(result) > 0, f"Unexpected result from pypandoc.convert_file: {result}"
        return result

    def execute_convert_markdown_file_to_pandoc_ast_json_str(self, input_md_path: Pathlike, extra_args: Optional[Tuple[str, ...]] = None, cworkdir: Optional[Pathlike] = None) -> str:
        if not isinstance(input_md_path, str) and not isinstance(input_md_path, pathlib.Path):
            raise TypeError(f"input_md_path must be a str or a pathlib.Path, not {type(input_md_path)}")
        if extra_args is not None and not isinstance(extra_args, tuple):
            raise TypeError(f"extra_args must be a tuple, not {type(extra_args)}")
        if cworkdir is not None and not isinstance(cworkdir, str) and not isinstance(cworkdir, pathlib.Path):
            raise TypeError(f"cworkdir must be a str or a pathlib.Path, not {type(cworkdir)}")

        extra_args_to_use = self.extra_args
        if extra_args is not None:
            extra_args_to_use = extra_args_to_use + extra_args
        if cworkdir is pathlib.Path:
            cworkdir = str(cworkdir)

        result = pypandoc.convert_file(
            source_file=input_md_path,
            format=str(self._input_format_and_extensions),
            to=str(PandocFormat.json),
            extra_args=extra_args_to_use,
            encoding='utf-8',
            cworkdir=cworkdir,
        )
        assert isinstance(result, str) and len(result) > 0, f"Unexpected result from pypandoc.convert_file: {result}"
        return result

    def execute_convert_html_file_to_pandoc_ast_json_str(self, input_html_path: Pathlike, extra_args: Optional[Tuple[str, ...]] = None, cworkdir: Optional[Pathlike] = None) -> str:
        if not isinstance(input_html_path, str) and not isinstance(input_html_path, pathlib.Path):
            raise TypeError(f"input_html_path must be a str or a pathlib.Path, not {type(input_html_path)}")
        if extra_args is not None and not isinstance(extra_args, tuple):
            raise TypeError(f"extra_args must be a tuple, not {type(extra_args)}")
        if cworkdir is not None and not isinstance(cworkdir, str) and not isinstance(cworkdir, pathlib.Path):
            raise TypeError(f"cworkdir must be a str or a pathlib.Path, not {type(cworkdir)}")

        extra_args_to_use = self.extra_args
        if extra_args is not None:
            extra_args_to_use = extra_args_to_use + extra_args
        if cworkdir is pathlib.Path:
            cworkdir = str(cworkdir)

        result = pypandoc.convert_file(
            source_file=input_html_path,
            format=str(self._input_format_and_extensions),
            to=str(PandocFormat.json),
            extra_args=extra_args_to_use,
            encoding='utf-8',
            cworkdir=cworkdir,
        )
        assert isinstance(result, str) and len(result) > 0, f"Unexpected result from pypandoc.convert_file: {result}"
        return result

    @staticmethod
    def create_default_for_onenote_docx() -> 'PandocMarkdownDocumentImportSettings':
        return PandocMarkdownDocumentImportSettings(
            input_format_and_extensions=default_input_format_and_extensions_for_onenote_docx_to_ast_json,
            extra_args=default_extra_args_for_onenote_docx_to_ast_json,
            pandoc_path=pypandoc.get_pandoc_path(),
        )

    @staticmethod
    def create_default_for_extant_obsidian_md() -> 'PandocMarkdownDocumentImportSettings':
        return PandocMarkdownDocumentImportSettings(
            input_format_and_extensions=default_input_format_and_extensions_for_obsidian_md_to_ast_json,
            extra_args=default_extra_args_for_obsidian_md_to_ast_json,
            pandoc_path=pypandoc.get_pandoc_path(),
        )

    @staticmethod
    def create_default_for_onenote_html() -> 'PandocMarkdownDocumentImportSettings':
        return PandocMarkdownDocumentImportSettings(
            input_format_and_extensions=default_input_format_and_extensions_for_onenote_html_to_ast_json,
            extra_args=default_extra_args_for_onenote_html_to_ast_json,
            pandoc_path=pypandoc.get_pandoc_path(),
        )
