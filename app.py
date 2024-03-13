import os
import json
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)

# Function to read and update the duplicate_files.json file
def update_duplicate_files(files_to_delete):
    with open('duplicate_files.json', 'r') as f:
        data = json.load(f)
        updated_data = {"duplicate_files": []}
        for files_pair in data["duplicate_files"]:
            updated_pair = [file_path for file_path in files_pair if file_path not in files_to_delete]
            if len(updated_pair) > 0:  # Only add if at least one file still exists
                updated_data["duplicate_files"].append(updated_pair)

    with open('duplicate_files.json', 'w') as f:
        json.dump(updated_data, f, indent=4)

# Route to present duplicate files for deletion
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files_to_delete = request.form.getlist('file_to_delete[]')
        deleted_files = []
        for file_path in files_to_delete:
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_files.append(file_path)
            else:
                print(f"File not found: {file_path}")  # Log the error
        update_duplicate_files(deleted_files)
        return redirect(url_for('index'))  # Redirect to index after deletion
    else:
        with open('duplicate_files.json', 'r') as f:
            duplicate_files = json.load(f).get("duplicate_files", [])
        return render_template('index.html', duplicate_files=duplicate_files)

# Route to serve the file
@app.route('/file/<path:file_path>')
def serve_file(file_path):
    full_file_path = '/' + file_path  # Prepend the missing path
    return send_from_directory(os.path.dirname(full_file_path), os.path.basename(full_file_path))

# Function to read data from JSON file
def load_data_from_json(input_file):
    if os.path.exists(input_file):
        with open(input_file, 'r') as f:
            data = json.load(f)
            file_info_data = data.get("file_info", {})
            # Populate file_info dictionary with correct format
            #file_info = { value for  value in file_info_data.items()}
            file_info = []
            for key, value in data.get("file_info", {}).items():
                file_info.append(value)
            return file_info
    return []

# Route to display all scanned files
@app.route('/all-files')
def all_files():
    file_info = load_data_from_json('duplicate_files.json')
    return render_template('all_files.html', file_info=file_info)

if __name__ == '__main__':
    app.run(debug=True)
