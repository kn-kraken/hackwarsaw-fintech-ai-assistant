from typing import Generator, Iterable
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from vertexai.language_models import TextEmbeddingModel
from vertexai.generative_models import (
    GenerativeModel,
    GenerationResponse,
    HarmCategory,
    HarmBlockThreshold,
)


GENERATION_CONFIG = {
    "max_output_tokens": 8192,
    "temperature": 0.2,
    "top_p": 0.6,
}

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

PROMPT_TEMPLATE = """
You are an AI assistant specialized in answering questions about starting and running a business in Poland.

Based on the relevant data:
{data}

Formulate an answer to the following user query:
{query}

Your answer must be in Polish.
"""


def get_text_embedding(
    text_embedding_model: TextEmbeddingModel, query: str
) -> np.ndarray:
    query_embedding = text_embedding_model.get_embeddings([query])[0].values
    return np.array(query_embedding)


def search_similar(
    text_embedding_model: TextEmbeddingModel,
    query: str,
    df: pd.DataFrame,
    embedding_column: str,
    top_n: int,
) -> pd.DataFrame:
    embedded_query = get_text_embedding(text_embedding_model, query)

    df["cosine_score"] = df[embedding_column].apply(
        lambda x: cosine_similarity([embedded_query], [np.array(x)])[0][0]
    )

    df = df.sort_values(by="cosine_score", ascending=False)

    return df.head(top_n)


def generate_model_response(
    model: GenerativeModel,
    text_embedding_model: TextEmbeddingModel,
    query: str,
    data: pd.DataFrame,
    top_n: int = 1,
    stream: bool = True,
) -> str | Generator[str, None, None]:
    relevant_data = search_similar(
        text_embedding_model, query, data.copy(), "content_embedding", top_n
    )

    data_text = ""

    for _, row in relevant_data.iterrows():
        data_text += row["article"] + "\n"
        data_text += row["content_clean"] + "\n\n"


    prompt = PROMPT_TEMPLATE.format(data=data_text, query=query)

    if stream:
        responses: Iterable[GenerationResponse] = model.generate_content(
            [prompt],
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS,
            stream=True,
        )

        return (response.text for response in responses)
    else:
        response = model.generate_content(
            [prompt],
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS,
            stream=False,
        )

        return response.text


if __name__ == "__main__":
    from ast import literal_eval
    import vertexai

    df = pd.read_csv('biznes-gov-pl-embeddings.csv', sep=';')
    df['content_embedding'] = df['content_embedding'].apply(lambda row: literal_eval(row))
    df = df[df['content_embedding'].apply(lambda x: len(x) == 768)]

    vertexai.init(project="hackwarsaw", location="us-central1")
    model = GenerativeModel(
        "gemini-1.5-flash-001",
    )

    text_embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")

    query = "Jak założyć firmę w Polsce?"
    response = generate_model_response(model, text_embedding_model, query, df, stream=False)
    print(response)

    # for response in generate_model_response(model, text_embedding_model, query, df):
    #     print(response)
