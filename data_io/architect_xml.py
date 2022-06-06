# coding: utf-8
import xml.etree.ElementTree as ET

from architect import DB, DbTable, TableColumn


class ExNodeNotFound(Exception):
    """
    Raised when a node is not found.
    """

    def __init__(self, request, src):
        """
        :param request: XPath request sent
        :type request: str
        :param src: file
        :type src: str
        """
        self._msg = "No nodes found \nat:'{}'\nin:'{}'".format(request, src)
        self._num = "XmlBrowser001"

    def __str__(self):
        return "{} ExNodeNotFound:{}".format(self._num, self._msg)


class ExAttributeNotFound(Exception):
    """
    Raised when an attribute is not found.
    """

    def __init__(self, attribute_name, node_name, node_content, src, context=None):
        """
        :param attribute_name: attribute name
        :type attribute_name: str
        :param node_name: name of the node containing attribute
        :type node_name: str
        :param node_content: attributes of node **node_name**
        :type node_content: str
        :param src: file
        :type src: str
        :param context: free area describing context of error
        :type context: str
        """
        self._msg = "Attribute '{}' not found\nin:'{}{}'\nat:{}".format(attribute_name, node_name, node_content, src)
        if context is not None:
            self._msg += "\ncontext:'{}'".format(context)
        self._num = "XmlBrowser002"

    def __str__(self):
        return "{} ExAttributeNotFound:{}".format(self._num, self._msg)


class ExAttributeWrongFormat(Exception):
    """
    Raised when an attribute has not good format.
    """

    def __init__(self, attribute_name, node_name, node_content, format, src, context=None):
        """
        :param attribute_name: attribute name
        :type attribute_name: str
        :param node_name: name of the node containing attribute
        :type node_name: str
        :param node_content: attributes of node **node_name**
        :type node_content: str
        :param format: format waited for attribute **attribute_name**
        :type format: free
        :param src: file
        :type src: str
        :param context: free area describing context of error
        :type context: str
        """
        self._msg = "Attribute '{}' must be {}\nin:'{}{}'at:{}".format(attribute_name, format, node_name,
                                                                       node_content, src)
        if context is not None:
            self._msg += "\ncontext:'{}'".format(context)
        self._num = "XmlBrowser003"

    def __str__(self):
        return "{} ExAttributeWrongFormat:{}".format(self._num, self._msg)


