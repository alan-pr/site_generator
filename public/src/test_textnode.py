import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_if_url(self):
        node = TextNode("Go to my website", TextType.LINK, "www.mywebsite.com")
        self.assertTrue(node.url is not None)

    def test_if_bold(self):
        node = TextNode("Bold text", TextType.BOLD)
        self.assertTrue(node.text_type is TextType.BOLD)


if __name__ == "__main__":
    unittest.main()