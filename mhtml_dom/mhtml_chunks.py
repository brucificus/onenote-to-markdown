import base64
import encodings
import logging
from typing import Optional, IO, Dict, Union

from mhtml_dom.ReversibleLineReaderContext import ReversibleLineReaderContext
from mhtml_dom.ContentType import ContentType
from mhtml_dom.quoted_printable import decode_quoted_printable_bytes, decode_quoted_printable_text


def read_mhtml_header_chunk(
    file: IO[bytes],
    encoding: str,
    *,
    logger = logging.getLogger(__name__ + '.read_mhtml_header_chunk')
) -> Optional[bytes]:
    newlines = {'\r\n', '\n', '\r'}

    def is_newline(line: str) -> bool:
        return line in newlines

    with ReversibleLineReaderContext(file, encoding) as reader:
        while True:
            line = reader.readline()

            if line == '':  # EOF.
                logger.debug('Reached: EOF.')
                break
            if is_newline(line):
                logger.debug('Reached: blank line.')
                break

            reader.commit_advancement()

        lines_read_count = len(reader.committed_lines_read) if reader.committed_lines_read else None
        file_read_start_position = reader.file_starting_position
        file_read_amount = reader.committed_bytes_read_count if lines_read_count else None

    logger.debug('Scanned ' + str(lines_read_count) + ' lines.')

    if not file_read_amount:
        logger.debug('No header found, aborting.')
        return None

    logger.debug(f'Header found, reading {file_read_amount} bytes-ish.')
    file.seek(file_read_start_position)
    return file.read(file_read_amount)


def skip_mhtml_blank_lines(
    file: IO[bytes],
    encoding: str,
    limit: Optional[int] = None,
    *,
    logger = logging.getLogger(__name__ + '.skip_mhtml_blank_lines')
) -> Optional[int]:
    newlines = {'\r\n', '\n', '\r'}

    def is_newline(line: str) -> bool:
        return line in newlines

    with ReversibleLineReaderContext(file, encoding) as reader:
        while True:
            reader.commit_advancement()
            lines_skipped = len(reader.committed_lines_read)

            if limit is not None and lines_skipped is not None and lines_skipped >= limit:
                logger.debug('Reached: limit.')
                break

            line = reader.readline()
            if is_newline(line):
                logger.debug('Skipping: blank line.')
                continue

            logger.debug('Reached: ' + ('EOF' if line == '' else 'line with content') + '.')
            break

        logger.debug('Scanned ' + str(lines_skipped) + ' lines.')

        if not lines_skipped:
            logger.debug('No blank lines found, aborting.')
            return None

        logger.debug('Found blank lines, skipping.')
        return lines_skipped


def read_mhtml_body_chunk(
    file: IO[bytes],
    multipart_section_boundary: str,
    encoding: str,
    *,
    logger = logging.getLogger(__name__ + '.read_mhtml_body_chunk')
) -> Optional[bytes]:
    with ReversibleLineReaderContext(file, encoding) as reader:
        while True:
            line = reader.readline()
            if line == '':  # EOF.
                logger.debug('Reached: EOF.')
                break
            if multipart_section_boundary and line.find(multipart_section_boundary) != -1:
                logger.debug('Reached: multipart section boundary.')
                break
            reader.commit_advancement()

        lines_read_count = len(reader.committed_lines_read) if reader.committed_lines_read else None
        file_read_start = reader.file_starting_position
        file_read_amount = reader.committed_bytes_read_count if lines_read_count else None

    logger.debug(f'Scanned {lines_read_count} lines, consisting of {file_read_amount} bytes-ish.')

    if not file_read_amount:
        logger.debug('No body chunk found, aborting.')
        return None

    logger.debug(f'Body chunk found, reading {file_read_amount} bytes-ish.')
    file.seek(file_read_start)
    return file.read(file_read_amount)


def skip_mhtml_section_boundary_line(
    file: IO[bytes],
    multipart_section_boundary: str,
    encoding: str,
    *,
    logger = logging.getLogger(__name__ + '.skip_mhtml_section_boundary_line')
) -> bool:
    with ReversibleLineReaderContext(file, encoding) as reader:
        line = reader.readline()
        if line == '':  # EOF.
            logger.debug('Reached: EOF.')
        elif line.strip().find(multipart_section_boundary) != -1:
            logger.debug('Reached: multipart section boundary.')
            reader.commit_advancement()
        else:
            logger.warning('Unexpected line: ' + repr(line))

        lines_read_count = len(reader.committed_lines_read) if reader.committed_lines_read else None

    logger.debug(f'Scanned {lines_read_count} lines.')

    if not lines_read_count:
        logger.debug('No section boundary line found, aborting.')
        return False

    logger.debug('Section boundary line found, skipping.')
    return True


