import functools
import hashlib
import pathlib
import shutil

import panflute

from typing import Iterable, Tuple, Union, Callable, Optional, List

from markdown_dom.ChangeTrackingPanfluteDocumentContextManager import ChangeTrackingPanfluteDocumentContextManager
from markdown_dom.PandocMarkdownDocumentExportSettings import PandocMarkdownDocumentExportSettings
from markdown_dom.PandocMarkdownDocumentImportSettings import PandocMarkdownDocumentImportSettings
from markdown_dom.PanfluteElementAccumulatorElementFilterContext import PanfluteElementAccumulatorElementFilterContext
from markdown_dom.type_variables import T, PanfluteElementFilter, PanfluteDocumentFilter, PanfluteElementPredicate, \
    PanfluteImageElementUrlProjection, normalize_elementlike, PanfluteElementLike, PanfluteElementAccumulatorFunc
from markdown_dom.AbstractDocumentElementContentText import AbstractDocumentElementContentText
from markdown_dom.CompoundDocumentElementContentTextMap import CompoundDocumentElementContentTextMap
from onenote_export import temporary_file
from onenote_export.Pathlike import Pathlike


class MarkdownDocument:
    def __init__(self,
                 initial_document_ast_json: Union[str, Callable[[], str]],
                 output_md_path: Pathlike,
                 save_settings: PandocMarkdownDocumentExportSettings = PandocMarkdownDocumentExportSettings.create_default_for_onenote_docx_to_obsidian_md(),
                 ):
        if not callable(initial_document_ast_json) and not isinstance(initial_document_ast_json, str):
            raise TypeError(f"initial_document_ast_json must be a callable or a str, not {type(initial_document_ast_json)}")
        if not isinstance(output_md_path, (str, pathlib.Path)):
            raise TypeError(f"output_md_path must be a str or a pathlib.Path, not {type(output_md_path)}")
        if not isinstance(save_settings, PandocMarkdownDocumentExportSettings):
            raise TypeError(f"save_settings must be a PandocMarkdownDocumentExportSettings, not {type(save_settings)}")

        self._document_context_manager_factory = lambda: ChangeTrackingPanfluteDocumentContextManager.from_ast_json(document_ast_json=initial_document_ast_json)
        self._document_context_manager: Optional[ChangeTrackingPanfluteDocumentContextManager] = None
        self._mode_is_readonly: Optional[bool] = None
        self._is_dirty: bool = False
        self._output_md_path = output_md_path
        self._save_settings = save_settings

    @classmethod
    def import_md_file(cls,
                       input_md_path: Pathlike,
                       open_settings: PandocMarkdownDocumentImportSettings = PandocMarkdownDocumentImportSettings.create_default_for_extant_obsidian_md(),
                       save_settings: PandocMarkdownDocumentExportSettings = PandocMarkdownDocumentExportSettings.create_default_for_onenote_docx_to_obsidian_md(),
                       ) -> 'MarkdownDocument':
        return cls(
            initial_document_ast_json= functools.partial(open_settings.execute_convert_markdown_file_to_pandoc_ast_json_str, input_md_path),
            output_md_path=input_md_path,
            save_settings=save_settings,
        )

    @classmethod
    def open_document_ast_json_str(cls,
                                   initial_document_ast_json: Union[str, Callable[[], str]],
                                   output_md_path: Pathlike,
                                   save_settings: PandocMarkdownDocumentExportSettings = PandocMarkdownDocumentExportSettings.create_default_for_onenote_docx_to_obsidian_md(),
                                   ) -> 'MarkdownDocument':
        return cls(
            initial_document_ast_json=initial_document_ast_json,
            output_md_path=output_md_path,
            save_settings=save_settings,
        )

    @property
    def is_dirty(self) -> bool:
        return self._is_dirty or not self._output_md_path.exists()

    @property
    def is_in_use(self) -> bool:
        return self._document_context_manager is not None and self._mode_is_readonly is not None

    @property
    def checksum(self) -> str:
        return self._use_pandoc_ast_json(lambda ast_json: hashlib.sha256(ast_json.encode('utf-8')).hexdigest())

    def _use_pandoc_ast_json(self, action: Callable[[str], T]) -> T:
        if self.is_in_use:
            raise Exception("Cannot use AST json when document is in use elsewhere.")
        if not self._document_context_manager:
            self._document_context_manager = self._document_context_manager_factory()
        self._mode_is_readonly = True

        try:
            return action(self._document_context_manager.document_ast_json)
        finally:
            self._mode_is_readonly = None

    def _replace_pandoc_ast_json(self, new_ast_json: Union[str, Callable]) -> None:
        if self.is_in_use:
            raise Exception("Cannot replace AST json when document is in use elsewhere.")
        if not self._document_context_manager:
            self._document_context_manager = self._document_context_manager_factory()
        self._mode_is_readonly = True

        with self._document_context_manager:
            if callable(new_ast_json):
                self._document_context_manager.document_ast_json = new_ast_json()
            else:
                self._document_context_manager.document_ast_json = new_ast_json

        if self._document_context_manager.is_dirty:
            self._is_dirty = True
            self._document_context_manager.commit_changes()
        self._mode_is_readonly = None

    def _use_panflute_document(self, action: Callable[[panflute.Doc], T], readonly: bool = True) -> T:
        if readonly:
            if self.is_in_use:
                raise Exception("Cannot begin read-only action while document is in use elsewhere.")
            if not self._document_context_manager:
                self._document_context_manager = self._document_context_manager_factory()
            self._mode_is_readonly = True
        else:
            if self.is_in_use:
                raise Exception("Cannot begin write-enabled action while document is in use elsewhere.")
            if not self._document_context_manager:
                self._document_context_manager = self._document_context_manager_factory()
            self._mode_is_readonly = False

        erring = False
        try:
            with self._document_context_manager:
                return action(self._document_context_manager.panflute_document)
        except:
            erring = True
            raise
        finally:
            if readonly:
                # TODO: Log warning if changes were attempted in a read-only context.
                self._document_context_manager.discard_changes()
            elif not erring and self._document_context_manager.is_dirty:
                self._is_dirty = True
                self._document_context_manager.commit_changes()
            self._mode_is_readonly = None

    def _update_panflute_document(self, projection: Callable[[panflute.Doc], panflute.Doc]):
        def as_document_action(doc: panflute.Doc) -> None:
            new_doc = projection(doc)
            self._document_context_manager.panflute_document = new_doc

        self._use_panflute_document(as_document_action, readonly=False)

    def update_via_panflute_filter(self,
                                   element_filter: PanfluteElementFilter,
                                   *args,
                                   **kwargs
                                   ) -> None:
        """
        Executes one or more filters against the document and its elements. Filtered items are updated in-place using the
        value returned by the respective filter.

        :param prepare_filter: Function executed at the beginning, right after the document is loaded.
        :param element_filter: Function executed on each element of the document that may optionally return a replacement
        for the element.
        :param finalize_filter: Function executed at the end, right before the document is saved.
        :param stop_if: Function executed on each element of the document. If it returns True, the filters are stopped.
        :return: None.
        """
        return self.update_via_panflute_filters(element_filters=[element_filter], *args, **kwargs)

    @staticmethod
    def _wrap_element_filter(element_filter: PanfluteElementFilter) -> Callable[[panflute.Element, panflute.Doc], Optional[Union[panflute.Element, List[panflute.Element]]]]:
        def adjust_filter_result(element: panflute.Element, filter_result: PanfluteElementLike) -> Optional[Union[panflute.Element, List[panflute.Element]]]:
            if filter_result is None:
                return None
            if filter_result is element:
                return None
            if isinstance(filter_result, panflute.Element):
                return filter_result

            filter_result = normalize_elementlike(filter_result, sequence_type=list)

            if not isinstance(filter_result, list):
                raise Exception(f"Filter or normalize_elementlike returned a non-list value: {filter_result}")

            if len(filter_result) == 1 and filter_result[0] is element:
                return None
            if len(filter_result) == 1:
                return filter_result
            return filter_result

        @functools.wraps(element_filter)
        def wrapped_filter(element: panflute.Element, doc: panflute.Doc) -> Callable[[panflute.Element, panflute.Doc], Optional[Union[panflute.Element, List[panflute.Element]]]]:
            filter_result = element_filter(element, doc)
            return adjust_filter_result(element, filter_result)

        return wrapped_filter


    def update_via_panflute_filters(self,
                                    prepare_filter: Optional[PanfluteDocumentFilter] = None,
                                    element_filters: Iterable[PanfluteElementFilter] = (),
                                    finalize_filter: Optional[PanfluteDocumentFilter] = None,
                                    stop_if: Optional[PanfluteElementPredicate] = None,
                                    ) -> None:
        """
        Executes one or more filters against the document and its elements. Filtered items are updated in-place using the
        value returned by the respective filter.

        :param prepare_filter: Function executed at the beginning, right after the document is loaded.
        :param element_filters: Sequence of functions executed on each element of the document that may
        each optionally return a replacement for the element.
        :param finalize_filter: Function executed at the end, right before the document is saved.
        :param stop_if: Function executed on each element of the document. If it returns True, the filters are stopped.
        :return: None.
        """

        element_filters = tuple(map(self._wrap_element_filter, element_filters))

        def document_projection(doc: panflute.Doc) -> panflute.Doc:
            new_doc = panflute.run_filters(
                actions=element_filters,
                prepare=prepare_filter,
                finalize=finalize_filter,
                doc=doc,
                stop_if=stop_if,
            )
            return new_doc

        self._update_panflute_document(document_projection)

    def update_image_element_urls(self,
                                  change: Union[PanfluteImageElementUrlProjection, Tuple[PanfluteImageElementUrlProjection, ...]],
                                  ) -> str:
        if isinstance(change, callable):
            url_projections = (change,)
        elif isinstance(change, tuple) and all(isinstance(c, callable) for c in change):
            url_projections = change
        else:
            raise TypeError(f"Expected callable or tuple of callables, got {change!r}")

        def element_filter(
            element: panflute.Element,
            doc: panflute.Doc,
            url_projection: PanfluteImageElementUrlProjection
        ) -> Optional[panflute.Element]:
            if isinstance(element, panflute.Image):
                new_element_url = url_projection(element, doc)
                if new_element_url != element.url and new_element_url is not None:
                    element.url = new_element_url

        element_filters = tuple(functools.partial(element_filter, url_projection=projection) for projection in url_projections)
        self.update_via_panflute_filters(element_filters=element_filters)

    def accumulate_from_elements(self, accumulator: PanfluteElementAccumulatorFunc, seed: Optional[T] = None, stop_if: Optional[PanfluteElementPredicate] = None) -> T:
        def _document_filter(doc: panflute.Doc) -> T:
            return PanfluteElementAccumulatorElementFilterContext.accumulate_from_elements(element=doc, accumulator=accumulator, seed=seed, stop_if=stop_if)

        return self._use_panflute_document(_document_filter, readonly=True)

    def count_elements(self, predicate: PanfluteElementPredicate = None) -> int:
        def _document_filter(doc: panflute.Doc) -> T:
            return PanfluteElementAccumulatorElementFilterContext.count_elements(element=doc, predicate=predicate)

        return self._use_panflute_document(_document_filter, readonly=True)

    def any_elements(self, predicate: PanfluteElementPredicate = None) -> bool:
        def _document_filter(doc: panflute.Doc) -> T:
            return PanfluteElementAccumulatorElementFilterContext.any_elements(element=doc, predicate=predicate)

        return self._use_panflute_document(_document_filter, readonly=True)

    def all_elements(self, predicate: PanfluteElementPredicate = None) -> bool:
        def _document_filter(doc: panflute.Doc) -> T:
            return PanfluteElementAccumulatorElementFilterContext.all_elements(element=doc, predicate=predicate)

        return self._use_panflute_document(_document_filter, readonly=True)


    def use_text_content(self, action: Callable[[Iterable[AbstractDocumentElementContentText]], T], readonly: bool = True) -> T:
        """
        Executes the given action against the document's text content.
        :param action: Action to execute. It is passed a generator that yields a map of the document's text content.
        :param readonly: Whether the document should be treated as read-only while action is running.
        :return: The result of the action.
        """

        if not isinstance(action, Callable):
            raise TypeError(f"Expected callable, got {action!r}")

        def continuous_text_map_generator(doc: panflute.Doc) -> Iterable[AbstractDocumentElementContentText]:
            while True:
                yield CompoundDocumentElementContentTextMap.from_element_walk(doc)

        def document_filter(doc: panflute.Doc) -> T:
            return action(continuous_text_map_generator(doc))

        return self._use_panflute_document(document_filter, readonly=readonly)

    def _save(self,
              document_ast_json: str,
              pandoc_extra_args: Tuple[str, ...] = (),
              cworkdir: Optional[Pathlike] = None,
              overwrite_existing: bool = True,
              ) -> None:
        if not overwrite_existing and self._output_md_path.exists():
            raise FileExistsError(f"File {self._output_md_path} already exists.")

        with temporary_file.TemporaryFilePath(suffix=".md", dir=cworkdir) as temp_md_path:
            self._save_settings.execute_convert_pandoc_ast_json_str_to_markdown_file(
                input_document_ast_json=document_ast_json,
                output_md_path=temp_md_path,
                extra_args=pandoc_extra_args,
                cworkdir=cworkdir,
            )
            if self._output_md_path.exists():
                # Sometimes 'unlink' fails when the file is open in another process.
                # So we try to manually overwrite the file content instead.
                # This also preserves the file's metadata.
                with temp_md_path.open("rb") as fs:
                    with self._output_md_path.open("wb") as fd:
                        shutil.copyfileobj(fs, fd)
            else:
                shutil.move(temp_md_path, self._output_md_path)

    def save(self,
             pandoc_extra_args: Tuple[str, ...] = (),
             cworkdir: Optional[Pathlike] = None,
             overwrite_existing: bool = True
             ) -> None:
        saver = functools.partial(
            self._save,
            pandoc_extra_args=pandoc_extra_args,
            cworkdir=cworkdir,
            overwrite_existing=overwrite_existing,
        )
        self._use_pandoc_ast_json(saver)
        self._is_dirty = False

    def __str__(self):
        members = ()
        members += (f"{self._output_md_path}",)
        if self.is_dirty:
            members += ("is_dirty",)
        if self.is_in_use:
            members += ("is_in_use",)
        return f"{self.__class__.__name__}({', '.join(members)})"

    def __repr__(self):
        members = ()
        members += (f"{self._output_md_path!r}",)
        members += (f"is_dirty={self.is_dirty!r}",)
        members += (f"is_in_use={self.is_in_use!r}",)
        return f"{self.__class__.__name__}({', '.join(members)})"
