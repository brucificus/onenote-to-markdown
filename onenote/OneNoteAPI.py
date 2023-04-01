import base64
from xml.etree import ElementTree

from win32com import client as win32

from onenote.HierarchyScope import HierarchyScope
from onenote.PageInfo import PageInfo
from onenote.PublishFormat import PublishFormat
from onenote.XMLSchema import XMLSchema
from onenote.retry_com import retry_com
from onenote_export.Pathlike import Pathlike


class OneNoteAPI:
    def __init__(self, app: win32.CDispatch = None):
        self._app = app if app is not None else self._create_onenote_com_object()

    @staticmethod
    def _create_onenote_com_object() -> win32.CDispatch:
        return win32.gencache.EnsureDispatch("OneNote.Application.12")

    @retry_com
    def get_hierarchy(self, node_id: str, hierarchy_scope: HierarchyScope, schema: XMLSchema = XMLSchema.xs2013) -> ElementTree:
        """
        Gets the notebook node hierarchy structure, starting from the node you specify (all notebooks or a single notebook,
         section group, or section), and extending downward to all descendants at the level you specify.
        See: https://learn.microsoft.com/en-us/office/client-developer/onenote/application-interface-onenote#gethierarchy-method
        :param node_id: The node (notebook, section group, or section) whose descendants you want. If you pass a null string
        (""), the method gets all nodes below the root node (that is, all notebooks, section groups, and sections). If you
        specify a notebook, section group, or section node, the method gets only descendants of that node.
        :param hierarchy_scope: The lowest descendant node level you want. For example, if you specify pages, the method gets
        all nodes as far down as the page level. If you specify sections, the method gets only section nodes below the
        notebook. For more information, see the HierarchyScope enumeration in the Enumerations topic.
        :param schema: The version of the OneNote XML schema, of type XMLSchema, that you want to be output. You can specify
        whether you want XML Schema version 2013, 2010, 2007, or the current version. NOTE: We recommend specifying a version
        of OneNote (such as xs2013) instead of using xsCurrent or leaving it blank, because this will allow your add-in to work
        with future versions of OneNote.
        :return: ElementTree
        """
        result_text = self._app.GetHierarchy(node_id, hierarchy_scope.value, schema.value)
        return ElementTree.fromstring(result_text)

    @retry_com
    def publish(self, page_id: str, target_file_path: Pathlike, publish_format: PublishFormat, clsid_of_exporter: str = ""):
        """
        Exports the page you specify to a file in any format that OneNote supports.
        See: https://learn.microsoft.com/en-us/office/client-developer/onenote/application-interface-onenote#publish-method
        :param page_id: The OneNote ID of the hierarchy you want to export.
        :param target_file_path: The absolute path to the location where you want to save the resulting output file. The file
        you specify must be one that does not already exist at that location.
        :param publish_format: One of the PublishFormat enumeration values that specifies the format in which you want the
        published page to be (for example, MHTML, PDF, and so on).
        :param clsid_of_exporter: The class ID (CLSID) of a registered COM application that can export Microsoft Windows
        enhanced metafiles (.emf). The COM application must implement the IMsoDocExporter interface. This parameter is included
        to permit third-party developers to write their own code to publish OneNote content in a custom format. For more
        information about the IMsoDocExporter interface, see Extending the Office 2007 Fixed-Format Export Feature.
        :return: None
        """
        self._app.Publish(page_id, str(target_file_path), publish_format.value, clsid_of_exporter)

    @retry_com
    def get_page_content(self, page_id: str, page_info: PageInfo, schema: XMLSchema) -> ElementTree:
        """
        Gets all of the content (in OneNote XML format) of the specified page.
        See: https://learn.microsoft.com/en-us/office/client-developer/onenote/application-interface-onenote#getpagecontent-method
        :param page_id: The OneNote ID of the page whose content you want to get.
        :param page_info: Specifies whether the GetPageContent method returns binary content, embedded in the XML code and
        base-64 encoded. Binary content can include, for example, images and ink data. The pageInfoToExport parameter also
        specifies whether to mark up the selection in the XML code that the GetPageContent method returns. It takes an
        enumerated value from the PageInfo enumeration.
        :param schema: The version of the OneNote XML schema, of type XMLSchema, that you want to be output. You can specify
        whether you want XML Schema version 2013, 2010, 2007, or the current version. NOTE: We recommend specifying a version
        of OneNote (such as xs2013) instead of using xsCurrent or leaving it blank, because this will allow your add-in to work
        with future versions of OneNote.
        :return: ElementTree
        """
        result_text = self._app.GetPageContent(page_id, page_info.value, schema.value)
        return ElementTree.fromstring(result_text)

    @retry_com
    def get_binary_page_content(self, page_id: str, callback_id: str) -> bytes:
        """
        Returns a binary object, such as ink or images, on an OneNote page.
        See: https://learn.microsoft.com/en-us/office/client-developer/onenote/application-interface-onenote#getbinarypagecontent-method
        :param page_id: The OneNote ID of the page that contains the binary object to get.
        :param callback_id: The OneNote ID of the binary object you want to get. This ID, known as a callbackID, is in the
        OneNote XML code for a page returned by the GetPageContent method.
        :return: bytes
        """
        result_bytes_as_base64 = self._app.GetBinaryPageContent(page_id, callback_id)
        result_bytes = base64.b64decode(result_bytes_as_base64)
        return result_bytes
