import urllib.parse
import requests
from io import BytesIO
import fitz
import base64
import re 

dpi = 120

mat = fitz.Matrix(dpi / 72, dpi / 72)
highlight_color = (1, 1, 0)


def transform_text(input_text):
    # Use urllib.parse to quote the input text
    transformed_text = urllib.parse.quote(input_text)
    return transformed_text


def pdf_to_image(filename, page_no, embedd_text=None):
    
    filename = transform_text(filename)
    path = f"https://storage.googleapis.com/zospital_medical_pdfs/anesthesia/books/{filename}/{page_no}.pdf"
    response = requests.get(path)


    if response.status_code == 200:
        # Read the content into a BytesIO object
        pdf_data = BytesIO(response.content)
        # Open he PDF using PyMuPDF
        with fitz.open("pdf", pdf_data) as doc:
            page = doc[0]

            text_instances = page.search_for(embedd_text)

            for text_instance in text_instances:
                highlight = page.add_highlight_annot(text_instance)

                # Set the highlight color
                highlight.set_colors(stroke=highlight_color)

            image = page.get_pixmap(matrix=mat)
            image = image.tobytes()
            image = base64.b64encode(image).decode("utf-8")

    return image


def contact(filename, page_no):
    filename  = re.sub(r'[^a-zA-Z\s]', '', filename)
    filename = transform_text(filename)
    page_no = page_no.split("_")[1]
    page_no = str(int(page_no) + 1)
    return f"https://storage.googleapis.com/zostipal_books/anesthesia/books/{filename}.pdf#page={page_no}"

def get_relevant_text(result):
    result = result[:5]

    context = [
        {
            "pdf_link": contact(x["payload"]["book_name"], x["payload"]["page_no"]),
            "pdf_image": pdf_to_image(
                x["payload"]["book_name"], x["payload"]["page_no"], x["payload"]["text"]
            ),
            "text": x["payload"]["text"],
            "page_no": str(int(x["payload"]["page_no"].split("_")[1])+1),
            "name": x["payload"]["book_name"],
            "year": x["payload"]["year"],
            "score": x["score"],
        }
        for x in result
    ]  # extract title and payload from result

    return context
