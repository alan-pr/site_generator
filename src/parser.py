from sys import argv
from enum import Enum
import re


# Types Enum
class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


# Constants
TEXT_FORMATS = [TextType.TEXT, TextType.BOLD, TextType.ITALIC, TextType.CODE]
LINK_REGEX = r"(?<!\!)\[(.*?)\]\((.*?)\)"
IMAGE_REGEX = r"!\[(.*?)\]\((.*?)\)"
HEADING_REGEX = r"^(\#{1,6})\s(.*)"
CODE_BLOCK_REGEX = r'(?m)(?s)^(```)[ \t]*\n(.*?)\n(```)[ \t]*(?=\n|$)'
QUOTE_REGEX = f"^(>)(.*)"
CODE_BLOCK_SYMBOL = "```"


# Static Functions
def main():
    if not argv:
        return
    if len(argv) == 2:
        markdown_file = argv[1]
        return parse_markdown(markdown_file)
    if len(argv) < 2 or not argv[1].startswith('-') or argv[1].count('-') != 1:
        return
    flags = argv[1][1:].split()
    if 'r' not in flags:
        return
    try:
        print(convert_to_html(argv[2]))
    except IndexError:
        print("Raw HTML code must be provided.")


def convert_to_html(text):
    return parse(text)


def parse(text):
    html_text = parse_block_types(text)
    while True:
        text_type = get_foremost_symbol(html_text)
        if text_type in TEXT_FORMATS[1:]:
            html_text = parse_delimiter(html_text, text_type)
        elif text_type is TextType.LINK or text_type is TextType.IMAGE:
            html_text = parse_link_and_image_texts(html_text)
        elif text_type is TextType.TEXT:
            # html_text = split_multiline_plain_text(html_text)
            break
    return html_text


def parse_delimiter(text, text_type):
    delimiter = get_text_type_symbol(text_type)
    paragraphs = text.split("\n\n")
    html_paragraphs = []

    for paragraph in paragraphs:
        if text.count(delimiter) > 1:
            if text.count(delimiter) % 2 == 0:
                html_text = split_text_delimiter(paragraph, delimiter, text_type)
            else:
                html_text = split_text_outer_delimiter(paragraph, delimiter, text_type)
        else:
            html_text = text
        # html_text = add_paragraph_tags(html_text)
        html_paragraphs.append(html_text.replace("\n", ' '))
    return ''.join(html_paragraphs)


def split_text_delimiter(text, delimiter, text_type):
    start = text.find(delimiter)
    end = text.find(delimiter, start + len(delimiter))

    if start == -1 or end == -1:
        return text
    tag = get_tag(text_type)
    before = text[:start]
    middle = text[start + len(delimiter):end]
    after = text[end + len(delimiter):]

    return f"{before}<{tag}>{middle}</{tag}>{after}"


def split_text_outer_delimiter(text, delimiter, text_type):
    start = text.find(delimiter)
    end = text.rfind(delimiter)

    if start == -1 or end == -1 or start == end:
        return text
    tag = get_tag(text_type)
    before = text[:start]
    middle = text[start + len(delimiter):end]
    after = text[end + len(delimiter):]

    return f"{before}<{tag}>{middle}</{tag}>{after}"


def split_multiline_plain_text(text):
    html_lines = []
    if text.count("\n\n") > 0:
        paragraphs = text.split("\n\n")
        html_text = ""
        for paragraph in paragraphs:
            html_text = parse_plain_text(paragraph)
            html_lines.append(html_text)
        return ''.join(html_lines)
    return parse_plain_text(text)


def split_in_two_text_delimiter(delimiter, text):
    if delimiter in text:
        delimiter_index = text.find(delimiter)
        return text[:delimiter_index], text[delimiter_index:].lstrip(delimiter)
    return text


def split_header_line(text):
    if "\n" in text:
        split_text = text.split("\n")
        return split_text[0], "\n".join(split_text[1:])
    return text, None


def split_code_block(block):
    block_split = block.split("```")
    block_split[1] = block_split[1][1:-1].replace("\n", "<br>")
    new_block = "```".join(block_split)
    new_block = add_code_block_tags(new_block)

    if is_valid_code_block(new_block):
        return split_code_block(new_block)
    return new_block


# def parse_plain_text(text):
#     return add_paragraph_tags(text).replace('\n', ' ')


def is_valid_code_block(block):
    count = 0
    for text in block.split("\n"):
        if re.search(CODE_BLOCK_REGEX, text):
            count += 1
        if count == 2:
            return True
    return False


