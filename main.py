from flask import Flask, request, render_template, session
import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from get_relevant_page import get_relevant_text

import string

PUNCT_TO_REMOVE = string.punctuation
app = Flask(__name__)

url = os.environ["URL"]
api_key = os.environ["API_KEY"]

client = QdrantClient(
    url=url,
    timeout=100,
    api_key=api_key,
)
collection_name = "medical_docu"
retriever = SentenceTransformer("/app/model/")
top_k = 10

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
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
        print(data)
        return render_template("index.html", results=data)
    except Exception as e:
        return render_template("index.html", error=str(e))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=os.getenv("PORT", 8080))
