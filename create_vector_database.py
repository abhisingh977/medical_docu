from tqdm import tqdm
import string
import os
from sentence_transformers import SentenceTransformer
from func import (
    removing_special_characters,
    spelling_correction,
    remove_singular_characters,
    remove_newlines_tabs,
    expand_contractions,
    accented_characters_removal,
    reducing_incorrect_character_repeatation,
    remove_links,
    remove_whitespace,
    strip_html_tags,
)
import fitz

from langchain.text_splitter import SentenceTransformersTokenTextSplitter
import os
import json
from pathlib import Path

os.environ["TOKENIZERS_PARALLELISM"] = "false"
# Define the directory where you want to start searching
start_directory = "/home/abhishek/abhi/medical/raw_data"

# Directory to store JSON files
json_directory = "/home/abhishek/abhi/medical/json_files/"

# Create the directory if it doesn't exist
Path(json_directory).mkdir(parents=True, exist_ok=True)

# Create an empty list to store the paths of PDF files
pdf_files = []

# Walk through the directory tree using os.walk
for root, dirs, files in os.walk(start_directory):
    for file in files:
        # Check if the file has a .pdf extension
        if file.endswith(".pdf"):
            # Construct the full path to the PDF file
            pdf_path = os.path.join(root, file)
            pdf_files.append(pdf_path)


model = SentenceTransformer("all-MiniLM-L6-v2")

json_file_counter = 0
splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=30)
PUNCT_TO_REMOVE = string.punctuation

json_list = []
def get_new_json_filename(counter):
    filename = os.path.join(json_directory, f"output_{counter}.json")
    if not os.path.exists(filename):
        with open(filename, "w") as new_file:
            new_file.write("")
    print(filename)
    return filename

# Initialize the current JSON file
current_json_filename = get_new_json_filename(json_file_counter)

for i in tqdm(range(len(pdf_files))):
    print(pdf_files[i])
    with fitz.open(pdf_files[i]) as doc:
        for j in tqdm(range(len(doc))):
            chunks = doc[j].get_text()

            if len(str(chunks)) >= 10:
                chunks = chunks.lower()
                chunks = chunks.translate(str.maketrans("", "", PUNCT_TO_REMOVE))
                chunks = " ".join(chunks.split())  # remove spaces
                chunks = removing_special_characters(chunks)
                chunks = remove_newlines_tabs(chunks)
                chunks = strip_html_tags(chunks)
                chunks = remove_links(chunks)
                chunks = remove_whitespace(chunks)
                chunks = accented_characters_removal(chunks)
                chunks = reducing_incorrect_character_repeatation(chunks)
                chunks = expand_contractions(chunks)
                chunks = spelling_correction(chunks)
                chunks = remove_singular_characters(chunks)

                if len(str(chunks)) > 5:
                    txt = splitter.split_text(text=chunks)

                    for t in txt:
                        embedding = model.encode(t).tolist() # Convertinf txt to embedding.
                        data_to_append = {
                            "text": t,
                            "embedding": embedding,
                            "page_no": j,
                            "filename": os.path.basename(pdf_files[i]),
                        }
                        json_list.append(data_to_append)

    with open(current_json_filename, "w") as f:
        json.dump(json_list, f)
        json_file_counter += 1
        current_json_filename = get_new_json_filename(json_file_counter)
        json_list = []
