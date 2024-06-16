FROM python:3.11.9-bookworm

WORKDIR /hackwarsaw

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SERVICE_ACCOUNT_KEY_BASE64=""

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
