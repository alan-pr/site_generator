from textnode import TextType


class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        props = ""
        if self.props is not None:
            for key, value in self.props.items():
                props += f" {key}=\"{value}\""
        return props

    def show_children(self):
        return list(map(lambda child: child.tag, self.children))

    def __repr__(self):
        return f"tag: {self.tag}\nvalue: {self.value}\nchildren: {self.show_children()}\nprops: {self.props_to_html()}"

class LeafNode(HTMLNode):
    def __init__(self, tag=None, value=None, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.value is None:
            raise ValueError("HTML leaf node needs a value")
        if self.tag is None:
            return f"{self.value}"
        return f"<{self.tag}>{self.props_to_html()}{self.value}</{self.tag}>"

class ParentNode(HTMLNode):
    def __init__(self, tag=None, children=None, props=None):
        super().__init__(tag, None, children, props)
    def to_html(self):
        if self.tag is None:
            raise ValueError("HTML parent node needs a tag")
        if self.children is None:
            raise ValueError("HTML parent node needs children")
        return f"<{self.tag}>{''.join(list(map(lambda child: child.to_html(), self.children)))}</{self.tag}>"

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text, None)
        case TextType.BOLD:
            return LeafNode("b", text_node.text, None)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text, None)
        case TextType.CODE:
            return LeafNode("code", text_node.text, None)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", "", {"src": text_node.url, "alt": None})
        case _:
            raise Exception("Unknown HTML tag type")