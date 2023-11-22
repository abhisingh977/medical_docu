import urllib.parse
import requests
from io import BytesIO
import fitz
import base64
import re 
from flask import request

if request.user_agent.is_mobile:
    dpi = 70
elif request.user_agent.is_tablet:
    dpi = 70
  # The user is using a tablet device
elif request.user_agent.is_desktop:
    dpi = 120
else:
    dpi = 120


mat = fitz.Matrix(dpi / 72, dpi / 72)
highlight_color = (1, 1, 0)


def transform_text(input_text):
    # Use urllib.parse to quote the input text
    transformed_text = urllib.parse.quote(input_text)
    return transformed_text


def pdf_to_image(filename, page_no,embedd_text,specialization):
    
    filename = transform_text(filename)
    path = f"https://storage.googleapis.com/zos_medical_pdfs/{specialization}/books/{filename}/{page_no}.pdf"
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
    else:
        return None


def contact(filename, page_no, specialization):
    filename  = re.sub(r'[^a-zA-Z\s]', '', filename)
    filename = transform_text(filename)
    page_no = page_no.split("_")[1]
    page_no = str(int(page_no) + 1)
    return f"https://storage.googleapis.com/zos_books/{specialization}/books/{filename}.pdf#page={page_no}"

def get_relevant_text(result, specialization):
    result = result[:5]

    context = [
        {
            "pdf_link": contact(x["payload"]["book_name"], x["payload"]["page_no"],specialization),
            "pdf_image": pdf_to_image(
                x["payload"]["book_name"], x["payload"]["page_no"], x["payload"]["text"],specialization
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
