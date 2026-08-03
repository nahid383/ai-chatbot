FROM python:3.12-slim

WORKDIR /app

# System deps needed by psycopg2 and some chromadb/pypdf transitive deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/uploads /app/chroma_data

EXPOSE 8000

# In production, no --reload. Railway/Render set $PORT; default to 8000 locally.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
