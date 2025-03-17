import unittest

from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node


class TestHTMLNode(unittest.TestCase):
    def setUp(self):
        self.node = LeafNode(None, "this is a text")
    @unittest.skip("")
    def test_to_html(self):
        self.assertRaises(NotImplementedError, self.node.to_html)
    @unittest.skip("")
    def test_props_to_html(self):
        self.assertEqual(self.node.props_to_html(), " href=\"www.google.com\" target=\"_blank\"")
    @unittest.skip("")
    def test_leaf_to_html_p(self):
        self.assertEqual(self.node.to_html(), "<p>Hello, world!</p>")
    @unittest.skip("")
    def test_leaf_to_html_a(self):
        self.assertEqual(self.node.to_html(), "<a href=\"www.google.com\" target=\"_blank\">Google</a>")
    @unittest.skip("")
    def test_leaf_node_no_value(self):
        self.assertRaises(ValueError, self.node.to_html)
    @unittest.skip("")
    def test_leaf_node_no_tag(self):
        self.assertIsInstance(self.node.to_html(), str)

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_no_children(self):
        parent_node = ParentNode("div", [])
        self.assertEqual(parent_node.to_html(), "<div></div>")

    def test_to_html_with_children_none(self):
        parent_node = ParentNode("div", None)
        with self.assertRaises(ValueError) as context:
            parent_node.to_html()
        self.assertEqual(str(context.exception), "HTML parent node needs children")

    def test_parent_node_to_html_with_no_tag(self):
        child_node = LeafNode("b", "bold text")
        parent_node = ParentNode(None, [child_node])
        with self.assertRaises(ValueError) as context:
            parent_node.to_html()
        self.assertEqual(str(context.exception), "HTML parent node needs a tag")

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold_text(self):
        node = TextNode("This is a bold text node", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is a bold text node")

    def test_italic_text(self):
        node = TextNode("This is a italic text node", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is a italic text node")

    def test_code_text(self):
        node = TextNode("This is a code text node", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "This is a code text node")

    def test_link(self):
        node = TextNode("This is a link node", TextType.LINK, "www.google.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "This is a link node")
        self.assertEqual(html_node.props, {"href": "www.google.com"})

    def test_image(self):
        node = TextNode("", TextType.IMAGE, "/images")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": "/images", "alt": None})


if __name__ == "__main__":
    unittest.main()