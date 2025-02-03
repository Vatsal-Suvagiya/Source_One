import os
import re

# We will replace ANY reference to https://themes.pixelwars.org
# (with or without /logistica/demo-01) using the same "depth" logic.
BASE_REGEX = r"https://themes\.pixelwars\.org(?:/logistica/demo-01)?"

# Dictionary mapping folder depth → the relative path prefix
REPLACEMENT_MAP = {
    1: "../",      # 1 folder deep
    2: "../../",
    3: "../../../",
    4: "../../../../"
}

def get_folder_depth(base_path, current_folder):
    """
    Returns how many levels 'current_folder' is below 'base_path'.
    If current_folder == base_path => 0
    If there's 1 slash => 2, etc.
    We add +1 so that 'demo-01\\service' => depth=1, etc.
    """
    relative_path = os.path.relpath(current_folder, base_path)
    if relative_path == ".":
        return 0
    return relative_path.count(os.sep) + 1

def process_html_file(file_path, depth):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Decide how many "../" for this depth
    replacement = REPLACEMENT_MAP.get(depth, "../" * depth)

    # Regex:
    #   1) https://themes.pixelwars.org
    #   2) optionally /logistica/demo-01
    #   3) capture everything that follows (group(1)) up to " ' < whitespace
    pattern = re.compile(BASE_REGEX + r'([^"\'<\s]*)', re.IGNORECASE)

    def replacer(match):
        after = match.group(1)  # e.g. "/wp-content/uploads..." or "" if nothing
        return replacement + after

    updated_content = pattern.sub(replacer, content)

    # --------------------------------------------------------------------
    # Final Step: Remove accidental double-slashes in the result,
    # but don't break "https://" or "http://".
    # This regex says: replace 2+ slashes not preceded by ':' with a single slash.
    # --------------------------------------------------------------------
    updated_content = re.sub(r'(?<!:)//+', '/', updated_content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"[OK] Updated {file_path} (depth={depth}) - replaced domain with '{replacement}'")

def update_index_files(root_directory):
    for root, dirs, files in os.walk(root_directory):
        for file_name in files:
            if file_name.lower() == "index.html":
                file_path = os.path.join(root, file_name)
                depth = get_folder_depth(root_directory, root)
                process_html_file(file_path, depth)

if __name__ == "__main__":
    # Change this to the path of your local "demo-01" folder
    root_folder = r"E:\logistica\New\downloaded_files\themes.pixelwars.org\logistica\demo-01"
    update_index_files(root_folder)
