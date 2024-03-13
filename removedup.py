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
file_info = {}


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
    global scanned_directories, duplicate_files, file_info

    # Find duplicate files in the specified directory
    for root, dirs, files in os.walk(directory):
        logging.info(f"Scanning directory: {root}")
        if root in scanned_directories:
            logging.info(f"Already scanned skip.. : {root}")
            continue  # Skip already scanned directories

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

def convert_tuple_to_list(data):
    # Convert tuples to lists in the dictionary keys
    converted_data = {str(key): value for key, value in data.items()}
    return converted_data

def save_data_to_json(output_file):
    global scanned_directories, duplicate_files, file_info

    # Convert tuples in file_info to lists
    file_info_converted = convert_tuple_to_list(file_info)

    # Save data to JSON file
    with open(output_file, 'w') as f:
        json.dump({"scanned_directories": list(scanned_directories), "duplicate_files": duplicate_files, "file_info": file_info_converted}, f, indent=4)

def load_data_from_json(input_file):
    global scanned_directories, duplicate_files, file_info

    # Load data from JSON file
    try:
        if os.path.exists(input_file):
            with open(input_file, 'r') as f:
                data = json.load(f)
                scanned_directories = set(data.get("scanned_directories", []))
                duplicate_files = data.get("duplicate_files", [])
                file_info_data = data.get("file_info", {})
                # Populate file_info dictionary with correct format
                file_info = {eval(key): value for key, value in file_info_data.items()}
        else:
            scanned_directories = set()
            duplicate_files = []
            file_info = {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from {input_file}: {e}")
        scanned_directories = set()
        duplicate_files = []
        file_info = {}



def signal_handler(sig, frame):
    global scanned_directories, duplicate_files, file_info

    print("\nInterrupt received. Saving scanned directories, duplicate files, and file info...")
    save_data_to_json(output_file)
    print("Scanned directories, duplicate files, and file info saved successfully.")
    logging.info("Scanned directories, duplicate files, and file info saved successfully.")
    sys.exit(0)


if __name__ == "__main__":
    # Set up interrupt handler
    signal.signal(signal.SIGINT, signal_handler)

    # Get start directory from environment variable or prompt user
    start_directory = os.getenv("START_DIRECTORY")
    if not start_directory:
        start_directory = input("Enter the initial start directory to scan for duplicate files: ")

    output_file = "duplicate_files.json"

    # Load scanned directories, duplicate files, and file info from previous run
    load_data_from_json(output_file)

    # Start scanning from the initial start directory
    find_duplicate_files(start_directory)

    if duplicate_files:
        print("Duplicate files found:")
        for file_path in duplicate_files:
            print(file_path)

        # Save details of duplicate files, scanned directories, and file info to JSON file
        save_data_to_json(output_file)
        print("Details of duplicate files, scanned directories, and file info saved to 'duplicate_files.json'.")
    else:
        print("No duplicate files found in the specified directory.")
