import os
from PIL import Image
from pdf2image import convert_from_path
import pytesseract

TEMP_DIR = 'temp'

def create_temp_dir():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

def save_temp_file(filename, file_content):
    create_temp_dir()
    temp_file_path = os.path.join(TEMP_DIR, filename)
    with open(temp_file_path, 'wb') as f:
        f.write(file_content.read())
    return temp_file_path

def allowed_file(filename):
    allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def read_file_content(file):
    return file

def read_image_from_content(content):
    try:
        return Image.open(content)
    except Exception as e:
        print(f"Error reading image: {e}")
        return None

def extract_text_from_image(image):
    try:
        return pytesseract.image_to_string(image)
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def convert_pdf_to_images(pdf_file_path):
    try:
        return convert_from_path(pdf_file_path)
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
    return []

def save_text(filename, text, media_dir):
    # Ensure media_dir exists
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
    
    text_filename = f"{os.path.splitext(filename)[0]}.txt"
    text_file_path = os.path.join(media_dir, text_filename)
    
    # Check if the path already exists as a file
    if os.path.isfile(text_file_path):
        raise Exception(f"Path conflict: {text_file_path} exists as a file.")
    
    with open(text_file_path, 'w') as f:
        f.write(text)
    
    return text_filename
