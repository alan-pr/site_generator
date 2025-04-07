import re


def convert_to_html(text):
    return parse(text)

def parse(text):
    split_text = split_into_lines(text)
    formatted_text = retrieve_headers(split_text)
    formatted_text = retrieve_code_blocks(formatted_text)
    formatted_text = join_code_blocks(formatted_text)
    formatted_text = retrieve_quote_blocks(formatted_text)
    formatted_text = join_quote_blocks(formatted_text)
    formatted_text = retrieve_unordered_list(formatted_text)
    formatted_text = retrieve_ordered_list(formatted_text)
    formatted_text = join_unordered_list_blocks(formatted_text)
    formatted_text = join_ordered_list_blocks(formatted_text)
    formatted_text = retrieve_paragraphs(formatted_text)
    formatted_text = format_newlines_from_paragraphs(formatted_text)
    formatted_text = retrieve_links(formatted_text)
    formatted_text = retrieve_images(formatted_text)
    formatted_text = retrieve_bold_text(formatted_text)
    formatted_text = retrieve_italic_text(formatted_text)
    formatted_text = retrieve_inline_code_text(formatted_text)
    return "".join(formatted_text)


def split_into_lines(text):
    return text.split("\n")


def retrieve_headers(text, line_number=0):
    lines = text.copy()
    line = lines[line_number]
    header = re.match(r"^(#{1,6})\s+(.*)$", line)
    if header:
        lines[line_number] = f"<h{len(header.group(1))}>{header.group(2)}</h{len(header.group(1))}>"
    line_number += 1
    if line_number == len(text):
        return lines
    return retrieve_headers(lines, line_number)


def retrieve_code_blocks(text, text_copy=None, line_number=0, first_delimiter_found=False):
    if text_copy is None:
        lines = text.copy()
    else:
        lines = text_copy
    line = lines[line_number]

    if first_delimiter_found:
        if re.match(r"^```$", line):
            lines[line_number] = "</code></pre>"
            return retrieve_code_blocks(lines)
        else:
            lines[line_number] = line
    else:
        if re.match(r"^```$", line):
            first_delimiter_found = True
            lines[line_number] = "<pre><code>"
    line_number += 1
    if line_number == len(text):
        return text
    return retrieve_code_blocks(text, lines, line_number, first_delimiter_found)


def retrieve_quote_blocks(text, line_number=0, delimiter_found=False):
    lines = text.copy()
    line = lines[line_number]
    if delimiter_found:
        if line == "":
            lines[line_number - 1] += "</blockquote>"
            return retrieve_quote_blocks(lines)
        lines[line_number] = line.lstrip(">").lstrip()
    else:
        quote = re.match(r"^>(.*)$", line)
        if quote:
            delimiter_found = True
            lines[line_number] = f"<blockquote>{quote.group(1).lstrip()}"
    line_number += 1
    if line_number == len(text):
        if delimiter_found:
            lines[line_number - 1] += "</blockquote>"
        return lines
    return retrieve_quote_blocks(lines, line_number, delimiter_found)


def retrieve_unordered_list(text, line_number=0, delimiter_found=False, last_item_index=0):
    lines = text.copy()
    line = lines[line_number]
    if delimiter_found:
        if line == "":
            lines[line_number - 1] += "</ul>"
            return retrieve_unordered_list(lines)
        list_content = re.match(r"(^-\s)(.*?)$", line)
        if list_content:
            lines[line_number] = f"<li>{list_content.group(2)}</li>"
            last_item_index = line_number
        else:
            lines[last_item_index] = lines[last_item_index].replace("</li>", "")
            lines[line_number] = f" {line}</li>"
            last_item_index = line_number
    else:
        list_content = re.match(r"(^-\s)(.*?)$", line)
        if list_content:
            delimiter_found = True
            last_item_index = line_number
            line = "<ul><li>" + list_content.group(2) + "</li>"
            lines[line_number] = line
    line_number += 1
    if line_number == len(text):
        lines[line_number - 1] += "</ul>"
        return lines
    return retrieve_unordered_list(lines, line_number, delimiter_found, last_item_index)


