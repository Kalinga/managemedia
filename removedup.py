import os
import hashlib
import json
import signal
import sys
import logging

logging.basicConfig(filename='duplicate_files.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

scanned_directories = set()
duplicate_files = []


def get_file_checksum(file_path):
    # Calculate the checksum of a file
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()


def find_duplicate_files(directory):
    global scanned_directories, duplicate_files

    # Find duplicate files in the specified directory
    file_info = {}

    for root, dirs, files in os.walk(directory):
        logging.info(f"Scanning directory: {root}")
        if root == directory:
            # Skip adding the initial directory to scanned_directories
            continue

        for filename in files:
            file_path = os.path.join(root, filename)
            file_size = os.path.getsize(file_path)
            checksum = get_file_checksum(file_path)
            if (file_size, checksum) in file_info:
                original_file_path = file_info[(file_size, checksum)]
                duplicate_files.append((original_file_path, file_path))
                logging.info(f"Duplicate file found: {file_path}")
            else:
                file_info[(file_size, checksum)] = file_path
                logging.info(f"File added to scanned files: {file_path}")

        logging.info(f"Finished scanning directory: {root}")

        # Add the directory to scanned_directories after all files in the directory have been processed
        if root != directory:
            scanned_directories.add(root)


def save_data_to_json(output_file):
    global scanned_directories, duplicate_files

    # Save data to JSON file
    with open(output_file, 'w') as f:
        json.dump({"scanned_directories": list(scanned_directories), "duplicate_files": duplicate_files}, f, indent=4)


def load_data_from_json(input_file):
    # Load data from JSON file
    if os.path.exists(input_file):
        with open(input_file, 'r') as f:
            return json.load(f)
    return {}


def signal_handler(sig, frame):
    global scanned_directories, duplicate_files

    print("\nInterrupt received. Saving scanned directories and duplicate files...")
    save_data_to_json(output_file)
    print("Scanned directories and duplicate files saved successfully.")
    logging.info("Scanned directories and duplicate files saved successfully.")
    sys.exit(0)


if __name__ == "__main__":
    # Set up interrupt handler
    signal.signal(signal.SIGINT, signal_handler)

    start_directory = input("Enter the initial start directory to scan for duplicate files: ")
    output_file = "duplicate_files.json"

    # Load scanned directories and duplicate files from previous run
    data = load_data_from_json(output_file)
    scanned_directories = set(data.get("scanned_directories", []))
    duplicate_files = data.get("duplicate_files", [])

    # Start scanning from the initial start directory
    find_duplicate_files(start_directory)

    if duplicate_files:
        print("Duplicate files found:")
        for file_path in duplicate_files:
            print(file_path)

        # Save details of duplicate files and scanned directories to JSON file
        save_data_to_json(output_file)
        print("Details of duplicate files saved to 'duplicate_files.json'.")
    else:
        print("No duplicate files found in the specified directory.")
