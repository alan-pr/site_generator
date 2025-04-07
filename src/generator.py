import os
import shutil
from pathlib import Path
from parser import convert_to_html


def scan_dir(dir_path):
    return os.listdir(dir_path)


def delete_dir_content(dir_path, show_log=True):
    files_deleted_count = 0
    directories_deleted_count = 0
    for item in scan_dir(dir_path):
        if os.path.isfile(f"{dir_path}/{item}"):
            os.remove(f"{dir_path}/{item}")
            files_deleted_count += 1
            if show_log:
                print(f"{item} file deleted.")
        elif os.path.isdir(f"{dir_path}/{item}"):
            shutil.rmtree(f"{dir_path}/{item}")
            directories_deleted_count += 1
            if show_log:
                print(f"{item} directory and all its subdirectories were deleted.")
    if show_log:
        print("================================================================================")
        print(f"{files_deleted_count} files deleted.")
        print(f"{directories_deleted_count} directories deleted.")
        print()


def copy_dir_content(path, skip_item=None):
    if skip_item is None:
        skip_item = []
    items = []
    content = scan_dir(path)
    for item in content:
        if item in skip_item:
            continue
        skip_item.append(item)
        if os.path.isfile(f"{path}/{item}"):
            items.append({"file": item})
        elif os.path.isdir(f"{path}/{item}"):
            items.append({"directory": item, "content": copy_dir_content(f"{path}/{item}", skip_item)})
    return {"path": path, "content": items}


def paste_content(destination_path, pasted_content):
    from_path = pasted_content["path"]
    content = pasted_content["content"]
    for item in content:
        if "file" in item.keys():
            try:
                shutil.copy(f"{from_path}/{item["file"]}", f"{destination_path}/{item["file"]}")
                print(f"{item["file"]} file was copied from {from_path} to {destination_path}\n")
            except shutil.SameFileError:
                pass
        if "directory" in item.keys():
            sub_destination_path = f"{destination_path}/{item["directory"]}"
            if not os.path.exists(sub_destination_path):
                os.mkdir(sub_destination_path)
                print(f"{item["directory"]} directory was copied from {from_path} to {destination_path}\n")
            paste_content(sub_destination_path, item["content"])


def copy_and_paste_dir_content(from_path, to_path):
    delete_dir_content(to_path)
    content = copy_dir_content(from_path)
    paste_content(to_path, content)


def extract_title(markdown):
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
                return line.lstrip("#").strip(" ")


def generate_page(from_path, template_path, dest_path):
    # with open(from_path) as markdown_file:
    #     markdown_content = markdown_file.read()
    # with open(template_path) as template_file:
    #     template_content = template_file.read()
    markdown_content = from_path.read_text()
    template_content = Path(template_path).read_text()
    # print(f"[X] {dest_path}")

    print(f"Generating page from {from_path} to {dest_path} using {template_path}...")

    title = extract_title(markdown_content)
    html_content = convert_to_html(markdown_content)
    new_page = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)

    Path(f"{dest_path}/index.html").write_text(new_page)


def generate_page_recursive(dir_path_content, template_path, dest_dir_path):
    path = Path(dir_path_content)
    for subdir in path.iterdir():
        if subdir.is_dir():
            dir_name = f"{str(subdir).replace("content", dest_dir_path)}"
            Path(dir_name).mkdir()
            generate_page_recursive(subdir, template_path, dest_dir_path)
    for subdir in path.iterdir():
        if subdir.is_file() and subdir.name == "index.md":
            dest_path = f"{dest_dir_path}/{"/".join(str(dir_path_content).split("/")[1:])}"
            generate_page(subdir, template_path, dest_path)