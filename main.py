from flask import Flask, request, render_template
import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from get_relevant_page import get_relevant_text
import string

PUNCT_TO_REMOVE = string.punctuation
app = Flask(__name__)

url = os.environ["URL"]
api_key = os.environ["API_KEY"]


collection_name = "medical_docu"
retriever = SentenceTransformer("model/")
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
        timeout=200,
        api_key=api_key,
    )
    try:
        # Get input text from the form
        input_text = request.form.get("text")
        chunks = input_text.lower()

        encoded_query = retriever.encode(
            chunks
        ).tolist()  # generate embeddings for the question


        result = client.search(
            collection_name=collection_name,
            query_vector=encoded_query,
            limit=top_k,
        )

        data = get_relevant_text(result)

        return render_template("index.html", results=data)


    except Exception as e:
        return render_template("index.html", error=str(e))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=os.getenv("PORT", 8080))
