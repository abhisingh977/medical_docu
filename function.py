from get_relevant_page import get_relevant_text
from flask import session, abort
import json
import time
from google.cloud import storage
import requests
import logging
import io
import uuid
import os
from constant import PaLM_url

# Configure logging
logging.basicConfig(level=logging.INFO)

GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")


def make_request(embedding_url):
    try:
        response = requests.get(embedding_url, timeout=1)
    except:
        pass


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


def request_with_retry(retries=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(retries):
                try:
                    response = func(*args, **kwargs)
                    if response.status_code in (
                        200,
                        201,
                    ):  # Customize based on your requirements
                        return response
                except requests.RequestException as e:
                    print(f"Request failed: {e}")
                time.sleep(delay)
            return None  # If all retries fail, return None or handle as needed

        return wrapper

    return decorator


@request_with_retry()
def request_to_qrand(endpoint, data, headers, timeout=60):
    res = requests.post(
        endpoint, data=json.dumps(data), headers=headers, timeout=timeout
    )
    return res


def search_client(endpoint, payload, headers, specialization):
    logging.info(f"Making request to endpoint: {endpoint}")
    res = request_to_qrand(
        endpoint=endpoint, data=payload, headers=headers, timeout=500
    )
    if res.status_code == 200:  # Assuming a successful response has status code 200
        res = res.json()  # Get the response data in JSON format
        res = res["result"]
        res = sorted(res, key=lambda x: x["score"], reverse=True)
        res = get_relevant_text(res, specialization)
        logging.info(f"Successful return to request to endpoint: {endpoint}")
    # Process the data as needed
    else:
        logging.info(f"Request failed with status code {res.status_code}")
        logging.info(
            res.text
        )  # Print the error message or details if the request fails
        logging.info(f"{endpoint} did not returned respose in time.")

    return res


@request_with_retry()
def request_to_sentence_embedding(embedding_url, input_data):
    response = requests.post(embedding_url, json=input_data, timeout=500)
    return response


def get_llm_response(input_text: str, specialization: str, max_output_tokens=800):
    json = {
        "prompt": {
            "text": f"For the text that is inside '' generate factual summary in context of medical field especially in context of {specialization}: '{input_text}'"
        },
        "temperature": 0.0,
        "candidate_count": 1,
        "top_k": 40,
        "top_p": 0.95,
        "max_output_tokens": max_output_tokens,
        "stop_sequences": [],
        "safety_settings": [
            {"category": "HARM_CATEGORY_DEROGATORY", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_TOXICITY", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_VIOLENCE", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUAL", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_MEDICAL", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
        ],
    }
    response = requests.post(PaLM_url, json=json)

    if response.status_code == 200:
        response = response.json()
        return response["candidates"][0]["output"]
    else:
        logging.info("Error in LLM response: %s", response.status_code)
        return "NO response from LLM server"


def upload_to_gcs(file_data):
    client = storage.Client()
    CHUNK_SIZE = 1024 * 1024 * 30
    bucket = client.get_bucket("user_uploaded_files")
    blob = bucket.blob(f"{uuid.uuid4().hex}.pdf", chunk_size=CHUNK_SIZE)
    blob.upload_from_file(file_data, content_type="multipart/form-data")


def save_chunk(chunk):
    if "file_data" not in save_chunk.__dict__:
        save_chunk.file_data = io.BytesIO()
    save_chunk.file_data.write(chunk)

    save_chunk.file_data.seek(0)
    upload_to_gcs(save_chunk.file_data)


def upload_blob_with_timeout(
    bucket_name, source_file_name, destination_blob_name, custom_timeout=60 * 60 * 5
):
    # Use the function
    # replace with your bucket name

    storage_client = storage.Client.from_service_account_json(
        GOOGLE_APPLICATION_CREDENTIALS
    )
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name, timeout=custom_timeout)
    blob.make_public()
    logging.info(f"File {source_file_name} uploaded to {destination_blob_name}.")


def download_html_from_gcs(bookmark_path):
    # Use the appropriate GCS bucket and download logic
    bucket_name = "user_bookmark_html"
    blob_name = f"{bookmark_path}"
    storage_client = storage.Client.from_service_account_json(
        GOOGLE_APPLICATION_CREDENTIALS
    )
    # Download the HTML content from GCS
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    html_content = blob.download_as_text()
    os.remove(blob_name)
    return html_content