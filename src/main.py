from sys import argv
from generator import copy_and_paste_dir_content, generate_page, generate_page_recursive


def main():
    # base_dir = os.path.dirname(os.path.abspath(__file__))
    # from_path = os.path.join(base_dir, "../static")
    # to_path = os.path.join(base_dir, "../public")
    if len(argv) > 1:
        basepath = argv[1]
    else:
        basepath = ""
    from_path = "static"
    to_path = "docs"
    copy_and_paste_dir_content(from_path, to_path)
    generate_page_recursive("content", "template.html", to_path, basepath)

main()