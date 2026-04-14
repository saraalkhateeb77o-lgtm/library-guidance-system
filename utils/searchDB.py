from client import embed
import database.collections.books as books

def search(term, results):
    termEmbedding = embed(term).embeddings[0].values

    result = books.collection.query(
        query_embeddings = [termEmbedding],
        n_results = results,
        # include = ['embeddings', 'metadatas']
    )

    docs = []

    for i in range(len(result['ids'])):
        doc = {
            'id': result['ids'][i],
            'data': result['metadatas'][i],
            # 'embeddings': result['embeddings'][i]
        }
        docs.append(doc)

    return docs