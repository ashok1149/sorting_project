import os
import re
import datetime
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from sorter import sort_pdf_by_sku  # Make sure sorter.py is in the same folder

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
SORTED_FOLDER = 'sorted'
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SORTED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist('pdf_files')
        if not files or files[0].filename == '':
            return render_template('index.html', error="No files selected!")

        sorted_files = []
        today = datetime.datetime.now().strftime('%Y-%m-%d')

        # Clear previous sorted files (optional)
        for f in os.listdir(SORTED_FOLDER):
            os.remove(os.path.join(SORTED_FOLDER, f))

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                input_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(input_path)

                base_name = os.path.splitext(filename)[0]
                sorted_filename = f"{base_name}_sorted_{today}.pdf"
                output_path = os.path.join(SORTED_FOLDER, sorted_filename)

                sort_pdf_by_sku(input_path, output_path)
                sorted_files.append(sorted_filename)

        return render_template('index.html', sorted_files=sorted_files)

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(SORTED_FOLDER, filename), as_attachment=True)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    path = os.path.join(SORTED_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
        return jsonify({'success': True, 'message': f'{filename} deleted'})
    else:
        return jsonify({'success': False, 'message': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
