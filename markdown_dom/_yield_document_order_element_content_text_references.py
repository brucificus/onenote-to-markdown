from typing import Iterable, Type, Tuple, Union

from markdown_dom.read_content_text_from import *
from markdown_dom.AbstractElementContentTextReference import AbstractElementContentTextReference
from markdown_dom.ElementContentTextReference import ElementContentTextReference
from markdown_dom.type_variables import normalize_elementlike, PanfluteElementLike


_ElementStackItem = Union[panflute.Element, Tuple[panflute.Element, AbstractElementContentTextReference]]


def _yield_document_order_element_content_text_references(
    source: PanfluteElementLike,
    *,
    synthetic_para_break_type: Optional[Type[panflute.Element]] = panflute.LineBreak,
    synthetic_text_linkage_break_text: Optional[str] = '\u200c',  # Zero-width non-joiner.
) -> Iterable[AbstractElementContentTextReference]:
    iteration_stack: Tuple[_ElementStackItem, ...] = normalize_elementlike(source)

    def create_synthetic_para_break(para: panflute.Para) -> Optional[_ElementStackItem]:
        if synthetic_para_break_type is None:
            return None
        synthetic_element = synthetic_para_break_type()
        content_text_reference = ElementContentTextReference(
            synthetic_element,
            get_content_text=lambda _: os.linesep,
            get_content_text_len=lambda _: len(os.linesep),
            delete_content_text_completely=lambda _: None,
        )
        return (synthetic_element, content_text_reference)

    def create_synthetic_text_linkage_break() -> Optional[_ElementStackItem]:
        if not synthetic_text_linkage_break_text:
            return None
        synthetic_element = panflute.Str(synthetic_text_linkage_break_text)
        content_text_reference = ElementContentTextReference(
            synthetic_element,
            get_content_text=read_content_text_from_Str,
            get_content_text_len=len_content_text_from_Str,
        )
        return (synthetic_element, content_text_reference)

    while len(iteration_stack) > 0:
        element = iteration_stack[0]
        iteration_stack = iteration_stack[1:]

        if isinstance(element, Tuple) \
            and len(element) == 2 \
            and isinstance(element[0], panflute.Element) \
            and isinstance(element[1], AbstractElementContentTextReference):
            yield element[1]
        elif isinstance(element, panflute.Doc):
            e: panflute.Doc = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Space):
            e: panflute.Space = element
            yield ElementContentTextReference(e,
                                              read_content_text_from_Space,
                                              len_content_text_from_Space,
                                              delete_content_text_completely=commit_element_suicide,
                                              )
        elif isinstance(element, panflute.HorizontalRule):
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            pass  # No text or child elements at this element.
        elif isinstance(element, panflute.SoftBreak):
            e: panflute.SoftBreak = element
            yield ElementContentTextReference(e,
                                              read_content_text_from_SoftBreak,
                                              len_content_text_from_SoftBreak,
                                              delete_content_text_completely=commit_element_suicide,
                                              )
        elif isinstance(element, panflute.LineBreak):
            e: panflute.LineBreak = element
            yield ElementContentTextReference(e,
                                              read_content_text_from_LineBreak,
                                              len_content_text_from_LineBreak,
                                              delete_content_text_completely=commit_element_suicide,
                                              )
        elif isinstance(element, panflute.Plain):
            e: panflute.Plain = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Para):
            e: panflute.Para = element
            if not synthetic_para_break_type:
                iteration_stack = tuple(e.content) + iteration_stack
            else:
                iteration_stack = tuple(e.content) + (create_synthetic_para_break(e),) + iteration_stack
        elif isinstance(element, panflute.BlockQuote):
            e: panflute.BlockQuote = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Emph):
            e: panflute.Emph = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Strong):
            e: panflute.Strong = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Underline):
            e: panflute.Underline = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Strikeout):
            e: panflute.Strikeout = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Superscript):
            e: panflute.Superscript = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Subscript):
            e: panflute.Subscript = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.SmallCaps):
            e: panflute.SmallCaps = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Note):
            e: panflute.Note = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Header):
            e: panflute.Header = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Div):
            e: panflute.Div = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Span):
            e: panflute.Span = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Quoted):
            e: panflute.Quoted = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Cite):
            e: panflute.Cite = element
            iteration_stack = tuple(e.content) + iteration_stack
            iteration_stack = tuple(e.citations) + iteration_stack
        elif isinstance(element, panflute.Citation):
            e: panflute.Citation = element
            iteration_stack = tuple(e.prefix) + iteration_stack
            iteration_stack = tuple(e.content) + iteration_stack
            iteration_stack = tuple(e.suffix) + iteration_stack
        elif isinstance(element, panflute.Link):
            e: panflute.Link = element
            yield ElementContentTextReference(e,
                                              read_content_text_from_Link,
                                              len_content_text_from_Link,
                                              set_content_text_to_Link,
                                              )
            if e.url is not None:
                if synthetic_text_linkage_break_text:
                    iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Image):
            e: panflute.Image = element
            yield ElementContentTextReference(e,
                                              read_content_text_from_Image,
                                              len_content_text_from_Image,
                                              set_content_text_to_Image,
                                              )
            if e.url is not None:
                if synthetic_text_linkage_break_text:
                    iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Str):
            e: panflute.Str = element
            yield ElementContentTextReference(e,
                                              read_content_text_from_Str,
                                              len_content_text_from_Str,
                                              set_content_text_to_Str,
                                              delete_content_text_completely=commit_element_suicide,
                                              )
        elif isinstance(element, panflute.CodeBlock):
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            pass  # No text or child elements at this element.
        elif isinstance(element, panflute.RawBlock):
            e: panflute.RawBlock = element
            yield ElementContentTextReference(e,
                                              read_content_text_from_RawBlock,
                                              len_content_text_from_RawBlock,
                                              set_content_text_to_RawBlock,
                                              delete_content_text_completely=commit_element_suicide,
                                              )
        elif isinstance(element, panflute.Code):
            e: panflute.Code = element
            yield ElementContentTextReference(e,
                                              read_content_text_from_Code,
                                              len_content_text_from_Code,
                                              set_content_text_to_Code,
                                              delete_content_text_completely=commit_element_suicide,
                                              )
        elif isinstance(element, panflute.Math):
            e: panflute.Math = element
            yield ElementContentTextReference(e,
                                              read_content_text_from_Math,
                                              len_content_text_from_Math,
                                              set_content_text_to_Math,
                                              delete_content_text_completely=commit_element_suicide,
                                              )
        elif isinstance(element, panflute.RawInline):
            e: panflute.RawInline = element
            yield ElementContentTextReference(e,
                                              read_content_text_from_RawInline,
                                              len_content_text_from_RawInline,
                                              set_content_text_to_RawInline,
                                              delete_content_text_completely=commit_element_suicide,
                                              )
        elif isinstance(element, panflute.ListItem):
            e: panflute.ListItem = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.BulletList):
            e: panflute.BulletList = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.OrderedList):
            e: panflute.OrderedList = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Definition):
            e: panflute.Definition = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.DefinitionItem):
            e: panflute.DefinitionItem = element
            iteration_stack = tuple(e.term) + iteration_stack
            iteration_stack = tuple(e.content) + iteration_stack
            iteration_stack = tuple(e.definitions) + iteration_stack
        elif isinstance(element, panflute.DefinitionList):
            e: panflute.DefinitionList = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.LineItem):
            e: panflute.LineItem = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.LineBlock):
            e: panflute.LineBlock = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Figure):
            e: panflute.Figure = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.MetaList):
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            pass  # No text or child elements at this element.
        elif isinstance(element, panflute.MetaMap):
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            pass  # No text or child elements at this element.
        elif isinstance(element, panflute.MetaInlines):
            e: panflute.MetaInlines = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.MetaBlocks):
            e: panflute.MetaBlocks = element
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.MetaString):
            e: panflute.MetaString = element
            yield ElementContentTextReference(e,
                                              read_content_text_from_MetaString,
                                              len_content_text_from_MetaString,
                                              set_content_text_to_MetaString,
                                              delete_content_text_completely=commit_element_suicide,
                                              )
        elif isinstance(element, panflute.MetaBool):
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            pass  # No text or child elements at this element.
        elif isinstance(element, panflute.Caption):
            e: panflute.Caption = element
            iteration_stack = (e.short_caption,) + iteration_stack
            iteration_stack = tuple(e.content) + iteration_stack
        elif isinstance(element, panflute.Table):
            e: panflute.Table = element
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            iteration_stack = (e.head,) + iteration_stack
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            iteration_stack = tuple(e.content) + iteration_stack
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            iteration_stack = (e.foot,) + iteration_stack
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            iteration_stack = (e.caption,) + iteration_stack
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
        elif isinstance(element, panflute.TableBody):
            e: panflute.TableBody = element
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            iteration_stack = tuple(e.head) + iteration_stack
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            iteration_stack = tuple(e.content) + iteration_stack
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
        elif isinstance(element, panflute.TableCell):
            e: panflute.TableCell = element
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            iteration_stack = tuple(e.content) + iteration_stack
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
        elif isinstance(element, panflute.TableFoot):
            e: panflute.TableFoot = element
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            iteration_stack = tuple(e.content) + iteration_stack
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            assert not e.content
        elif isinstance(element, panflute.TableHead):
            e: panflute.TableHead = element
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            iteration_stack = tuple(e.content) + iteration_stack
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            assert not e.content
        elif isinstance(element, panflute.TableRow):
            e: panflute.TableRow = element
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
            iteration_stack = tuple(e.content) + iteration_stack
            if synthetic_text_linkage_break_text:
                iteration_stack = (create_synthetic_text_linkage_break(),) + iteration_stack
        elif element is None:
            pass
        else:
            raise NotImplementedError('Unknown element type: ' + str(type(element)))
