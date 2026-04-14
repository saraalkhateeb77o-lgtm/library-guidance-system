import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(path="./chroma_db")