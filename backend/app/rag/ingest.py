import os
from pathlib import Path

import chromadb
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = BACKEND_DIR / "knowledge"

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "nomic-embed-text"
)

CHROMA_PATH = BACKEND_DIR / os.getenv(
    "CHROMA_PATH",
    "data/chroma"
)


def get_embedding(text: str) -> list[float]:
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/embed",
        json={
            "model": EMBEDDING_MODEL,
            "input": text
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["embeddings"][0]


def split_markdown_into_chunks(text: str, source: str) -> list[dict]:
    lines = text.splitlines()

    chunks = []
    current_lines = []
    chunk_index = 0

    for line in lines:
        if line.startswith("## ") and current_lines:
            chunk_text = "\n".join(current_lines).strip()

            if chunk_text:
                chunks.append({
                    "id": f"{source}-{chunk_index}",
                    "text": chunk_text,
                    "source": source
                })

                chunk_index += 1

            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        chunk_text = "\n".join(current_lines).strip()

        if chunk_text:
            chunks.append({
                "id": f"{source}-{chunk_index}",
                "text": chunk_text,
                "source": source
            })

    return chunks


def load_documents() -> list[dict]:
    documents = []

    for file_path in KNOWLEDGE_DIR.glob("*.md"):
        text = file_path.read_text(encoding="utf-8")

        chunks = split_markdown_into_chunks(
            text=text,
            source=file_path.name
        )

        documents.extend(chunks)

    return documents


def ingest():
    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    try:
        client.delete_collection(
            name="customer_support"
        )
    except ValueError:
        pass

    collection = client.create_collection(
        name="customer_support"
    )

    documents = load_documents()

    for document in documents:
        embedding = get_embedding(document["text"])

        collection.upsert(
            ids=[document["id"]],
            documents=[document["text"]],
            embeddings=[embedding],
            metadatas=[
                {
                    "source": document["source"]
                }
            ]
        )
        print(
            f'Indexed: {document["id"]} '
            f'({document["source"]})'
        )



if __name__ == "__main__":
    ingest()