class XmlBrowser(ET.ElementTree):
    """Class to navigate easily in a xml via XPath request."""

    def __init__(self, element=None, file=None):
        """
        Initialize xml file parser

        :param element: root element. default None
        :param file: file path to parse. default None
        """
        if element is None:
            element = ET.Element("Root")
        super().__init__(element, file)
        self._src = file

    @property
    def src(self):
        return self._src

    def parse(self, source, parser=None):
        """
        Load external XML document into element tree. Override from base class
        to save file source name

        :param source: file name or file object
        :type source: str or file
        :param parser: is an optional parser instance that defaults to XMLParser.
        :return: the root element of the given source document.

        :except ParseError: raised if the parser fails to parse the document.

        """
        super().parse(source, parser)
        self._src = source

    def add_sub_tree(self, sub_tree, root_node=None, erase_children=False):
        """Append a tree to this tree."""
        if root_node is None:
            root_node = self.getroot()
        if erase_children is True:
            for child in root_node:
                root_node.remove(child)
        root_node.append(sub_tree)

    def get_node(self, nodes, root=None):
        """
        Get all node(s) returned after an xpath request made by assembling all nodes and adding
        them to a root request './'.

        .. note:: XPath request example:

            *'./Nominal/CompleteSection/Meanlines/Meanline'*

            -->This request will return every node named *'Meanline'*.

        :param nodes: nodes name from root (not included) to final node
        :type nodes: iterable
        :param root: root node to use
        :type root: xml.etree.ElementTree.Element
        :return: nodes returned by xpath request
        :rtype: [xml.etree.ElementTree.Element]

        :exception ExNodeNotFound: if no nodes found whit XPath request

        """
        # XPath start point
        if root is None:
            root = self.getroot()

        # Building XPath request
        request = "./" + "/".join(nodes)
        # Sending request
        nodes_found = root.findall(request)
        # request return
        if len(nodes_found) > 0:
            return nodes_found
        else:
            raise ExNodeNotFound(request, self._src) from None

    def add_node(self, nodes_name_list, final_node_attrib=None, root_node=None):
        """
        Add nodes to the current instance.

        example:

        Suppose a CrXml file like below:

        .. code-block:: xml

            <Edges>
              <Identity>
                <Nominal>
                  <PartId>364-068-611</PartId>
                  <Engine>1B</Engine>
                  <CreationDate>2019-03-11 05:40:01</CreationDate>
                  <Issue>B</Issue>
                  <FileName>Edges_364-068-611_B_11032019.xml</FileName>
                </Nominal>
              <Identity>
            <Edges>

        After applying the function:

        .. code-block:: python

            Cr.add_node(["Foo", "Bar"], final_node_attrib={"a": 12})

        CrXml file will look like:

        .. code-block:: xml

            <Edges>
              <Identity>
                <Nominal>
                  <PartId>364-068-611</PartId>
                  <Engine>1B</Engine>
                  <CreationDate>2019-03-11 05:40:01</CreationDate>
                  <Issue>B</Issue>
                  <FileName>Edges_364-068-611_B_11032019.xml</FileName>
                </Nominal>
              </Identity>
              <Foo>
                <Bar a="12"/>
              </Foo>
            </Edges>

        .. note:: If one or more nodes already exists they are not recreated.

        :param nodes_name_list: nodes to add. Each node as a child of the previous nodes.
        :type nodes_name_list: iterable
        :param final_node_attrib: attributes to add to the final node (optional)
        :type final_node_attrib: None or {Name: Value}
        :param root_node: node of instance used as parent for first element of *nodes_name_list*
        :type root_node: None or xml.etree.ElementTree.Element
        """
        if root_node is None:
            root_node = self.getroot()

        for i in range(0, len(nodes_name_list) - 1):
            node_name = str(nodes_name_list[i])
            node = root_node.find(str(node_name))
            if node is None:
                root_node = ET.SubElement(root_node, str(node_name))
            else:
                root_node = node

        if type(final_node_attrib) is dict:
            root_node = ET.SubElement(root_node, str(nodes_name_list[-1]), final_node_attrib)
        else:
            root_node = ET.SubElement(root_node, str(nodes_name_list[-1]))

        return root_node

    def set_heads_tails(self, head="  ", tail="\n"):
        """
        Set instance content for display.

        :param head: node start pattern
        :type head: str
        :param tail: node end pattern
        :type tail: str
        """
        self._set_nodes_head_tail(self.getroot(), 0, head, tail)

    @staticmethod
    def _get_attribute(node, attrib_name, context=None):
        """
        Extract one attribute from a node.

        :param node: node
        :type node: xml.etree.ElementTree.Element
        :param attrib_name: node attribute name
        :type attrib_name: str
        :return: attribute value
        :rtype: str

        :exception ExAttributeNotFound: attribute not found

        """
        try:
            attrib_value = node.attrib[attrib_name]
        except KeyError:
            raise ExAttributeNotFound(attrib_name, node.tag, node.attrib,
                                      context) from None
        else:
            return attrib_value

    def _add_int_to_attribute(self, nodes, attribute, num):
        """
        Add an int number to a numerical attribute.

        :param nodes: nodes name from root (not included) to node containing attributes
        :type nodes: iterable
        :param attribute: attribute name
        :param num: number to add

        :exception ExAttributeWrongFormat:

        """
        nodes_found = self.get_node(nodes)

        for node in nodes_found:
            attribute_value = self._get_attribute(node, attribute, nodes)

            if attribute_value.isnumeric():
                node.attrib[attribute] = str(int(num + int(attribute_value)))
            else:
                raise ExAttributeWrongFormat(attribute, node.tag, node.attrib,
                                             "int", self._src, context=nodes)

    def update_attribute(self, nodes, attribute, new_value):
        """
        Update an attribute value.

        :param nodes: nodes name from root (not included) to node containing attributes
        :type nodes: iterable
        :param attribute: attribute name
        :param new_value: attribute new value
        """
        nodes_found = self.get_node(nodes)
        for node in nodes_found:
            node.attrib[attribute] = str(new_value)

    def get_nodes_at(self, param_name, param_value, nodes, child_node_name=None, root=None):
        """
        Get all node(s) (or sub nodes) contained at attribute param_name
        'param_value' after an xpath.
        request made by:

        1. Assembling all nodes and adding them to root request './'
        2. Then add index attribute request
        3. Finally (if required) add sub_node_name to request

        .. note:: XPath request with child node example (param_name='cr', param_value='CR10'):

            *'./Nominal/CompleteSection/Meanlines/Meanline[@cr='CR10']/Point'*

            --> This request will return every node named *'Point'* at cr *'CR10'*.

        :param param_name: attribute name
        :param param_value: attribute value
        :param nodes: nodes name from root (not included) to final node
        :type nodes: iterable
        :param child_node_name: sub node to extract (optional)
        :type child_node_name: str
        :return: nodes returned by xpath request
        :rtype: [xml.etree.ElementTree.Element]

        :exception ValueError: if no nodes found whit XPath request
        :exception ExNodeNotFound: if no nodes found whit XPath request

        """
        if root is None:
            root = self.getroot()

        # Building XPath request
        request = "./" + "/".join(nodes)
        request += "[@{}='{}']".format(param_name, param_value)
        if child_node_name is not None:
            request += "/{}".format(child_node_name)

        # Sending request
        nodes_found = root.findall(request)

        # request return
        if len(nodes_found) > 0:
            return nodes_found
        else:
            raise ExNodeNotFound(request, self._src) from None

    def _set_nodes_head_tail(self, node, lvl, head, tail):
        """
        Recursive function to set start and end of node text for display.

        .. code-block:: xml

            <Foo value="6">
                <Bar a="12"/>
            </Foo>

        xml.etree.ElementTree.Element allow to change two property :

        - tail: Text after this element's end tag

        - text: Text before first subelement of this element

        By combining head and tail pattern we are able to recursively indent xml file

        :param node: node
        :type node: xml.etree.ElementTree.Element
        :param lvl: number of head pattern to put in front of node
        :param head: text pattern in front of this node
        :param tail: text pattern at the end of a node
        """
        node.tail = tail + head * lvl
        if len(node) > 0:
            lvl += 1
            node.text = tail + head * lvl
            for child in node:
                self._set_nodes_head_tail(child, lvl, head, tail)


