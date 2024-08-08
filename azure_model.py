from dotenv import load_dotenv
import os
import utils

load_dotenv(".env")
print(os.getenv("endpoint"))

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.documentintelligence.models import AnalyzeResult
 

endpoint = os.getenv("endpoint")
credential = os.getenv("AZURE_KEY")

document_analyse_client = DocumentAnalysisClient(endpoint, credential=AzureKeyCredential(credential))

def _in_span(word, spans):
    for span in spans:
        if word.span.offset >= span.offset and (
            word.span.offset + word.span.length
        ) <= (span.offset + span.length):
            return True
    return False
 
def get_words(page, line):
    result_words = []
    for word in page.words:
        if _in_span(word, line.spans):
            result_words.append(word)
    return result_words

def get_result_from_file(path):
    with open(path, "rb") as f:
        poller = document_analyse_client.begin_analyze_document(
            "prebuilt-document", document=f
        )
    result: AnalyzeResult = poller.result()
    return result
    # print(result)

def analyse(result):
    extracted_lines = []

    if result.styles and any([style.is_handwritten for style in result.styles]):
        extracted_lines.append("Document contains handwritten content")
    
    for page in result.pages:
        extracted_lines.append(f"----Analyzing layout from page #{page.page_number}----")

        if page.lines:
            for line_idx, line in enumerate(page.lines):
                if line.content:
                    extracted_lines.append(line.content)
                
    if result.tables:
        for table_idx, table in enumerate(result.tables):
            extracted_lines.append(f"Table # {table_idx} has {table.row_count} rows and {table.column_count} columns")
            for cell in table.cells:
                extracted_lines.append(f"...Cell[{cell.row_index}][{cell.column_index}] has text '{cell.content}'")

    extracted_lines.append("----------------------------------------")
    return extracted_lines


#path = "temp/FSA_FRAME TEAMS MEETING-01 2.jpg"
#result_text = (get_result_from_file(path))
#extracted_text = (analyse(result_text))
#print(extracted_text)
   
   
#The file size must not exceed 5 MB !!!
def ext_text(temp_file_path):
    path = temp_file_path
    extracted_text = (analyse(get_result_from_file(path)))
    return extracted_text


def read_and_write_file(filename, extracted_text, media_dir):
    # Ensure media_dir exists
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
    
    text_filename = f"{os.path.splitext(filename)[0]}.txt"
    text_file_path = os.path.join(media_dir, text_filename)
    
    # Check if the path already exists as a file
    if os.path.isfile(text_file_path):
        raise Exception(f"Path conflict: {text_file_path} exists as a file.")
    
    try:
        with open(text_file_path, 'w', encoding='utf-8') as outfile:
            # Ensure every line ends with a newline character
            lines = [line if line is not None else '' for line in extracted_text]
            outfile.writelines(line + '\n' for line in lines)
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")
        
    return text_filename