def parse_link_and_image_texts(text):
    html_text = text
    if is_markdown_link_present(text):
        links = extract_markdown_links(text)
        for link in links:
            formatted_link = f"<a href=\"{link[1]}\">{link[0]}</a>"
            html_text = re.sub(LINK_REGEX, formatted_link, html_text, count=1)
    else:
        images = extract_markdown_images(text)
        for image in images:
            formatted_image = f"<img src=\"{image[1]}\" alt=\"{image[0]}\">"
            html_text = re.sub(IMAGE_REGEX, formatted_image, html_text, count=1)
    return html_text


def parse_block_text(text):
    blocks = split_code_block(text)
    blocks = re.split(r"\n{2,}", blocks)
    new_blocks = []
    code_block_text_access = False
    quote_block_access = False
    for block in blocks:
        heading = re.findall(HEADING_REGEX, block)
        code_block = is_valid_code_block(block)
        quote = re.findall(QUOTE_REGEX, block)
        if heading:
            formatted_block = format_header(block, heading)
            new_blocks.extend(formatted_block)
        if code_block_text_access and not code_block:
            formatted_text = add_code_block_tags(block)
            new_blocks.append(formatted_text)
        if code_block:
            split_code_block(block)
        if not quote and quote_block_access:
            formatted_text = block
            if "\n" in block:
                formatted_text = add_closing_quote_tag(block)
                try:
                    formatted_text, after_text = split_in_two_text_delimiter("</blockquote>", formatted_text)
                    formatted_text += "</blockquote>" + parse_block_text(after_text.lstrip("\n"))
                except ValueError:
                    pass
            formatted_text = add_closing_quote_tag(formatted_text)
            new_blocks.append(formatted_text)
        if quote:
            quote_block_access = True
            formatted_text = add_opening_quote_tag(block)
            new_blocks.append(formatted_text)
        if not heading and not code_block and not code_block_text_access and not quote and not quote_block_access:
            new_blocks.append(block)
    return "\n".join(new_blocks)


def format_header(block, heading):
    size = len(heading[0][0])
    new_block = []
    header, new_parag = split_header_line(block)
    new_block.append(add_header_tags(size, header))

    if new_parag is not None:
        new_block.append(parse_block_text(new_parag))

    return new_block


def add_paragraph_tags(text):
    if text[:3] == "<p>" and text[-4:] == "</p>":
        return text
    return "<p>" + text + "</p>"


def add_header_tags(size, text):
    if size not in range(1, 7):
        raise ValueError("Header sizes should be from 1 to 6.")
    return f"<h{size}>{text.replace('#', '', size).lstrip()}</h{size}>"


def add_code_block_tags(text):
    return f"<pre><code>{text.lstrip('```').rstrip('```')}</code></pre>"


def add_opening_quote_tag(text):
    return f"<blockquote>{text.replace('>', '', 1)}"


def add_closing_quote_tag(text):
    end_index = text.find("\n")
    return f"{text[:end_index]}</blockquote>{text[end_index:]}"


def get_foremost_symbol(text):
    foremost_text_type = None
    foremost_index = float("inf")

    for text_type in list(TextType):
        if text_type in [TextType.TEXT, TextType.LINK, TextType.IMAGE]:
            continue
        if text.count(get_text_type_symbol(text_type)) < 2:
            continue
        if text_type in TEXT_FORMATS[1:]:
            symbol = get_text_type_symbol(text_type)
            current_index = text.find(symbol)
            if 0 <= current_index < foremost_index:
                foremost_index = current_index
                foremost_text_type = text_type
    if foremost_text_type is None:
        return get_non_format_text(text)
    return foremost_text_type


def get_non_format_text(text):
    if is_markdown_link_present(text):
        return TextType.LINK
    if is_markdown_image_present(text):
        return TextType.IMAGE
    return TextType.TEXT


def get_text_type_symbol(text_type):
    match text_type:
        case TextType.BOLD:
            return "**"
        case TextType.ITALIC:
            return "_"
        case TextType.CODE:
            return "```"
        case _:
            raise ValueError(f"Unknown text type: {text_type}")


def get_tag(text_type):
    match text_type:
        case TextType.BOLD:
            return "b"
        case TextType.ITALIC:
            return "i"
        case TextType.CODE:
            return "code"


def extract_markdown_images(text):
    return re.findall(IMAGE_REGEX, text)


def extract_markdown_links(text):
    return re.findall(LINK_REGEX, text)


def is_markdown_link_present(text):
    return re.search(LINK_REGEX, text) is not None


def is_markdown_image_present(text):
    return re.search(IMAGE_REGEX, text) is not None


