from dotenv import load_dotenv
import os
from google_auth_oauthlib.flow import Flow

load_dotenv('.env')

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
client_secrets_file = os.environ.get('ClientSecretsFile')

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri=os.environ.get('redirect_uris')
)
url1 = os.environ.get('url1')
api_key1 = os.environ.get('api_key1')
collection_name1 = os.environ.get('collection_name1')

url2 = os.environ.get('url2')
api_key2 = os.environ.get('api_key2')
collection_name2 = os.environ.get('collection_name2')


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
