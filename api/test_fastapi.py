import requests

url = "http://127.0.0.1:8000/get_embedding_from_input/"  # Change the URL to your server's address

input_data = {
    "input_text": "This is a test sentence for embedding generation."
}

response = requests.post(url, json=input_data)
if response.status_code == 200:
    embeddings = response.json()
    print("Received embeddings:", embeddings)
else:
    print("Request failed with status code:", response.status_code)
