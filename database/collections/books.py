from database.client import client
import json

collection = client.get_or_create_collection(name="books")

def add(data, embeddings):
    collection.add(
        ids=[data['id']],
        embeddings=[embeddings],
        metadatas=[data],
    )

def get(id):
    result = collection.get(ids=[id], include=['embeddings', 'metadatas'])
    doc = {
        'id': result['ids'][0],
        'data': result['metadatas'][0],
        'embeddings': result['embeddings'][0]
    }
    return doc

def clear():
    collection.delete(where={"id": {"$ne": ""}})