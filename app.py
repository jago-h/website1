from flask import Flask, request, render_template, send_from_directory
import pytesseract
from PIL import Image
import pdf2image
from io import BytesIO
import os

# Specify the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
UPLOAD_FOLDER = 'uploads'
TEXT_FOLDER = 'texts'

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEXT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_text(file_name, text):
    base_name, _ = os.path.splitext(file_name)
    text_file_name = f"{base_name}.txt"
    text_file_path = os.path.join(TEXT_FOLDER, text_file_name)
    with open(text_file_path, 'w') as f:
        f.write(text)
    return text_file_name

def process_file(file):
    file_name = file.filename

    if not allowed_file(file_name):
        return f"Unsupported file type for {file_name}. Please upload only PNG, JPG, JPEG, or PDF files."

    file_content = BytesIO(file.read())  # Read file content into a BytesIO object

    try:
        if file_name.lower().endswith('.pdf'):
            try:
                images = pdf2image.convert_from_bytes(file_content.read())
                texts = [pytesseract.image_to_string(image) for image in images]
                combined_text = "\n".join(texts)
                text_file_name = save_text(file_name, combined_text)
                return f"Text from {file_name}:\n" + combined_text + f"<br><a href='/download/{text_file_name}'>Download text file</a>"
            except Exception as pdf_error:
                return f"Error processing PDF {file_name}: {str(pdf_error)}"
        else:
            try:
                image = Image.open(file_content)
                print(f"Image mode: {image.mode}, Size: {image.size}")  # Debugging info
                text = pytesseract.image_to_string(image)
                if not text.strip():
                    return f"No text found in image {file_name}."
                text_file_name = save_text(file_name, text)
                return f"Text from {file_name}:\n" + text + f"<br><a href='/download/{text_file_name}'>Download text file</a>"
            except Exception as img_error:
                return f"Error processing image {file_name}: {str(img_error)}"
    except Exception as e:
        return f"Error processing {file_name}: {str(e)}"

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('files')
    results = []
    for file in files:
        if file and allowed_file(file.filename):
            result = process_file(file)
            results.append(result)
    return '<br>'.join(results)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(TEXT_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=5002)
