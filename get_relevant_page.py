import urllib.parse

def transform_text(input_text):
    # Use urllib.parse to quote the input text
    transformed_text = urllib.parse.quote(input_text)
    return transformed_text

def contact(filename, page_no):
    filename = transform_text(filename)
    page_no = str(int(page_no)+1)
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
            "text": x.payload["text"],
        }
        for x in sorted_result
    ]  # extract title and payload from result
  
    return context