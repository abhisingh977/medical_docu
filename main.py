from flask import Flask, request,jsonify, render_template, redirect, session, abort
from google.oauth2 import id_token
from constant import flow, top_k, GOOGLE_CLIENT_ID, endpoint1,endpoint2, embedding_url, headers1, headers2, endpoint3, headers3
from pip._vendor import cachecontrol
from threading import Thread
import google.auth.transport.requests
import io
import time
import os
import json
import uuid
from google.cloud import storage, firestore
from function import request_to_sentence_embedding, search_client, login_is_required, make_request, get_llm_response
import requests
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import logging
# from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
load_dotenv('.env')
db = firestore.Client(project="medical-docu")
app = Flask("medical-docu")
app.config['TIMEOUT'] = 600
app.secret_key = os.environ.get('ClientSecret')
user_collection = db.collection("users")
# CORS(app)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

@app.route('/anesthesia')
def anesthesia():
    return render_template('anesthesia.html')

@app.route('/gynecology')
def gynecology():
    return render_template('gynecology.html')

@app.route("/")
def index():
    try:
        Thread(target=make_request, args=(embedding_url,)).start()
    except:
        pass
    if "google_id" in session:
        # User is already logged in, redirect to the main page
        return redirect("/authed_user")

    return render_template("login_page.html")

@app.route("/no_login")
def no_login():
    return render_template("channel.html")

@app.route("/authed_user")
@login_is_required
def authed_user():
    return render_template("channel.html")

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/logout")
def logout():
    session.clear()
    return render_template("login_page.html")

@app.route("/callback")
def callback():

    https_authorization_url = request.url.replace('http://', 'https://')
    flow.fetch_token(authorization_response=https_authorization_url)
    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["given_name"] = id_info.get("given_name")
    session["family_name"] = id_info.get("family_name")
    session["email"] = id_info.get("email")
    session["locale"] = id_info.get("locale")

    doc_ref = user_collection.document(id_info.get("sub"))
    doc = doc_ref.get()
    if doc.exists:
        field_value = doc.get("count")
        doc_ref.update({"count": field_value+1})
    else:
        doc_ref.set({"given_name": id_info.get("given_name"), "family_name": id_info.get("family_name"),
        "email": id_info.get("email"), "locale":id_info.get("locale"),"picture": id_info.get("picture"), "count":1 })

    return redirect("/authed_user")

@app.route('/llm')
def api1():
    # Access user input from the request
    user_input = request.args.get('input')
    specialization = request.args.get('specialization')
    llm_res = get_llm_response(user_input, specialization)
    # Call API 1 with user input and return the response
    # Replace the following line with your API 1 call
    api1_response = {"data": f"{llm_res}"}
    return jsonify(api1_response)

@app.route('/search')
def api2():
    # Access user input from the request
    input_text = request.args.get('input')
    if len(input_text) < 30:
        input_text = get_llm_response(input_text, specialization="anesthesia",max_output_tokens=40)

    print(input_text)
    start_year = int(request.args.get('sy'))
    end_year = int(request.args.get('ey'))

    # Parse options parameter into a list
    options = request.args.get('options')
    if options:
        options_list = options.split(',')
    else:
        options_list = []

    google_id = session.get("google_id")
    if google_id:
        doc_ref = user_collection.document(session["google_id"])
    else:
        doc_ref = user_collection.document("unknown")
    
    current_timestamp = time.time()
    activity = doc_ref.collection("activity")
    activity = activity.document(str(current_timestamp))
    activity.set({"specialization":"anesthesia","start_year": start_year,"end_year": end_year,"input_text": str(input_text), "time": current_timestamp, "selected books": options_list})        
    
    chunks = input_text.lower()
    input_data = {
    "input_text": chunks
    }

    try:
        response = request_to_sentence_embedding(embedding_url+"/"+"get_embedding_from_input/", input_data)
        if response.status_code == 200:
            embedding = response.json()  
        else:
            logging.info(f"Request failed with status code {response.status_code}")
            logging.info(response.text)  # Print the error message or details if the request fails
            logging.info(f"No embedding")
        if len(options_list) != 0: 
            payload = {
            "vector": embedding[0],
            "limit": top_k,
            "with_payload": True,
            "filter": {"must": [{"key": "year",
                    "range": {"gte": start_year,
                            "lte": end_year}
                    },{
                    "key": "book_name",
                    "match": {
                        "any": options_list
                    }
                    }]}
            }
        else:
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
            future1 = executor.submit(search_client, endpoint1, payload, headers1, specialization="anesthesia")
            future2 = executor.submit(search_client, endpoint2, payload, headers2,specialization="anesthesia")

        result1 = future1.result()
        result2 = future2.result()
        result1.extend(result2)
        
        sorted_res = sorted(result1, key=lambda x: x['score'], reverse=True)
        logging.info(f"Total res: {str(len(sorted_res))}")
        
        # Call API 2 with user input and return the response
        # Replace the following line with your API 2 call
        api2_response = {"data": f"{json.dumps(sorted_res)}"}

        return jsonify(api2_response)

    except Exception as e:
        return render_template("server_limit.html")

