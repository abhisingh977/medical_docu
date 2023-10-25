from flask import Flask, request, render_template
import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from get_relevant_page import get_relevant_text
import time
import string

PUNCT_TO_REMOVE = string.punctuation
app = Flask(__name__)

url = os.environ["URL"]
api_key = os.environ["API_KEY"]


collection_name = "medical_docu"
retriever = SentenceTransformer("/app/model/")
top_k = 5
max_retries = 3
retry_delay = 2  # You can adjust this delay based on your needs


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    client = QdrantClient(
        url=url,
        timeout=100,
        api_key=api_key,
    )
    try:
        # Get input text from the form
        input_text = request.form.get("text")
        chunks = input_text.lower()

        encoded_query = retriever.encode(
            chunks
        ).tolist()  # generate embeddings for the question

        retries = 0
        while retries < max_retries:
            try:
                result = client.search(
                    collection_name=collection_name,
                    query_vector=encoded_query,
                    limit=top_k,
                )

                data = get_relevant_text(result)
                print(data)
                return render_template("index.html", results=data)
            except TimeoutError as e:
                # Handle the timeout error here, and then retry after a delay
                print(f"Retry {retries + 1}: Timeout Error - {e}")
                retries += 1
                time.sleep(retry_delay)

        # If all retries fail, return an error message
        return render_template(
            "index.html", error="Search operation failed after multiple retries."
        )
    except Exception as e:
        return render_template("index.html", error=str(e))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=os.getenv("PORT", 8080))