def parse_mhtml_header_chunk(
    header_chunk: bytes,
    charset: Optional[str] = None,
    content_transfer_encoding: Optional[str] = None,
    reparse_on_charset_change: bool = True,
    reparse_on_content_transfer_encoding_change: bool = True,
    *,
    logger = logging.getLogger(__name__ + '.parse_mhtml_header_chunk')
) -> Dict[str, str]:
    charset_to_use = encodings.normalize_encoding(charset or 'utf-8')
    content_transfer_encoding_to_use = content_transfer_encoding or 'quoted-printable'

    lines = header_chunk.decode('utf-8').splitlines()
    headers = {}
    should_escape_quoted_printable = content_transfer_encoding is None or content_transfer_encoding == 'quoted-printable'

    current_key = None
    current_value = None

    for line in lines:
        if line == '':
            raise ValueError('Empty line in header chunk')

        line_starts_with_tab = line.startswith('\t')
        line_ends_with_quoted_printable_escape = line.strip().endswith('=')
        line_contains_colon = ':' in line
        continuing_previous_line = current_key is not None and not line_contains_colon and line_starts_with_tab

        if not continuing_previous_line and line_starts_with_tab:
            raise ValueError('Line starts with tab but no key is set')

        if continuing_previous_line:
            if line_starts_with_tab:
                current_value += line[1:]
            else:
                current_value += line
            if should_escape_quoted_printable and line_ends_with_quoted_printable_escape:
                current_value = current_value[:-1]
            continue

        if line_contains_colon:
            if current_key is not None:
                if should_escape_quoted_printable:
                    current_key = decode_quoted_printable_text(current_key, is_multiline=False, possibly_contains_newlines=False)
                    current_value = decode_quoted_printable_text(current_value, is_multiline=False, possibly_contains_newlines=False)
                if current_value.startswith(' '):
                    current_value = current_value[1:]
                headers[current_key] = current_value
            current_key, current_value = line.split(':', 1)
            if should_escape_quoted_printable and line_ends_with_quoted_printable_escape:
                current_value = current_value[:-1]
            continue

        raise ValueError('Unexpected line in header chunk: ' + repr(line))

    if current_key is not None:
        if should_escape_quoted_printable:
            current_key = decode_quoted_printable_text(current_key, is_multiline=False, possibly_contains_newlines=False)
            current_value = decode_quoted_printable_text(current_value, is_multiline=False, possibly_contains_newlines=False)
        if current_value.startswith(' '):
            current_value = current_value[1:]
        headers[current_key] = current_value

    if reparse_on_charset_change or reparse_on_content_transfer_encoding_change:

        found_charset = None
        if 'Content-Type' in headers:
            content_type_params = ContentType.from_str(headers['Content-Type']).params
            if content_type_params.charset:
                found_charset = content_type_params.charset
        found_content_transfer_encoding = None
        if 'Content-Transfer-Encoding' in headers:
            found_content_transfer_encoding = headers['Content-Transfer-Encoding']

        if found_charset is not None and encodings.normalize_encoding(found_charset) != charset_to_use:
            logger.debug('Found novel charset: ' + repr(found_charset))
            should_restart_because_charset = reparse_on_charset_change
        else:
            should_restart_because_charset = False

        if found_content_transfer_encoding is not None and found_content_transfer_encoding != content_transfer_encoding_to_use:
            logger.debug('Found novel Content-Transfer-Encoding: ' + repr(found_content_transfer_encoding))
            should_restart_because_content_transfer_encoding = reparse_on_content_transfer_encoding_change
        else:
            should_restart_because_content_transfer_encoding = False

        if should_restart_because_charset or should_restart_because_content_transfer_encoding:
            logger.debug('Restarting header parsing with parameter changes.')
            return parse_mhtml_header_chunk(
                header_chunk,
                charset=found_charset,
                content_transfer_encoding=found_content_transfer_encoding,
                reparse_on_charset_change=found_charset is None and reparse_on_charset_change,
                reparse_on_content_transfer_encoding_change=found_content_transfer_encoding is None and reparse_on_content_transfer_encoding_change,
            )

    logger.debug('Parsed headers: ' + repr(headers))
    return headers


def parse_mhtml_body_chunk(
    body_chunk: bytes,
    charset: Optional[str] = None,
    content_transfer_encoding: Optional[str] = None,
    *,
    logger = logging.getLogger(__name__ + '.parse_mhtml_body_chunk')
) -> Union[str, bytes]:
    content_transfer_encoding_to_use = content_transfer_encoding or 'quoted-printable'
    charset_to_use = encodings.normalize_encoding(charset or 'utf-8')

    if content_transfer_encoding_to_use == 'quoted-printable':
        logger.debug('Decoding quoted-printable body chunk.')
        body_chunk = decode_quoted_printable_bytes(body_chunk, is_multiline=True, possibly_contains_newlines=True)
        return body_chunk.decode(charset_to_use)
    if content_transfer_encoding_to_use == 'base64':
        logger.debug('Decoding base64 body chunk.')
        return base64.b64decode(body_chunk)
    logger.debug('Unknown content transfer encoding: ' + repr(content_transfer_encoding_to_use) + ', raising exception.')
    raise ValueError(f"Unknown content transfer encoding: {content_transfer_encoding_to_use}")
