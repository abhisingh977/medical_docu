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
            "filename": x.payload["filename"],
            "page_no": x.payload["page_no"],
            "text": x.payload["text"],
        }
        for x in sorted_result
    ]  # extract title and payload from result
  
    return context

