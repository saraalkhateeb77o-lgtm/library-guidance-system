# from client import embed 
# import database.collections.books as books 
# from dotenv import load_dotenv 
# load_dotenv('.env') 

# def search(term, results): 
#     termEmbedding = embed(term).embeddings[0].values 
#     result = books.collection.query( 
#         query_embeddings = [termEmbedding],
#         n_results = results, 
#         # include = ['embeddings', 'metadatas'] 
#     ) 
#     docs = [] 
#     for i in range(len(result['ids'])): 
#         doc = { 
#             'id': result['ids'][i], 
#             'data': result['metadatas'][i], 
#             # 'embeddings': result['embeddings'][i] 
#         } 
#         docs.append(doc) 

#     return docs

from client import embed
import database.collections.books as books
from dotenv import load_dotenv
import os

load_dotenv('.env')


def search(term, results):
    termEmbedding = embed(term).embeddings[0].values

    result = books.collection.query(
        query_embeddings=[termEmbedding],
        n_results=20,
        include=['metadatas', 'distances']
    )

    docs = []

    distances = result['distances'][0]
    metadatas = result['metadatas'][0]
    ids = result['ids'][0]

    # ✅ adaptive threshold (based on distribution)
    avg = sum(distances) / len(distances)
    best = distances[0]

    threshold = (best + avg) / 2 + 0.05

    # 🔥 loosen threshold for short queries (like "ai")
    if len(term.split()) == 1:
        threshold += 0.05

    for i in range(len(ids)):
        if distances[i] <= threshold:
            docs.append({
                'id': ids[i],
                'data': metadatas[i],
                'distance': distances[i]
            })

    # ✅ fallback if empty
    if not docs:
        for i in range(min(3, len(ids))):
            docs.append({
                'id': ids[i],
                'data': metadatas[i],
                'distance': distances[i]
            })

    # 🔥 QUERY EXPANSION
    term_lower = term.lower()
    expanded_terms = [term_lower]

    if term_lower == "computer":
        expanded_terms += ["software", "technology", "programming", "engineering"]

    elif term_lower == "engine":
        expanded_terms += ["engineering", "mechanical", "machine"]

    elif term_lower == "ai":
        expanded_terms += ["artificial intelligence", "machine learning", "neural networks"]

    # 🔥 SCORING SYSTEM
    scored_docs = []

    for doc in docs:
        title = doc['data'].get('title', '').lower()
        keywords_list = doc['data'].get('keywords', [])
        category = doc['data'].get('category', '').lower()

        score = 1 - doc['distance']  # base semantic score

        # 🔥 boosts
        if any(t in title for t in expanded_terms):
            score += 0.3

        if any(t in kw.lower() for t in expanded_terms for kw in keywords_list):
            score += 0.2

        if any(t in category for t in expanded_terms):
            score += 0.15

        if any(t in word for t in expanded_terms for word in title.split()):
            score += 0.1

        doc['score'] = score

        # 🔥 adaptive score filtering (NOT fixed anymore)
        min_score = max(0.35, (1 - avg) * 0.7)

        if score >= min_score:
            scored_docs.append(doc)

    # ✅ fallback again if over-filtered
    if not scored_docs:
        scored_docs = docs[:3]

    # ✅ final ranking
    scored_docs.sort(key=lambda x: x['score'], reverse=True)

    return scored_docs[:results]