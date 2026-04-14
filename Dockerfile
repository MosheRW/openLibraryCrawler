FROM mcr.microsoft.com/playwright/python:v1.58.0-noble

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Credentials are injected at runtime via --env-file .env or -e flags.
# options.yaml is still read for queries and settings.

CMD ["python", "main.py"]
