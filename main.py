from flask import Flask, request,jsonify, render_template, redirect, session, abort
from google.oauth2 import id_token
from constant import flow, top_k, GOOGLE_CLIENT_ID, endpoint1,endpoint2, embedding_url, headers1, headers2
from pip._vendor import cachecontrol
from threading import Thread
import google.auth.transport.requests
import os
import json
import numpy as np
from function import request_to_sentence_embedding, search_client, login_is_required, make_request, get_llm_response
import requests
from concurrent.futures import ThreadPoolExecutor
from google.cloud import firestore
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
load_dotenv('.env')
db = firestore.Client(project="medical-docu")
app = Flask("medical-docu")
app.config['TIMEOUT'] = 600
app.secret_key = os.environ.get('ClientSecret')

@app.route("/")
def index():
    try:
        Thread(target=make_request, args=(embedding_url,)).start()
    except:
        pass
    return render_template("index.html")


@login_is_required
@app.route("/authed_user")
def authed_user():
    return render_template("index.html")

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")

@app.route("/callback")
def callback():

    logging.info("URL")
    logging.info(request.url)
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

    doc_ref = db.collection("users").document(id_info.get("sub"))
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
    llm_res = get_llm_response(user_input)
    # Call API 1 with user input and return the response
    # Replace the following line with your API 1 call
    api1_response = {"data": f"{llm_res}"}
    return jsonify(api1_response)

@app.route('/search')
def api2():
    # Access user input from the request
    input_text = request.args.get('input')
    start_year = int(request.args.get('sy'))
    end_year = int(request.args.get('ey'))
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
        
        # Call API 2 with user input and return the response
        # Replace the following line with your API 2 call
        api2_response = {"data": f"{json.dumps(sorted_res)}"}

        return jsonify(api2_response)

    except Exception as e:
        return render_template("server_limit.html")


if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0", port=os.getenv("PORT", 8080))
