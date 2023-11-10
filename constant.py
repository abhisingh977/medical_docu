from dotenv import load_dotenv
from flask import Flask
import os
from google_auth_oauthlib.flow import Flow



load_dotenv('/home/abhishek/abhi/medical_docu/.env')

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
client_secrets_file = os.getenv('ClientSecretsFile')


flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri=os.getenv('redirect_uris')
)
url1 = os.getenv('url1')
api_key1 = os.getenv('api_key1')
collection_name1 = os.getenv('collection_name1')

url2 = os.getenv('url2')
api_key2 = os.getenv('api_key2')
collection_name2 = os.getenv('collection_name2')

PaLM_API_KEY= os.getenv('PaLM_API_KEY')
PaLM_url = os.getenv('PaLM_url')

embedding_url = os.getenv('embedding_url')
top_k = 10

endpoint2 = f'{url2}/collections/{collection_name2}/points/search'
headers2 = {
  'Content-Type': 'application/json',
  'api-key': api_key2
}
collection_name1 = "data"
endpoint1 = f'{url1}/collections/{collection_name1}/points/search'
headers1 = {
  'Content-Type': 'application/json',
  'api-key': api_key1
}
