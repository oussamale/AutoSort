import os

def resolve_duplicate(destination_path):
    """
    If file exists, append (1), (2), ... before extension.
    Example: file.pdf → file (1).pdf
    """
    if not os.path.exists(destination_path):
        return destination_path  # No duplicates

    base, ext = os.path.splitext(destination_path)
    counter = 1

    new_path = f"{base} ({counter}){ext}"
    while os.path.exists(new_path):
        counter += 1
        new_path = f"{base} ({counter}){ext}"

    return new_path


def validate_directory(path):
    if not os.path.exists(path):
        return False, "The folder does not exist."

    if not os.access(path, os.W_OK):
        return False, "You do not have permission to write in this folder."

    # Check if directory is writable by creating a temp file
    try:
        test_file = os.path.join(path, ".__write_test.tmp")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
    except Exception:
        return False, "The folder is not writable."

    return True, ""
