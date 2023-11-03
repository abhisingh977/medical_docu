from flask import Flask, request, render_template
import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from get_relevant_page import get_relevant_text
import string
import requests

PUNCT_TO_REMOVE = string.punctuation
app = Flask(__name__)
embedding_url = "http://0.0.0.0:8000/get_embedding_from_input/"  

url = os.environ["URL"]
api_key = os.environ["API_KEY"]


collection_name = "medical_docu"
retriever = SentenceTransformer("model/")
top_k = 5


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
        input_data = {
        "input_text": chunks
        }
        response = requests.post(url, json=input_data)

        if response.status_code == 200:
            embeddings = response.json()


        result = client.search(
            collection_name=collection_name,
            query_vector=embeddings[0],
            limit=top_k,
        )

        data = get_relevant_text(result)

        return render_template("index.html", results=data)


    except Exception as e:
        return render_template("index.html", error=str(e))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=os.getenv("PORT", 8080))