@app.route('/upload_chunk', methods=['POST'])
def upload_chunk():
    try:
        chunk = request.files['document'].read()
        save_chunk(chunk)
        return render_template("pdf_uploaded.html")
    except Exception as e:
        return render_template("server_limit.html")


def upload_to_gcs(file_data):
    client = storage.Client()
    CHUNK_SIZE = 1024 * 1024 * 30
    bucket = client.get_bucket("user_uploaded_files")
    blob = bucket.blob(f"{uuid.uuid4().hex}.pdf", chunk_size=CHUNK_SIZE)
    blob.upload_from_file(file_data, content_type='multipart/form-data')

def save_chunk(chunk):
    if 'file_data' not in save_chunk.__dict__:
        save_chunk.file_data = io.BytesIO()
    save_chunk.file_data.write(chunk)

    save_chunk.file_data.seek(0)
    upload_to_gcs(save_chunk.file_data)

@app.route('/upload')
def upload():
    
    if "google_id" in session:
        # User is already logged in, redirect to the main page
        return render_template('upload.html')
    
    return render_template("login_page.html")


@app.route('/search2')
def api3():
    # Access user input from the request
    input_text = request.args.get('input')

    if len(input_text) < 30:
        input_text = get_llm_response(input_text, specialization="gynecology",max_output_tokens=40)

    start_year = int(request.args.get('sy'))
    end_year = int(request.args.get('ey'))

    # Parse options parameter into a list
    options = request.args.get('options')
    if options:
        options_list = options.split(',')
    else:
        options_list = []

    google_id = session.get("google_id")
    if google_id:
        doc_ref = user_collection.document(session["google_id"])
    else:
        doc_ref = user_collection.document("unknown")
    
    current_timestamp = time.time()
    activity = doc_ref.collection("activity")
    activity = activity.document(str(current_timestamp))
    activity.set({"specialization":"gynecology","start_year": start_year,"end_year": end_year,"input_text": str(input_text), "time": current_timestamp, "selected books": options_list})        
    
    chunks = input_text.lower()
    input_data = {
    "input_text": chunks
    }

    try:
        response = request_to_sentence_embedding(embedding_url+"/"+"get_embedding_from_input/", input_data)
        if response.status_code == 200:
            embedding = response.json()  
        else:
            logging.info(f"Request failed with status code {response.status_code}")
            logging.info(response.text)  # Print the error message or details if the request fails
            logging.info(f"No embedding")
        if len(options_list) != 0: 
            payload = {
            "vector": embedding[0],
            "limit": 10,
            "with_payload": True,
            "filter": {"must": [{"key": "year",
                    "range": {"gte": start_year,
                            "lte": end_year}
                    },{
                    "key": "book_name",
                    "match": {
                        "any": options_list
                    }
                    }]}
            }
        else:
            payload = {
            "vector": embedding[0],
            "limit": 10,
            "with_payload": True,
            "filter": {"must": [{"key": "year",
                    "range": {"gte": start_year,
                            "lte": end_year}
                    }]}
            }

        result = search_client(endpoint3, payload, headers3,specialization="gynecology")

        sorted_res = sorted(result, key=lambda x: x['score'], reverse=True)
        logging.info(f"Total res: {str(len(sorted_res))}")
        
        # Call API 2 with user input and return the response
        # Replace the following line with your API 2 call
        api2_response = {"data": f"{json.dumps(sorted_res)}"}

        return jsonify(api2_response)

    except Exception as e:
        return render_template("server_limit.html")

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0", port=os.getenv("PORT", 8080))
