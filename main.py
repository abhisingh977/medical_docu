from flask import Flask, request, render_template
import os
from get_relevant_page import get_relevant_text
import requests
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import json
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['TIMEOUT'] = 5000

embedding_url = os.environ["embedding_url"]

url1 = os.environ["url1"]
api_key1 = os.environ["api_key1"]
collection_name1 = "data"
endpoint1 = f'{url1}/collections/{collection_name1}/points/search'
headers1 = {
  'Content-Type': 'application/json',
  'api-key': api_key1
}

url2 = os.environ["url2"]
api_key2 = os.environ["api_key2"]
collection_name2 = "anesthesia"
endpoint2 = f'{url2}/collections/{collection_name2}/points/search'
headers2 = {
  'Content-Type': 'application/json',
  'api-key': api_key2
}

top_k = 10

def search_client(endpoint,payload, headers):
    logging.info(f"Making request to endpoint: str{endpoint}")
    res = requests.post(endpoint, data=json.dumps(payload), headers=headers,timeout=500)
    if res.status_code == 200:  # Assuming a successful response has status code 200
        res = res.json()  # Get the response data in JSON format
        res = res["result"]
        res = sorted(res, key=lambda x: x['score'], reverse=True)
        res = get_relevant_text(res)

    # Process the data as needed
    else:
        logging.info(f"Request failed with status code {res.status_code}")
        logging.info(res.text)  # Print the error message or details if the request fails
        logging.info(f"{endpoint} did not returned respose in time.")


    return res

def make_request(embedding_url):
    try:
        response = requests.get(embedding_url,timeout=1)
    except:
        pass

@app.route("/")
def index():
    try:
        Thread(target=make_request, args=(embedding_url,)).start()
    except:
        pass

    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():

# Get input text from the form
    input_text = request.form.get("text")
    start_year = int(request.form.get("start_year"))
    end_year = int(request.form.get("end_year"))

    chunks = input_text.lower()
    input_data = {
    "input_text": chunks
    }

    try:
        response = requests.post(embedding_url+"/"+"get_embedding_from_input/", json=input_data)

        if response.status_code == 200:
            embedding = response.json()
            
        else:
            logging.info(f"Request failed with status code {res.status_code}")
            logging.info(res.text)  # Print the error message or details if the request fails
            logging.info(f"No embedding")

        payload = {
        "vector": embedding[0],
        "limit": top_k,
        "with_payload": True,
        "filter": {"must": [{"key": "year",
                "range": {"gte": start_year,
                        "lte": end_year}
                }]}
        }

        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(search_client, endpoint1, payload, headers1)
            future2 = executor.submit(search_client, endpoint2, payload, headers2)

        result1 = future1.result()
        result2 = future2.result()
        result1.extend(result2)
        
        sorted_res = sorted(result1, key=lambda x: x['score'], reverse=True)
        logging.info(f"Total res: {str(len(sorted_res))}")

        return render_template("index.html", results=sorted_res)

    except Exception as e:
        return render_template("index.html", error=str(e))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT", 8080))
