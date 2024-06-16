import pandas as pd
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingModel
from google.cloud import storage
from google.oauth2 import service_account
from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from ast import literal_eval

from app.modules.rag import generate_model_response

service_account_path = 'service-account.json'

credentials = service_account.Credentials.from_service_account_file(service_account_path)
vertexai.init(project="hackwarsaw", location="us-central1", credentials=credentials)
model = GenerativeModel(
    "gemini-1.5-flash-001",
)
text_embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")


storage_client = storage.Client(credentials=credentials, project=credentials.project_id)

bucket_name = 'hackwarsaw-fintech-ai-assistant'
csv_filename = 'biznes-gov-pl-embeddings.csv'

bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(csv_filename)
blob.download_to_filename(csv_filename)

df = pd.read_csv('biznes-gov-pl-embeddings.csv', sep=';')
df['content_embedding'] = df['content_embedding'].apply(lambda row: literal_eval(row))
df = df[df['content_embedding'].apply(lambda x: len(x) == 768)]

app = FastAPI()


@app.get("/")
async def docs_redirect():
    return RedirectResponse(url="/docs")

@app.get("/generate", response_model=str)
async def generate(query: str, stream: bool = False):
    return generate_model_response(
        model, text_embedding_model, query, df, stream=stream
    )
