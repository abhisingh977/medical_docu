import urllib.parse
import requests
from io import BytesIO
import fitz
import base64

dpi = 300
mat = fitz.Matrix(dpi / 72, dpi / 72)
highlight_color = (1, 1, 0)


def transform_text(input_text):
    # Use urllib.parse to quote the input text
    transformed_text = urllib.parse.quote(input_text)
    return transformed_text


def pdf_to_image(filename, page_no, embedd_text=None):
    filename = transform_text(filename)
    path = f"https://storage.googleapis.com/medical_docu_pdfs/{filename}"
    response = requests.get(path)
    page_no = int(page_no)

    if response.status_code == 200:
        # Read the content into a BytesIO object
        pdf_data = BytesIO(response.content)
        # Open he PDF using PyMuPDF
        with fitz.open("pdf", pdf_data) as doc:
            page = doc[page_no]

            text_instances = page.search_for(embedd_text)

            for text_instance in text_instances:
                highlight = page.add_highlight_annot(text_instance)

                # Set the highlight color
                highlight.set_colors(stroke=highlight_color)

            image = page.get_pixmap(matrix=mat)
            image = image.tobytes()
            image = base64.b64encode(image).decode("utf-8")

            # print(image)
    return image


def contact(filename, page_no):
    filename = transform_text(filename)
    page_no = str(int(page_no) + 1)
    return f"https://storage.googleapis.com/medical_docu_pdfs/{filename}#page={page_no}"


def get_relevant_text(result):
    """
    Get the relevant plot for a given question

    Args:
        question (str): What do we want to know?
        top_k (int): Top K results to return

    Returns:
        context (List[str]):
    """
    sorted_result = sorted(result, key=lambda x: x.score, reverse=True)

    context = [
        {
            "pdf_link": contact(x.payload["filename"], x.payload["page_no"]),
            "pdf_image": pdf_to_image(
                x.payload["filename"], x.payload["page_no"], x.payload["embeded_text"]
            ),
            "text": x.payload["text"],
        }
        for x in sorted_result
    ]  # extract title and payload from result

    return context
