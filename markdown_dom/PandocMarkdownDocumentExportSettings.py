import pathlib
from typing import Tuple, Optional

import pypandoc

from markdown_dom.PandocExtension import PandocExtension
from markdown_dom.PandocExtensionActivationMap import PandocExtensionActivationMap
from markdown_dom.PandocFormat import PandocFormat
from markdown_dom.PandocFormatAndExtensions import PandocFormatAndExtensions
from onenote_export.Pathlike import Pathlike


default_extra_args_for_onenote_docx_to_obsidian_md = (
    '--wrap=preserve',
    '--standalone'
)
default_output_format_for_onenote_docx_to_obsidian_md = PandocFormat.markdown
default_output_extensions_for_onenote_docx_to_obsidian_md = str(PandocExtensionActivationMap(
    format=default_output_format_for_onenote_docx_to_obsidian_md,
    value={
        # These are the default values unless otherwise noted.
        # We include the (current) default values here for clarity. See: https://pandoc.org/MANUAL.html
        # We aim for Obsidian compatibility. See: https://www.markdownguide.org/tools/obsidian/
        PandocExtension.abbreviations: False,
        PandocExtension.all_symbols_escapable: False,  # Not a default value. Obsidian doesn't support all symbols as escapable.
        PandocExtension.angle_brackets_escapable: True,  # Not a default value. Obsidian DOES support angle brackets as escapable.
        PandocExtension.ascii_identifiers: False,
        PandocExtension.auto_identifiers: False,  # Not a default value. Obsidian doesn't support identifiers.
        PandocExtension.autolink_bare_uris: False,
        PandocExtension.backtick_code_blocks: True,
        PandocExtension.blank_before_blockquote: True,
        PandocExtension.blank_before_header: True,
        PandocExtension.bracketed_spans: False,  # Not a default value. Obsidian doesn't support bracketed spans.
        PandocExtension.citations: False,  # Not a default value. Obsidian doesn't support citations.
        PandocExtension.compact_definition_lists: False,
        PandocExtension.definition_lists: False,  # Not a default value. Obsidian doesn't support definition lists.
        PandocExtension.east_asian_line_breaks: False,
        PandocExtension.emoji: False,
        PandocExtension.escaped_line_breaks: True,
        PandocExtension.example_lists: False,  # Not a default value. Obsidian doesn't support example lists.
        PandocExtension.fancy_lists: False,  # Not a default value. Obsidian doesn't support fancy lists.
        PandocExtension.fenced_code_attributes: False,  # Not a default value. Obsidian doesn't support fenced code attributes.
        PandocExtension.fenced_code_blocks: True,
        PandocExtension.fenced_divs: False,  # Not a default value. Obsidian doesn't support fenced divs.
        PandocExtension.footnotes: False,  # Not a default value. Obsidian doesn't support footnotes.
        PandocExtension.four_space_rule: False,
        PandocExtension.gfm_auto_identifiers: False,
        PandocExtension.grid_tables: False,  # Not a default value. Obsidian doesn't support grid tables.
        PandocExtension.gutenberg: False,
        PandocExtension.hard_line_breaks: False,
        PandocExtension.header_attributes: False,  # Not a default value. Obsidian doesn't support header attributes.
        PandocExtension.ignore_line_breaks: False,
        PandocExtension.implicit_figures: True,
        PandocExtension.implicit_header_references: True,
        PandocExtension.inline_code_attributes: True,
        PandocExtension.inline_notes: True,
        PandocExtension.intraword_underscores: True,
        PandocExtension.latex_macros: True,
        PandocExtension.line_blocks: False,  # Not a default value. Obsidian doesn't support line blocks.
        PandocExtension.link_attributes: True,  # TODO: Consider disabling this. Obsidian doesn't support link attributes.
        PandocExtension.lists_without_preceding_blankline: True,  # Not a default value. Obsidian supports lists without preceding blank lines.
        PandocExtension.literate_haskell: False,
        # PandocExtension.mark: False,  # Not all recent versions of Pandoc support this extension.
        PandocExtension.markdown_attribute: False,
        PandocExtension.markdown_in_html_blocks: False,  # Not a default value. Obsidian doesn't fully support md in html blocks.
        PandocExtension.mmd_header_identifiers: False,
        PandocExtension.mmd_link_attributes: False,
        PandocExtension.mmd_title_block: False,
        PandocExtension.multiline_tables: False,  # Not a default value. Obsidian doesn't support multiline tables.
        PandocExtension.native_divs: True,
        PandocExtension.native_spans: True,
        PandocExtension.old_dashes: False,
        PandocExtension.pandoc_title_block: False,  # Not a default value. Obsidian doesn't support pandoc title blocks.
        PandocExtension.pipe_tables: True,
        PandocExtension.raw_attribute: False,  # Not a default value. Obsidian doesn't support raw attributes.
        PandocExtension.raw_html: True,
        PandocExtension.raw_tex: False,  # Not a default value. Obsidian doesn't support raw tex.
        PandocExtension.rebase_relative_paths: False,
        PandocExtension.short_subsuperscripts: False,
        PandocExtension.shortcut_reference_links: True,
        PandocExtension.simple_tables: False,  # Not a default value. We don't want simple tables.
        PandocExtension.smart: False,  # Not a default value. TODO: TBD.
        PandocExtension.space_in_atx_header: True,
        PandocExtension.spaced_reference_links: False,
        PandocExtension.startnum: True,
        PandocExtension.strikeout: True,
        PandocExtension.subscript: False,  # Not a default value. Obsidian doesn't support subscript md syntax.
        PandocExtension.superscript: False,  # Not a default value. Obsidian doesn't support superscript md syntax.
        PandocExtension.task_lists: True,
        PandocExtension.table_captions: False,  # Not a default value. Obsidian doesn't support table captions.
        PandocExtension.tex_math_dollars: False,  # Not a default value. Obsidian doesn't support tex math dollars.
        PandocExtension.tex_math_double_backslash: False,
        PandocExtension.tex_math_single_backslash: False,
        # PandocExtension.wikilinks_title_after_pipe: False,  # Not all recent versions of Pandoc support this extension.
        # PandocExtension.wikilinks_title_before_pipe: False,  # Not all recent versions of Pandoc support this extension.
        PandocExtension.yaml_metadata_block: True,
    }
))
default_output_format_and_extensions_for_onenote_docx_to_obsidian_md = PandocFormatAndExtensions(
    default_output_format_for_onenote_docx_to_obsidian_md,
    default_output_extensions_for_onenote_docx_to_obsidian_md,
)


