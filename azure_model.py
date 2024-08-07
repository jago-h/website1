from dotenv import load_dotenv
import os

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
    if result.styles and any([style.is_handwritten for style in result.styles]):
        print("Document contains handwritten content")
    else:
        print("Document does not contain handwritten content")

    for page in result.pages:
        print(f"----Analyzing layout from page #{page.page_number}----")

        if page.lines:
            for line_idx, line in enumerate(page.lines):
                print(line.content)
                
    if result.tables:
        for table_idx, table in enumerate(result.tables):
            print(f"Table # {table_idx} has {table.row_count} rows and " f"{table.column_count} columns")
            for cell in table.cells:
                print(f"...Cell[{cell.row_index}][{cell.column_index}] has text '{cell.content}'")

    print("----------------------------------------")

   
#The file size must not exceed 5 MB !!!
path = "temp/FSA_FRAME TEAMS MEETING-01 2.jpg"
print(analyse(get_result_from_file(path)))