import os
import hashlib
import json
import signal
import sys
import logging

logging.basicConfig(filename='duplicate_files.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


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


def find_duplicate_files(directory, scanned_directories):
    # Find duplicate files in the specified directory
    file_info = {}
    duplicate_files = []

    for root, dirs, files in os.walk(directory):
        logging.info(f"Scanning directory: {root}")
        if root in scanned_directories:
            continue  # Skip already scanned directories
        for filename in files:
            file_path = os.path.join(root, filename)
            file_size = os.path.getsize(file_path)
            checksum = get_file_checksum(file_path)
            if (file_size, checksum) in file_info:
                duplicate_files.append(file_path)
                logging.info(f"Duplicate file found: {file_path}")
            else:
                file_info[(file_size, checksum)] = file_path
                logging.info(f"File added to scanned files: {file_path}")

        logging.info(f"Finished scanning directory: {root}")

    # Update scanned directories list
    scanned_directories.add(directory)

    return duplicate_files, scanned_directories


def save_data_to_json(data, output_file):
    # Save data to JSON file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)


def load_data_from_json(input_file):
    # Load data from JSON file
    if os.path.exists(input_file):
        with open(input_file, 'r') as f:
            return json.load(f)
    return {}


def signal_handler(sig, frame):
    print("\nInterrupt received. Saving scanned directories and duplicate files...")
    save_data_to_json({"scanned_directories": list(scanned_directories), "duplicate_files": duplicate_files},
                      output_file)
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
    new_duplicate_files, scanned_directories = find_duplicate_files(start_directory, scanned_directories)
    duplicate_files.extend(new_duplicate_files)

    if new_duplicate_files:
        print("Duplicate files found:")
        for file_path in new_duplicate_files:
            print(file_path)

        # Save details of duplicate files and scanned directories to JSON file
        save_data_to_json({"scanned_directories": list(scanned_directories), "duplicate_files": duplicate_files},
                          output_file)
        print("Details of duplicate files saved to 'duplicate_files.json'.")
    else:
        print("No duplicate files found in the specified directory.")


