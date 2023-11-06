from flask import Flask, request, render_template
import os
import httpx
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from get_relevant_page import get_relevant_text
import requests
from threading import Thread
from concurrent.futures import ThreadPoolExecutor


app = Flask(__name__)
embedding_url = "https://embeddings-svgzkfaqoa-uc.a.run.app"  

url1 = "https://eeaf6476-d517-463d-aec6-80c8de35d1b4.us-east4-0.gcp.cloud.qdrant.io:6333"#os.environ["URL1"]
api_key1 = "Qs-hsKFr4q50-Wh5poVPZ60_QiisichTrwNjjGmM09h0g0srKdVpZg"#os.environ["API_KEY1"]
collection_name1 = "data"

url2 = "https://735a1992-d2a2-47e7-985d-26d74299665b.us-east4-0.gcp.cloud.qdrant.io:6333"
api_key2 = "5wVZ_ZP4AK8UvgV7DgW9pptnjLs1WPmYzvxe3nyCFur7O3em2cbqBA"
collection_name2 = "anesthesia"


retriever = SentenceTransformer("model/")
top_k = 10


def search_client(client, collection_name, query_vector, top_k=10):
    res =  client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
    )
    sorted_res = sorted(res, key=lambda x: x.score, reverse=True)

    return sorted_res

def make_request(embedding_url):
    response = httpx.get(embedding_url)

@app.route("/")
def index():
    try:
        Thread(target=make_request, args=(embedding_url,)).start()
    except httpx.ReadTimeout:
        pass

    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    client1 = QdrantClient(
        url=url1,
        timeout=60,
        api_key=api_key1,
    )
    client2 = QdrantClient(
        url=url2,
        timeout=60,
        api_key=api_key2,
    )
    try:
        # Get input text from the form
        input_text = request.form.get("text")
        chunks = input_text.lower()
        input_data = {
        "input_text": chunks
        }
        response = requests.post(embedding_url+"/"+"get_embedding_from_input/", json=input_data)

        if response.status_code == 200:
            embeddings = response.json()


        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(search_client, client1, collection_name1, embeddings[0], top_k)
            future2 = executor.submit(search_client, client2, collection_name2, embeddings[0], top_k)

        result1 = future1.result()
        result2 = future2.result()
        result1.append(result2)
        
        data = get_relevant_text(result1)

        return render_template("index.html", results=data)


    except Exception as e:
        return render_template("index.html", error=str(e))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=os.getenv("PORT", 8080))