def retrieve_ordered_list(text, line_number=0, delimiter_found=False, last_item_index=0):
    lines = text.copy()
    line = lines[line_number]
    if delimiter_found:
        if line == "":
            lines[line_number - 1] += "</ol>"
            return retrieve_ordered_list(lines)
        list_content = re.match(r"^(?:(\d{1,9}|[a-zA-Z]|[ivxlcdmIVXLCDM]{1,5})[.)]\s+)?(.*)", line)
        if list_content:
            lines[line_number] = f"<li>{list_content.group(2).lstrip(". ")}</li>"
            last_item_index = line_number
        else:
            lines[last_item_index] = lines[last_item_index].replace("</li>", "")
            lines[line_number] = f" {line}</li>"
            last_item_index = line_number
    else:
        list_content = re.match(r"^((?:\d{1,9}|[a-zA-Z]|[ivxlcdmIVXLCDM]{1,5}))[.)]\s+(.*)", line)
        if list_content:
            delimiter_found = True
            number = list_content.group(1)
            content = list_content.group(2)
            last_item_index = line_number
            list_type = get_ordered_list_type(number)
            line = f"<ol type=\"{list_type}\" start=\"{number}\"><li>" + content + "</li>"
            lines[line_number] = line
    line_number += 1
    if line_number == len(text):
        lines[line_number - 1] += "</ul>"
        return lines
    return retrieve_ordered_list(lines, line_number, delimiter_found, last_item_index)


def get_ordered_list_type(first_item_number):
    if re.match(r"\d", first_item_number):
        return "1"
    elif re.match(r"[a-h]", first_item_number):
        return "a"
    elif re.match(r"[A-H]", first_item_number):
        return "A"
    elif re.match(r"[ivxlcdm]", first_item_number):
        return "i"
    elif re.match(r"[IVXLCDM]", first_item_number):
        return "I"


def retrieve_paragraphs(text, line_number=0, is_paragraph=False):
    lines = text.copy()
    line = lines[line_number]
    tags = ("<pre>", "<h1>", "<h2>", "<h3>", "<h4>", "<h5>", "<h6>", "<blockquote>", "<ul>", "<ol>", "<li>")
    found = False
    for tag in tags:
        if tag in line:
            found = True
            break
    if found and is_paragraph:
        lines[line_number - 1] += "</p>"
        return retrieve_paragraphs(lines, line_number, False)
    if not found and not is_paragraph and line != "":
        lines[line_number] = "<p>" + line
        is_paragraph = True
    line_number += 1
    if line_number == len(text):
        if is_paragraph:
            lines[line_number - 1] += "</p>"
        return lines
    return retrieve_paragraphs(lines, line_number, is_paragraph)


def join_code_blocks(lines, line_number=0, first_index=0, first_line_found=False):
    if first_line_found:
        if lines[line_number] == "</code></pre>":
            start = first_index
            end = line_number
            line = lines[start] + "<br>".join(lines[start + 1:end]) + lines[end]
            new_lines = lines.copy()
            new_lines[start] = line
            if end < len(lines):
                new_lines[start + 1:] = lines[end + 1:]
            return join_code_blocks(new_lines)
    else:
        if lines[line_number] == "<pre><code>":
            first_line_found = True
            first_index = line_number
    line_number += 1
    if line_number == len(lines):
        return lines
    return join_code_blocks(lines, line_number, first_index, first_line_found)


def join_quote_blocks(lines, line_number=0, first_index=0, first_line_found=False):
    if first_line_found:
        if "</blockquote>" in lines[line_number]:
            start = first_index
            end = line_number
            line = "<br>".join(lines[start:end + 1])
            new_lines = lines.copy()
            new_lines[start] = line
            if end < len(lines):
                new_lines[start + 1:] = lines[end + 1:]
            return join_quote_blocks(new_lines)
    else:
        if "<blockquote>" in lines[line_number]:
            first_line_found = True
            first_index = line_number
    line_number += 1
    if line_number == len(lines):
        return lines
    return join_quote_blocks(lines, line_number, first_index, first_line_found)


def join_unordered_list_blocks(lines, line_number=0, first_index=0, first_line_found=False):
    if first_line_found:
        if "</ul>" in lines[line_number]:
            start = first_index
            end = line_number
            line = "".join(lines[start:end + 1])
            new_lines = lines.copy()
            new_lines[start] = line
            if end < len(lines):
                new_lines[start + 1:] = lines[end + 1:]
            return join_unordered_list_blocks(new_lines)
    else:
        if "<ul>" in lines[line_number]:
            first_line_found = True
            first_index = line_number
    line_number += 1
    if line_number == len(lines):
        return lines
    return join_unordered_list_blocks(lines, line_number, first_index, first_line_found)