class PandocMarkdownDocumentExportSettings:
    def __init__(self,
                 output_format_and_extensions: PandocFormatAndExtensions,
                 extra_args: Tuple[str, ...] = (),
                 pandoc_path: str = pypandoc.get_pandoc_path()
                 ):
        if not isinstance(output_format_and_extensions, PandocFormatAndExtensions):
            raise TypeError(f'output_format_and_extensions must be of type PandocFormatAndExtensions, not {type(output_format_and_extensions)}')
        if not isinstance(extra_args, tuple):
            raise TypeError(f'extra_args must be of type tuple, not {type(extra_args)}')
        if not isinstance(pandoc_path, str):
            raise TypeError(f'pandoc_path must be of type str, not {type(pandoc_path)}')

        self._output_format_and_extensions = output_format_and_extensions
        self._extra_args = extra_args
        self._pandoc_path = pandoc_path

    @property
    def output_format(self) -> PandocFormat:
        return self._output_format_and_extensions.format

    @property
    def output_format_extensions(self) -> str:
        return self._output_format_and_extensions.extensions

    @property
    def extra_args(self) -> Tuple[str, ...]:
        return self._extra_args

    @property
    def pandoc_path(self) -> str:
        return self._pandoc_path

    def execute_convert_pandoc_ast_json_str_to_markdown_file(self, input_document_ast_json: str, output_md_path: Pathlike, extra_args: Optional[Tuple[str, ...]] = None, cworkdir: Optional[Pathlike] = None):
        if not isinstance(input_document_ast_json, str):
            raise TypeError(f"input_document_ast_json must be a str, not {type(input_document_ast_json)}")
        if not isinstance(output_md_path, str) and not isinstance(output_md_path, pathlib.Path):
            raise TypeError(f"output_md_path must be a str or a pathlib.Path, not {type(output_md_path)}")
        if extra_args is not None and not isinstance(extra_args, tuple):
            raise TypeError(f"extra_args must be a tuple, not {type(extra_args)}")
        if cworkdir is not None and not isinstance(cworkdir, str) and not isinstance(cworkdir, pathlib.Path):
            raise TypeError(f"cworkdir must be a str or a pathlib.Path, not {type(cworkdir)}")

        extra_args_to_use = self.extra_args
        if extra_args is not None:
            extra_args_to_use = extra_args_to_use + extra_args
        if cworkdir is pathlib.Path:
            cworkdir = str(cworkdir)

        result = pypandoc.convert_text(
            source=input_document_ast_json,
            format=str(PandocFormat.json),
            outputfile=output_md_path,
            to=str(self._output_format_and_extensions),
            extra_args=extra_args_to_use,
            verify_format=False,
            cworkdir=cworkdir
        )
        assert result is None or isinstance(result, str) and len(result) == 0, f"Unexpected result from pypandoc.convert_text: {result}"

    @staticmethod
    def create_default_for_onenote_docx_to_obsidian_md() -> 'PandocMarkdownDocumentExportSettings':
        return PandocMarkdownDocumentExportSettings(
            output_format_and_extensions=default_output_format_and_extensions_for_onenote_docx_to_obsidian_md,
            extra_args=default_extra_args_for_onenote_docx_to_obsidian_md,
            pandoc_path=pypandoc.get_pandoc_path(),
        )


    @staticmethod
    def create_default_for_onenote_html_to_obsidian_md() -> 'PandocMarkdownDocumentExportSettings':
        return PandocMarkdownDocumentExportSettings(
            output_format_and_extensions=default_output_format_and_extensions_for_onenote_docx_to_obsidian_md,
            extra_args=default_extra_args_for_onenote_docx_to_obsidian_md,
            pandoc_path=pypandoc.get_pandoc_path(),
        )
