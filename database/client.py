import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(path="./chroma_db")
def autocorrect(text):
    prompt = f"""
You are a library search autocorrector.

Correct spelling mistakes only.

Return ONLY corrected text.

If no correction needed return same text.

Query:
{text}
"""
    return chat(prompt)