def join_ordered_list_blocks(lines, line_number=0, first_index=0, first_line_found=False):
    if first_line_found:
        if "</ol>" in lines[line_number]:
            start = first_index
            end = line_number
            line = "".join(lines[start:end + 1])
            new_lines = lines.copy()
            new_lines[start] = line
            if end < len(lines):
                new_lines[start + 1:] = lines[end + 1:]
            return join_unordered_list_blocks(new_lines)
    else:
        if "<ol>" in lines[line_number]:
            first_line_found = True
            first_index = line_number
    line_number += 1
    if line_number == len(lines):
        return lines
    return join_unordered_list_blocks(lines, line_number, first_index, first_line_found)


def retrieve_links(text, line_number=0):
    lines = text.copy()
    line = lines[line_number]
    links = list(re.finditer(r"(?<!!)\[(.*?)\]\((.*?)\)", line))
    if links:
        for link in links:
            anchor_text = link.group(1)
            hyper_text = link.group(2)
            start = link.start()
            end = link.end()
            lines[line_number] = f"{line[:start]}<a href=\"{hyper_text}\">{anchor_text}</a>{line[end:]}"
        return retrieve_links(lines)
    line_number += 1
    if line_number == len(text):
        return lines
    return retrieve_links(lines, line_number)


def retrieve_images(text, line_number=0):
    lines = text.copy()
    line = lines[line_number]
    links = list(re.finditer(r"!\[(.*?)\]\((.*?)\)", line))
    if links:
        for link in links:
            alt_text = link.group(1)
            source = link.group(2)
            start = link.start()
            end = link.end()
            lines[line_number] = f"{line[:start]}<img src=\"{source}\" alt=\"{alt_text}\">{line[end:]}"
        return retrieve_images(lines)
    line_number += 1
    if line_number == len(text):
        return lines
    return retrieve_images(lines, line_number)


def retrieve_delimiter_text(text, line_number, regex_pattern, tag):
    lines = text.copy()
    if line_number == len(text):
        return lines
    line = text[line_number]
    matches = list(re.finditer(regex_pattern, line))
    count = len(matches)
    if matches and count > 1:
        if count == 3:
            line = add_tags_outer(line, regex_pattern, tag)
        else:
            line = add_tags(line, regex_pattern, tag)
    lines[line_number] = line
    line_number += 1
    return retrieve_delimiter_text(lines, line_number, regex_pattern, tag)


def add_tags(text, regex_pattern, tag):
    line = re.sub(regex_pattern, f"<{tag}>", text, count=1)
    line = re.sub(regex_pattern, f"</{tag}>", line, count=1)
    matches = list(re.finditer(regex_pattern, line))
    if matches:
        return add_tags(line, regex_pattern, tag)
    return line


def add_tags_outer(text, regex_pattern, tag):
    matches = list(re.finditer(regex_pattern, text))
    line = re.sub(regex_pattern, f"<{tag}>", text, count=1)
    reversed_line = line[::-1]
    reversed_line = re.sub(regex_pattern, f">{tag[::-1]}/<", reversed_line, count=1)
    line = reversed_line[::-1]
    if matches:
        return add_tags_outer(line, regex_pattern, tag)
    return line


def retrieve_bold_text(text, line_number=0):
    return retrieve_delimiter_text(text, line_number, r"(?<!\*)\*\*(?!\*)", "b")


def retrieve_italic_text(text, line_number=0):
    return retrieve_delimiter_text(text, line_number, r"(?<!_)_(?!_)", "i")


def retrieve_inline_code_text(text, line_number=0):
    return retrieve_delimiter_text(text, line_number, r"(?<!`)`(?!`)", "code")


def format_newlines_from_paragraphs(text, line_number=0, paragraph_found=False, paragraph_done=False, start_index=0, end_index=0):
    lines = text.copy()
    if line_number >= len(text):
        return lines
    line = lines[line_number]
    if paragraph_found and "</p>" in line:
        end_index = line_number
        paragraph_done = True
    elif "<p>" in line and "</p>" not in line:
        paragraph_found = True
        start_index = line_number
    if paragraph_done:
        paragraph = "<br>".join(lines[start_index:end_index + 1])
        lines = lines[:start_index] + [paragraph] + lines[end_index + 1:]
        return format_newlines_from_paragraphs(lines)
    line_number += 1
    if line_number == len(text):
        return lines
    return format_newlines_from_paragraphs(lines, line_number, paragraph_found, paragraph_done, start_index, end_index)