def parse_block_types(text):
    code_block = format_code_block(text, CODE_BLOCK_SYMBOL)
    header_block = format_header_blocks(code_block)
    quote_block = format_quote_block(header_block)
    unordered_list = format_unordered_list(quote_block)
    ordered_list = format_ordered_list(unordered_list)
    paragraphs = format_paragraph(ordered_list)
    return paragraphs


def retrieve_code_blocks(text, delimiter, block=None, pointer_index=0, first_delimiter_found=False):
    if block is None:
        block = {}
    delimiter_size = len(delimiter)

    if pointer_index + delimiter_size > len(text):
        if "start" in block and "end" not in block:
            return None
        return block if "start" in block and "end" in block else None

    if text[pointer_index:pointer_index + delimiter_size] == delimiter:
        if not first_delimiter_found:
            if pointer_index + delimiter_size < len(text):
                if text[pointer_index + delimiter_size] == "\n":
                    first_delimiter_found = True
                    block.update({"content": "", "start": pointer_index})
        else:
            if text[pointer_index - 1] == "\n":
                block["end"] = pointer_index
                return block
        pointer_index += delimiter_size - 1
    else:
        if first_delimiter_found:
            block["content"] += text[pointer_index]

    return retrieve_code_blocks(text, delimiter, block, pointer_index + 1, first_delimiter_found)


def format_code_block(text, delimiter="```"):
    code_block = retrieve_code_blocks(text, delimiter)
    if code_block:
        start = code_block["start"]
        end = code_block["end"]
        content = code_block["content"]

        size = len(delimiter)
        formatted = f"{text[:start]}<pre><code>{content.strip().replace('\n', '<br>')}</code></pre>{text[end + size:]}"
        return format_code_block(formatted, delimiter)
    else:
        return text


def retrieve_headers(text, pointer_index=0, block=None, first_delimiter_found=False, first_whitespace_found=False):
    if block is None:
        block = {}
    if pointer_index == len(text):
        if first_delimiter_found:
            block["end"] = pointer_index
            return block
        return block
    if first_delimiter_found:
        if first_whitespace_found and text[pointer_index] != "\n":
            block["content"] += text[pointer_index]
        else:
            if text[pointer_index] == "#":
                block["size"] += 1
            elif text[pointer_index] == " ":
                first_whitespace_found = True
        if text[pointer_index] == "\n":
            block["end"] = pointer_index
            return block
    else:
        if text[pointer_index] == "#" and (pointer_index == 0 or text[pointer_index - 1] == "\n"):
            first_delimiter_found = True
            block.update({"content": "", "start": pointer_index, "end": pointer_index, "size": 1})
    pointer_index += 1
    return retrieve_headers(text, pointer_index, block, first_delimiter_found, first_whitespace_found)


def format_header_blocks(block):
    header = retrieve_headers(block)
    if header:
        content = header["content"]
        start = header["start"]
        end = header["end"]
        size = header["size"]
        formatted_headers = f"{block[:start]}<h{size}>{content}</h{size}>{block[end:]}"
        return format_header_blocks(formatted_headers)
    else:
        return block


def retrieve_quote_block(text, pointer_index=0, block=None, delimiter_found=False, newline_found=False):
    if block is None:
        block = {}
    if pointer_index == len(text):
        if delimiter_found:
            block["end"] = pointer_index
        return block
    if delimiter_found:
        if text[pointer_index] == "\n":
            if newline_found:
                block["end"] = pointer_index
                return block
            newline_found = True
        else:
            newline_found = False
        block["content"] += text[pointer_index]
    else:
        if text[pointer_index] == ">" and (pointer_index == 0 or text[pointer_index - 1] == "\n"):
            delimiter_found = True
            block.update({"content": "", "start": pointer_index, "end": pointer_index})
    pointer_index += 1
    return retrieve_quote_block(text, pointer_index, block, delimiter_found, newline_found)


def format_quote_block(block):
    quote_block = retrieve_quote_block(block)
    if quote_block:
        content = quote_block["content"]
        start = quote_block["start"]
        end = quote_block["end"]
        formatted_quote_block = f"{block[:start]}<blockquote>{content.replace('\n', '<br>')}</blockquote>{block[end:]}"
        return format_quote_block(formatted_quote_block)
    else:
        return block


