from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
import shutil
import utils
import settings
import azure_model

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = settings.TEMP_FOLDER
app.config['MEDIA_DIR'] = settings.MEDIA_DIR

def clean_folders():
    """Remove all files in the TEMP_FOLDER and MEDIA_DIR."""
    for directory in [app.config['TEMP_FOLDER'], app.config['MEDIA_DIR']]:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

@app.route('/')
def index():
    return render_template('scanner.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['MEDIA_DIR'], filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Clean the upload and media folders before processing new files
    clean_folders()
    
    if 'files' not in request.files:
        return "No files part", 400

    files = request.files.getlist('files')
    ocr_model = request.form.get('ocr_model')
    
    if not files:
        return "No selected files", 400

    text_files = []
    for file in files:
        if file.filename == '':
            return "One or more files have no selected file", 400

        if not utils.allowed_file(file.filename):
            return f"Invalid file format for {file.filename}", 400
        
        
        file_content = utils.read_file_content(file)
        if file_content is None:
            return f"Error reading file {file.filename}", 500

        temp_file_path = utils.save_temp_file(file.filename, file_content)


        if ocr_model == 'pytesseract':
            if file.filename.endswith('.pdf'):
                images = utils.convert_pdf_to_images(temp_file_path)
                if not images:
                    return f"Failed to convert PDF {file.filename} to images", 500
                texts = [utils.extract_text_from_image(img) for img in images]
                extracted_text = "\n".join(texts)
            else:
                image = utils.read_image_from_content(file_content)
                if image is None:
                    return f"Failed to read image {file.filename}", 500
                extracted_text = utils.extract_text_from_image(image)
            
            text_file_name = utils.save_text(file.filename, extracted_text, app.config['MEDIA_DIR'])  # Save to static/media
            text_files.append(text_file_name)

        elif ocr_model == 'azure':
            extracted_text = azure_model.ext_text(temp_file_path)
            text_file_name = azure_model.read_and_write_file(file.filename, extracted_text, app.config['MEDIA_DIR'])  # Save to static/media
            text_files.append(text_file_name)
       
    
    return render_template('results.html', text_files=text_files)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['MEDIA_DIR'], filename)
    if os.path.exists(file_path):
        return send_from_directory(app.config['MEDIA_DIR'], filename)
    else:
        return f"File {filename} not found.", 404

@app.route('/save_file', methods=['POST'])
def save_file():
    filename = request.form.get('filename')
    file_path = os.path.join(app.config['MEDIA_DIR'], filename)
    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        print(f"An error occurred while sending the file: {e}")
        return redirect(url_for('scanner'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['MEDIA_DIR']):
        os.makedirs(app.config['MEDIA_DIR'])
    app.run(debug=True, port=5001)
    