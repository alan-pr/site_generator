import os
from generator import copy_and_paste_dir_content, generate_page, generate_page_recursive


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_path = os.path.join(base_dir, "../static")
    public_path = os.path.join(base_dir, "../public")
    copy_and_paste_dir_content(static_path, public_path)
    # generate_page("content/index.md", "template.html", "public")
    generate_page_recursive("content", "template.html", "public")

main()