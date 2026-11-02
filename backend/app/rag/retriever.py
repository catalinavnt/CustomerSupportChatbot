import os
from pathlib import Path

import chromadb
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parents[2]

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

MAX_DISTANCE = 1.2


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


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    collection = client.get_collection(
        name="customer_support"
    )

    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    retrieved = []

    for i in range(len(results["documents"][0])):
        distance = results["distances"][0][i]

        if distance > MAX_DISTANCE:
            continue

        retrieved.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "distance": distance
        })

    return retrieved


if __name__ == "__main__":
    query = input("Question: ")

    results = retrieve(query)

    if not results:
        print("\nNo relevant information found.")
    else:
        for index, result in enumerate(results, start=1):
            print(f"\nResult {index}")
            print(f"Source: {result['source']}")
            print(f"Distance: {result['distance']}")
            print(result["text"])

    input("\nPress Enter to exit...")