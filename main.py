from flask import Flask, request, render_template
import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from get_relevant_page import get_relevant_text
import base64

import string

PUNCT_TO_REMOVE = string.punctuation
app = Flask(__name__)

url = "https://52ff6a40-646f-4e96-ab95-d19b32ece70d.us-east4-0.gcp.cloud.qdrant.io:6333"
api_key = "4hxthKyOpwJqXwmwwmEUlVkFSqSr6ETc-s8P8jslW50hGykRxBJ_3g"

client = QdrantClient(
    url=url,
    timeout=100,
    api_key=api_key,
)
collection_name = "medical_docu"
retriever = SentenceTransformer("model/")
top_k = 5


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():

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
    print(f"results: {result}")
    data = get_relevant_text(result)

    return render_template("index.html", results=data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=os.getenv("PORT", 8080))
