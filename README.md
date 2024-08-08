# File Scanner App

Welcome to the File Scanner App repository! This application allows users to upload files, choose an OCR (Optical Character Recognition) model (either PyTesseract or Azure), and extract text from the uploaded files. The extracted text can be previewed and saved as a `.txt` file.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Routes](#routes)
- [Contributing](#contributing)
- [License](#license)

## Features

- Upload multiple files (supports PDF, PNG, JPG, JPEG)
- Choose between PyTesseract and Azure OCR models for text extraction
- Preview extracted text before saving
- Download extracted text as a `.txt` file

## Requirements

- Python 3.x
- Flask
- PyTesseract
- Azure Form Recognizer
- Additional libraries as specified in `requirements.txt`

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/jago-h/website1.git
    cd website1
    ```

2. **Create and activate a virtual environment:**
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

## Configuration

1. **Update settings:**
    Create a `settings.py` file in the root directory with the following content:
    ```python
    UPLOAD_FOLDER = 'uploads'
    MEDIA_DIR = 'static/media'
    TEMP_FOLDER = 'temp'
    AZURE_FORM_RECOGNIZER_ENDPOINT = 'YOUR_AZURE_FORM_RECOGNIZER_ENDPOINT'
    AZURE_FORM_RECOGNIZER_KEY = 'YOUR_AZURE_FORM_RECOGNIZER_KEY'
    ```

2. **Ensure necessary directories exist:**
    ```sh
    mkdir -p temp static/media
    ```

## Usage

1. **Run the application:**
    ```sh
    flask run
    ```

2. **Open your browser and navigate to:**
    ```
    http://127.0.0.1:5000
    ```

## Routes

- **`GET /`**
  - Renders the main scanner page.
  
- **`POST /upload`**
  - Handles file uploads and text extraction.
  
- **`GET /uploads/<filename>`**
  - Serves the uploaded files from the media directory.

- **`POST /save_file`**
  - Saves the extracted text as a `.txt` file.

- **`GET /download/<filename>`**
  - Allows downloading of the saved text files.

## Contributing

We welcome contributions! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

## License

This project was a part of an internship programme at FPT Software. It is intended for non-commercial use only. Commercial use of this software is strictly prohibited without prior written permission. 

If you use this software in your research or other work, please cite it as follows:

**File Scanner App by Jagoda Hanuszewicz and Heaymalaah Kunalan**

