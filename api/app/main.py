import base64
import json
import os
import pandas as pd
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingModel
from google.cloud import storage
from google.oauth2 import service_account
from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse, StreamingResponse
from ast import literal_eval
from typing import Generator

from app.modules.rag import generate_model_response

service_account_key_base64 = os.getenv("SERVICE_ACCOUNT_KEY_BASE64")
if not service_account_key_base64:
    raise ValueError("SERVICE_ACCOUNT_KEY_BASE64 environment variable is not set.")

service_account_key = base64.b64decode(service_account_key_base64).decode("utf-8")
cred_dict = json.loads(service_account_key)

credentials = service_account.Credentials.from_service_account_info(cred_dict)
vertexai.init(project="hackwarsaw", location="us-central1", credentials=credentials)
model = GenerativeModel(
    "gemini-1.5-flash-001",
)
text_embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")


storage_client = storage.Client(credentials=credentials, project=credentials.project_id)

bucket_name = "hackwarsaw-fintech-ai-assistant"
csv_filename = "biznes-gov-pl-embeddings.csv"

bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(csv_filename)
blob.download_to_filename(csv_filename)

df = pd.read_csv("biznes-gov-pl-embeddings.csv", sep=";")
df["content_embedding"] = df["content_embedding"].apply(lambda row: literal_eval(row))
df = df[df["content_embedding"].apply(lambda x: len(x) == 768)]

app = FastAPI()


def get_model():
    return model


def get_text_embedding_model():
    return text_embedding_model


def get_data():
    return df


@app.get("/")
async def docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/generate", response_model=str)
async def generate(
    query: str,
    model: GenerativeModel = Depends(get_model),
    text_embedding_model: TextEmbeddingModel = Depends(get_text_embedding_model),
    data: pd.DataFrame = Depends(get_data),
) -> str:
    return generate_model_response(model, text_embedding_model, query, data)


@app.get("/generate-stream")
async def generate_stream(
    query: str,
    model: GenerativeModel = Depends(get_model),
    text_embedding_model: TextEmbeddingModel = Depends(get_text_embedding_model),
    data: pd.DataFrame = Depends(get_data),
) -> StreamingResponse:
    def stream_response() -> Generator[str, None, None]:
        for response in generate_model_response(
            model, text_embedding_model, query, data, stream=True
        ):
            yield response

    return StreamingResponse(stream_response(), media_type="text/plain")
