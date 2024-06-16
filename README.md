# Hackwarsaw FinTech AI Assistant

This code contains code for a REST API that serves the AI Assistant for the Hackwarsaw FinTech project. The AI Assistant is a chatbot capable of Retrieval Augmented Generation (RAG) and is built using the FastAPI framework and VertexAI services from Google Cloud.

## Running the code

The easiest way to run this application is via the provided Dockerfile.

First, change to the API directory:

```bash
cd api
```

Then, build the Docker image:

```bash
docker build -t hackwarsaw-fintech-ai-assistant .
```

Finally, run the Docker container:

```bash
docker run -p 8000:80 -e SERVICE_ACCOUNT_KEY_BASE64=<value> hackwarsaw-fintech-ai-assistant
```

Replace `<value>` with the base64 encoded service account key for this application that makes it possible to use GCP services.

## Repository structure

The repository is structured as follows:
- `api/`: Contains the code for the REST API.
- `scraper/`: Contains scripts used for scraping data from the web.
