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

    # Save the file to inspect if necessary
    temp_file_path = os.path.join(UPLOAD_FOLDER, file_name)
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_content.getvalue())
    
    # Reset the BytesIO object position to the beginning
    file_content.seek(0)

    if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
        try:
            # Try to open the image using PIL
            Image.open(file_content).verify()  # Verify if it is a valid image
        except Exception as e:
            return f"The file {file_name} is not a valid image. Error: {str(e)}"
        
        # Re-open the image after verification for processing
        file_content.seek(0)
    
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
                # Reset the BytesIO object position to the beginning
                file_content.seek(0)
                image = Image.open(file_content)
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

@app.route('/view/<filename>')
def view_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/list_uploads', methods=['GET'])
def list_uploads():
    files = os.listdir(UPLOAD_FOLDER)
    files_list = [f'<a href="/view/{file}">{file}</a>' for file in files]
    return '<br>'.join(files_list)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(TEXT_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=5002)

