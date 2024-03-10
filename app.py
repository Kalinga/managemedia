import os
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Function to read and update the duplicate_files.json file
def update_duplicate_files(files_to_delete):
    with open('duplicate_files.json', 'r') as f:
        data = json.load(f)
        updated_data = {"duplicate_files": []}
        for files_pair in data["duplicate_files"]:
            updated_pair = [file_path for file_path in files_pair if file_path not in files_to_delete]
            if len(updated_pair) == 2:  # Only add if both files still exist
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

if __name__ == '__main__':
    app.run(debug=True)