def create_table(table_node):
    """Create a DbTable from a power architect Xml node 'architect-project/target-database/table'"""
    table_key = table_node.attrib["id"]
    table_name = table_node.attrib["name"]
    return DbTable(table_key, table_name)


def create_column(column_node):
    """Create a TableColumn from a power architect Xml node 'architect-project/target-database/table/folder/column'"""
    key = column_node.attrib["id"]
    name = column_node.attrib["name"]
    autoincrement = column_node.attrib["autoIncrement"] == "true"
    not_null = column_node.attrib["nullable"] == "0"
    pk = "primaryKeySeq" in column_node.attrib
    column_type = int(column_node.attrib["type"])

    return TableColumn(key, name, autoincrement, pk, column_type, not_null)


def add_relation_in_db(db: DB, table_node, column_node):
    """Create a relation in DB from a power architect Xml node
     'architect-project/target-database/relationships/relationship'"""

    pk_table_key = table_node.attrib["pk-table-ref"]
    fk_table_key = table_node.attrib["fk-table-ref"]

    pk_column_key = column_node.attrib["pk-column-ref"]
    fk_column_key = column_node.attrib["fk-column-ref"]

    db.add_relation(pk_table_key, fk_table_key, pk_column_key, fk_column_key)


def load_from_architect_file(filepath):

    xml_browser = XmlBrowser(file=filepath)
    db = DB()

    tables = xml_browser.get_node(("target-database", "table"))
    for t in tables:
        table = create_table(t)
        db.tables[table.key] = table

        columns = xml_browser.get_node(("folder", "column"), t)
        for c in columns:
            column = create_column(c)
            table.columns[column.key] = column

    relations = xml_browser.get_node(("target-database", "relationships", "relationship"))
    for relation in relations:
        column_mapping = xml_browser.get_node(("column-mapping",), relation)
        add_relation_in_db(db, relation, column_mapping[0])

    return db
