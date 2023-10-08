from flask import Flask, request, jsonify, render_template
import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from get_relevant_page import get_relevant_text
from func import (
    removing_special_characters,
    spelling_correction,
    lemmatization,
    remove_singular_characters,
    remove_words_not_in_english,
    remove_newlines_tabs,
    expand_contractions,
    accented_characters_removal,
    reducing_incorrect_character_repeatation,
    remove_links,
    remove_whitespace,
    strip_html_tags,
)
import string

PUNCT_TO_REMOVE = string.punctuation
app = Flask(__name__)

url = "https://9a61774e-dd62-4dcd-a475-9a1ccfcf89b6.us-east4-0.gcp.cloud.qdrant.io:6333"
api_key = "ddrUQecTjYVIc39ckHemRSZP5sfiyWq1fLxvJpzUxFg-2PdeKbV1tw"

client = QdrantClient(
    url=url,
    api_key=api_key,
)
collection_name = "medical_docu"
retriever = SentenceTransformer("/app/model/")
top_k = 5


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    try:
        # Get input text from the form
        input_text = request.form.get("text")
        chunks = input_text.lower()
        chunks = chunks.translate(str.maketrans("", "", PUNCT_TO_REMOVE))
        chunks = " ".join(chunks.split())  # remove spaces
        chunks = removing_special_characters(chunks)
        chunks = remove_newlines_tabs(chunks)
        chunks = strip_html_tags(chunks)
        chunks = remove_links(chunks)
        chunks = remove_whitespace(chunks)
        chunks = accented_characters_removal(chunks)
        chunks = reducing_incorrect_character_repeatation(chunks)
        chunks = expand_contractions(chunks)
        chunks = spelling_correction(chunks)
        chunks = lemmatization(chunks)
        chunks = remove_singular_characters(chunks)
        chunks = remove_words_not_in_english(chunks)

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
