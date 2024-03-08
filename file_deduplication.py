import os
import hashlib
import json

# Function to calculate MD5 checksum of a file
def calculate_md5(file_path):
    with open(file_path, 'rb') as f:
        md5 = hashlib.md5()
        while chunk := f.read(8192):
            md5.update(chunk)
        return md5.hexdigest()

# Function to build a map of file paths and their MD5 checksums
def build_file_map(directory):
    file_map = {}
    for root, _, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            md5 = calculate_md5(file_path)
            file_map[file_path] = md5
    return file_map

# Function to load file map from a JSON file
def load_file_map(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    else:
        return {}

# Function to save file map to a JSON file
def save_file_map(file_map, file_path):
    with open(file_path, 'w') as f:
        json.dump(file_map, f, indent=4)

# Main function
def main(directory, map_file):
    # Load existing file map or create an empty one
    file_map = load_file_map(map_file)
    
    # If the directory has not been scanned before, build the file map
    if directory not in file_map:
        file_map[directory] = build_file_map(directory)
        save_file_map(file_map, map_file)
    else:
        print("Directory already scanned. Skipping...")

    # Example: Print file paths and their MD5 checksums
    for file_path, md5 in file_map[directory].items():
        print(f"File: {file_path}, MD5: {md5}")

if __name__ == "__main__":
    directory_to_scan = "/path/to/directory"
    file_map_file = "file_map.json"
    main(directory_to_scan, file_map_file)
