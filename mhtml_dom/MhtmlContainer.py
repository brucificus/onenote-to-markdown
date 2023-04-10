import encodings
import itertools
import os
import pathlib
from collections.abc import Iterable
from functools import cache

from typing import Union, Optional, Set

from .ContentType import ContentType
from .MhtmlContainerHeaders import MhtmlContainerHeaders
from .MhtmlContentItem import MhtmlContentItem
from .mhtml_chunks import skip_mhtml_blank_lines, read_mhtml_header_chunk, parse_mhtml_header_chunk, read_mhtml_body_chunk, \
    parse_mhtml_body_chunk, skip_mhtml_section_boundary_line
from .path_commonizer import create_path_commonizer


class MhtmlContainer(MhtmlContainerHeaders):
    def __init__(self, container_headers: MhtmlContainerHeaders, content_items: tuple[MhtmlContentItem]):
        if not content_items:
            raise ValueError('No content_items provided')

        assert all(item.body is not None for item in content_items)

        super().__init__(container_headers._headers)
        self._content_items = content_items

    @property
    def content_items(self) -> tuple[MhtmlContentItem]:
        return self._content_items

    @property
    @cache
    def extractable_content_items(self) -> Set[MhtmlContentItem]:
        items_having_content_location = {item for item in self.content_items if item.content_location}
        path_commonizer = create_path_commonizer(tuple(item.content_location for item in items_having_content_location))
        if not path_commonizer:
            return set()

        items_by_transformed_path = [(path_commonizer(item.content_location), item) for item in items_having_content_location]
        items_by_transformed_path = sorted(items_by_transformed_path, key=lambda item: item[0])
        items_grouped_by_transformed_path_iter = itertools.groupby(items_by_transformed_path, key=lambda item: item[0])
        items_grouped_by_transformed_path = {tp: set(list(items)[0][1:]) for tp, items in items_grouped_by_transformed_path_iter}

        items_retaining_unique_content_location = {list(items_grouped_by_transformed_path[tp])[0] for tp in items_grouped_by_transformed_path if len(items_grouped_by_transformed_path[tp]) == 1}
        return items_retaining_unique_content_location

    @property
    @cache
    def is_fully_extractable(self) -> bool:
        items_having_content_location = {item for item in self.content_items if item.content_location}
        return len(items_having_content_location) == len(self.extractable_content_items)

    def extractall(self, output_dir: pathlib.Path, *, overwrite: bool = False) -> Optional[pathlib.Path]:
        """
        Extracts all content items to the specified directory, and returns the path to the first HTML content item (if any).
        This only supports cases where the content items have a common prefix in their content_location.
        :param output_dir: The directory to which the content items will be extracted.
        :return: The path to the first HTML content item (if any).
        """

        if not output_dir.exists():
            output_dir.mkdir(parents=True)
        if not output_dir.is_dir():
            raise ValueError('output_dir must be a directory')

        path_commonizer = create_path_commonizer(tuple(item.content_location for item in self.extractable_content_items))

        if not self.is_fully_extractable or not path_commonizer:
            raise ValueError('Cannot extract content items to a common directory because a common content_location prefix could not be extracted from them')

        items_by_path = {path_commonizer(item.content_location): item for item in self.extractable_content_items}

        first_html_item_path: Optional[pathlib.Path] = None
        for item_path in sorted(items_by_path.keys()):
            item = items_by_path[item_path]
            assert item.body is not None

            item_output_path = output_dir / item_path
            item_output_path.parent.mkdir(parents=True, exist_ok=True)
            item.save_to_file(item_output_path, overwrite=overwrite)

            if not first_html_item_path and item.content_type.value.startswith('text/html'):
                first_html_item_path = item_output_path

        return first_html_item_path

    def __str__(self):
        result = f'{self.__class__.__name__}('
        if self.subject:
            result += f'subject: {self.subject!r}\n'
        if self.snapshot_content_location:
            result += f'snapshot_content_location: {self.snapshot_content_location!r}\n'
        if self.content_type:
            if self.content_type.params:
                result += f'content_type: "{self.content_type.value}; …"\n'
            else:
                result += f'content_type: {self.content_type.value!r}\n'
        result = result.replace('\n', '; ')
        result += 'content_items: ' + ', '.join(repr(item) for item in self.content_items)
        result += ')'
        return result

    def __repr__(self):
        return self.__str__()

    @classmethod
    def read_file(cls, path: pathlib.Path) -> 'MhtmlContainer':
        content_items = tuple(cls.read_file_content_items(path))
        assert content_items

        first_item = content_items[0]
        container_headers = MhtmlContainerHeaders(first_item._headers)
        if not first_item.body:
            content_items = content_items[1:]
            assert content_items

        return cls(container_headers, content_items)

    @staticmethod
    def read_file_content_items(path: pathlib.Path) -> Iterable[MhtmlContentItem]:
        default_charset = 'utf-8'
        detected_charset: Optional[str] = None
        detected_content_transfer_encoding: Optional[str] = None
        detected_multipart_section_boundary: Optional[str] = None

        with path.open('rb') as file:
            first_section = True
            charset_to_use = encodings.normalize_encoding(detected_charset or default_charset)

            while True:
                header_bytes = read_mhtml_header_chunk(file, encoding=charset_to_use)
                if not header_bytes and first_section:
                    raise ValueError('No file header found')
                if not header_bytes:
                    break
                headers = parse_mhtml_header_chunk(header_bytes)
                header_bytes = None

                if 'Content-Type' in headers:
                    content_type_params = ContentType.from_str(headers['Content-Type']).params
                    if content_type_params.charset:
                        charset_to_use = encodings.normalize_encoding(content_type_params.charset)
                    if content_type_params.boundary:
                        detected_multipart_section_boundary = content_type_params.boundary
                if 'Content-Transfer-Encoding' in headers:
                    detected_content_transfer_encoding = headers['Content-Transfer-Encoding']

                skip_mhtml_blank_lines(file, encoding=charset_to_use, limit=2 if first_section else 1)

                body_bytes = read_mhtml_body_chunk(
                    file,
                    multipart_section_boundary=detected_multipart_section_boundary,
                    encoding=charset_to_use
                )

                body: Optional[Union[str, bytes]] = None
                if body_bytes:
                    body = parse_mhtml_body_chunk(
                        body_bytes,
                        charset=charset_to_use,
                        content_transfer_encoding=detected_content_transfer_encoding
                    )
                    body_bytes = None

                yield MhtmlContentItem(headers, body)

                boundary_found = skip_mhtml_section_boundary_line(
                    file,
                    multipart_section_boundary=detected_multipart_section_boundary,
                    encoding=charset_to_use
                )

                if not boundary_found:
                    break

                first_section = False
                headers = {}
                body = None
