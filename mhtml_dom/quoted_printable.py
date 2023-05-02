import logging
import re


quoted_printable_substitution_pattern = re.compile(r'=(?P<code>[0-9A-F]{2})')


def replace_matched_quoted_printable_substitution(match: re.Match) -> str:
    return chr(int(match.group('code'), 16))


def decode_quoted_printable_text(text: str, is_multiline: bool = True, possibly_contains_newlines: bool = True) -> str:
    if is_multiline and not possibly_contains_newlines:
        raise ValueError('is_multiline=True and possibly_contains_newlines=False are mutually exclusive')

    if is_multiline:
        text_lines = text.splitlines(keepends=True)
        text_lines = tuple(decode_quoted_printable_text(line, is_multiline=False, possibly_contains_newlines=True) for line in text_lines)
        return ''.join(text_lines)

    keep_escaped_newlines = False
    keep_unescaped_newlines = True

    if possibly_contains_newlines:
        text_rstripped = text.rstrip()
        newline_len = len(text) - len(text_rstripped)

        if text_rstripped.endswith('='):
            if keep_escaped_newlines:
                text = text_rstripped[:-1] + text[-newline_len:]
            else:
                text = text_rstripped[:-1]
        else:
            if keep_unescaped_newlines:
                pass
            else:
                text = text_rstripped

    text = re.sub(quoted_printable_substitution_pattern, replace_matched_quoted_printable_substitution, text)
    return text


_text_decode_methods = (
    ('ascii', None),
    ('ascii', 'surrogateescape'),
    ('utf-8', None),
    ('utf-8', 'surrogateescape'),
)

_text_reencode_methods = (
    ('ascii', None),
    ('ascii', 'surrogateescape'),
    ('utf-8', None),
    ('utf-8', 'surrogateescape'),
)


def decode_quoted_printable_bytes(
    text_as_bytes: bytes,
    is_multiline: bool = True,
    possibly_contains_newlines: bool = True,
    *,
    logger: logging.Logger = logging.getLogger(__name__ + '.decode_quoted_printable_bytes'),
) -> bytes:
    text: str = None
    for i, (decode_encoder, decode_errors) in enumerate(_text_decode_methods):
        try:
            if decode_errors:
                text = text_as_bytes.decode(decode_encoder, errors=decode_errors)
            else:
                text = text_as_bytes.decode(decode_encoder)
            break
        except UnicodeDecodeError as e:
            if i == len(_text_decode_methods) - 1:
                logger.error('Failed to decode quoted-printable text as bytes: %r', text_as_bytes, exc_info=True)
                raise
            logger.debug('Failed to decode quoted-printable text as bytes using %r.', (decode_encoder, decode_errors), exc_info=True)
            continue

    text = decode_quoted_printable_text(text, is_multiline=is_multiline, possibly_contains_newlines=possibly_contains_newlines)

    for i, (reencode_encoder, reencode_errors) in enumerate(_text_reencode_methods):
        try:
            if reencode_errors:
                return text.encode(reencode_encoder, errors=reencode_errors)
            return text.encode(reencode_encoder)
        except UnicodeEncodeError as e:
            if i == len(_text_reencode_methods) - 1:
                logger.error('Failed to re-encode quoted-printable text: %r', text, exc_info=True)
                raise
            logger.debug('Failed to re-encode quoted-printable text using %r.', (reencode_encoder, reencode_errors), exc_info=True)
            continue
