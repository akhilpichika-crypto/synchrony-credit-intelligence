from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(MODEL_NAME)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100):
    """
    Split document text into overlapping character-based chunks.
    """

    if not text or not text.strip():
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def generate_embedding(text: str):
    """
    Convert text into a 384-dimensional embedding vector.
    """

    embedding = embedding_model.encode(text)

    return embedding.tolist()