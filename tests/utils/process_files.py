import os

def process_files(directory_path):
    if not os.path.exists(directory_path):
        return []

    if not os.path.isdir(directory_path):
        raise ValueError(f"Path '{directory_path}' is not a directory.")

    compatible_files = []
    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        if os.path.isfile(filepath):
            extension = filename.split('.')[-1].lower() if '.' in filename else ""
            if extension in ['png', 'jpg', 'jpeg', 'gif', 'mp3']:
                compatible_files.append(filepath)

    return compatible_files