def retrieve_unordered_list(text, pointer_index=0, items=None, delimiter_found=False, whitespace_found=False, newline_found=False):
    if items is None:
        items = {"list": [], "start": pointer_index, "end": pointer_index}
    if pointer_index == len(text):
        if delimiter_found:
            items["end"] = pointer_index
        return items
    if delimiter_found:
        if whitespace_found:
            if text[pointer_index] == "\n":
                if newline_found:
                    return items
                newline_found = True
                if pointer_index + 1 < len(text):
                    if text[pointer_index + 1] == "-":
                        delimiter_found = False
                    else:
                        items["list"][-1]["content"] += " "
                items["list"][-1]["content"] += text[pointer_index]
                items["end"] = pointer_index
            else:
                items["list"][-1]["content"] += text[pointer_index]
                newline_found = False
        else:
            if text[pointer_index] == " ":
                whitespace_found = True
            else:
                return items
    else:
        if text[pointer_index] == "-" and (pointer_index == 0 or text[pointer_index - 1] == "\n"):
            delimiter_found = True
            if not items["list"]:
                items["start"] = pointer_index
            items["list"].append({"content": ""})
    pointer_index += 1
    return retrieve_unordered_list(text, pointer_index, items, delimiter_found, whitespace_found, newline_found)


def format_unordered_list(block):
    unordered_list = retrieve_unordered_list(block)
    if unordered_list["list"]:
        formatted_unordered_list = ""
        start = unordered_list["start"]
        end = unordered_list["end"]
        for item in unordered_list["list"]:
            content = item["content"]
            formatted_unordered_list += f"<li>{content.replace('\n', '').lstrip().strip()}</li>"
        return f"{block[:start]}<ul>{formatted_unordered_list}</ul>{block[end:]}"
    else:
        return block


def retrieve_ordered_list(text, pointer_index=0, items=None, first_digit_found=False, roman_number_found=False, period_found=False, whitespace_found=False, newline_found=False):
    if items is None:
        items = {"list": [], "type": "1", "count_start": "", "start": pointer_index, "end": pointer_index}
    if pointer_index == len(text):
        items["end"] = pointer_index
        return items
    if first_digit_found:
        char = text[pointer_index]
        if period_found:
            if whitespace_found:
                if char == "\n":
                    if newline_found:
                        items["end"] = pointer_index
                        return items
                    else:
                        items["end"] = pointer_index
                        newline_found = True
                        return retrieve_ordered_list(text, pointer_index, items, newline_found=newline_found)
                else:
                    items["list"][-1] += char
            else:
                if char == " ":
                    whitespace_found = True
                    items["list"].append("")
        else:
            if char == ".":
                period_found = True
        if roman_number_found:
            if period_found:
                pass
            else:
                items["count_start"] += char
    else:
        char = text[pointer_index]
        if pointer_index == 0 or text[pointer_index - 1] == "\n":
            if re.match(r"\d", char):
                first_digit_found = True
                if not items["list"]:
                    items["count_start"] = char
                    items["start"] = pointer_index
            elif char in ["a", "A"]:
                first_digit_found = True
                if not items["list"]:
                    items["type"] = char
                    items["count_start"] = "1"
                    items["start"] = pointer_index
            elif char in ["i", "I"]:
                first_digit_found = True
                roman_number_found = True
                if not items["list"]:
                    items["type"] = char
                    items["start"] = pointer_index
            elif char == ".":
                first_digit_found = True
                period_found = True
                if not items["list"]:
                    items["start"] = pointer_index
    pointer_index += 1
    return retrieve_ordered_list(text, pointer_index, items, first_digit_found, roman_number_found, period_found, whitespace_found, newline_found)


def format_ordered_list(block):
    ordered_list = retrieve_ordered_list(block)
    if ordered_list["list"]:
        formatted_ordered_list = ""
        start = ordered_list["start"]
        end = ordered_list["end"]
        for item_content in ordered_list["list"]:
            formatted_ordered_list += f"<li>{item_content}</li>"
        formatted_ordered_list = f"{block[:start]}<ol type=\"{ordered_list['type']}\" start=\"{ordered_list['count_start']}\">{formatted_ordered_list}</ol>{block[end:]}"
        return format_ordered_list(formatted_ordered_list)
    else:
        return block


def format_paragraph(blocks):
    tags = ("<pre>", "<blockquote>", "<ol", "<ul>", "<h1>", "<h2>", "<h3>", "<h4>", "<h5>", "<h6>")
    split_block = blocks.split("\n")
    new_blocks = []
    for block in split_block:
        found = False
        for tag in tags:
            if tag in block:
                found = True
                break
        if block != "":
            if not found:
                new_blocks.append(f"<p>{block}</p>")
            else:
                new_blocks.append(block)
    return "".join(new_blocks)


def parse_markdown(markdown_file):
    with open(markdown_file) as file:
        markdown_text = file.read()
    return convert_to_html(markdown_text)


# print(main())
with open("markdown_page.md") as f:
    text = f.read()
print(convert_to_html(text))
