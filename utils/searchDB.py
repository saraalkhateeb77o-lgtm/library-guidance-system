from client import embed
import database.collections.books as books
from dotenv import load_dotenv
import os
from difflib import get_close_matches

load_dotenv('.env')


def is_arabic(text):
    return any('\u0600' <= c <= '\u06FF' for c in text)


def normalize_arabic(text):
    text = text.lower()

    if text.startswith("ال"):
        text = text[2:]

    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ة", "ه")
    text = text.replace("ى", "ي")

    return text


def arabic_autocorrect(term):
    result = books.collection.get(include=['metadatas'])

    words = []

    for data in result['metadatas']:
        words += (data.get('title_ar') or '').split()
        words += (data.get('keywords_ar') or '').split()

    words = list(set(words))

    match = get_close_matches(term, words, n=1, cutoff=0.7)

    return match[0] if match else term


def search(term, results):

    # Arabic search (no embedding)
    if is_arabic(term):
        result = books.collection.get(include=['metadatas'])

        docs = []

        original_term = term
        corrected_term = arabic_autocorrect(term)

        normalized_term = normalize_arabic(corrected_term)

        for i in range(len(result['ids'])):
            data = result['metadatas'][i]

            text = (
                (data.get('title_ar') or '') +
                (data.get('description_ar') or '') +
                (data.get('keywords_ar') or '') +
                (data.get('topic_ar') or '')
            )

            normalized_text = normalize_arabic(text)

            if normalized_term in normalized_text:
                docs.append({
                    "id": result['ids'][i],
                    "data": data,
                    "score": 1
                })

        if not docs:
            return {
                "message": "ما لقينا كتب لهاد البحث جربي كلمة ثانية",
                "fixedQuery": corrected_term if corrected_term != original_term else None,
                "results": []
            }

        response = {
            "results": docs[:results]
        }

        if corrected_term != original_term:
            response["fixedQuery"] = corrected_term

        return response

    # =========================
    # 🔵 English search + fallback
    # =========================

    try:
        termEmbedding = embed(term)[0]

        result = books.collection.query(
            query_embeddings=[termEmbedding],
            n_results=20,
            include=['metadatas', 'distances']
        )

    except Exception as e:
        print("Embedding failed:", e)

        result = books.collection.get(include=['metadatas'])

        docs = []

        for i in range(len(result['ids'])):
            data = result['metadatas'][i]

            text = (
                (data.get('title_en') or '') +
                (data.get('description_en') or '') +
                (data.get('keywords') or '') +
                (data.get('topic_en') or '')
            ).lower()

            if term.lower() in text:
                docs.append({
                    "id": result['ids'][i],
                    "data": data,
                    "score": 1
                })

        return docs[:results]

    docs = []

    distances = result['distances'][0]
    metadatas = result['metadatas'][0]
    ids = result['ids'][0]

    if not distances:
        return []

    avg = sum(distances) / len(distances)
    best = distances[0]

    threshold = (best + avg) / 2 + 0.05

    if len(term.split()) == 1:
        threshold += 0.05

    for i in range(len(ids)):
        if distances[i] <= threshold:
            docs.append({
                'id': ids[i],
                'data': metadatas[i],
                'distance': distances[i]
            })

    if not docs:
        for i in range(min(3, len(ids))):
            docs.append({
                'id': ids[i],
                'data': metadatas[i],
                'distance': distances[i]
            })

    term_lower = term.lower()
    expanded_terms = [term_lower]

    scored_docs = []

    for doc in docs:
        data = doc['data']

        title = data.get('title_en') or data.get('title_ar') or ''
        keywords_raw = data.get('keywords') or data.get('keywords_ar') or ''
        category = data.get('topic_en') or data.get('topic_ar') or ''

        title = title.lower()
        category = category.lower()
        keywords_list = keywords_raw.lower().split(',')

        score = 1 - doc['distance']

        if any(t in title for t in expanded_terms):
            score += 0.3

        if any(t in kw for t in expanded_terms for kw in keywords_list):
            score += 0.2

        if any(t in category for t in expanded_terms):
            score += 0.15

        if any(t in word for t in expanded_terms for word in title.split()):
            score += 0.1

        doc['score'] = score

        min_score = max(0.35, (1 - avg) * 0.7)

        if score >= min_score:
            scored_docs.append(doc)

    # 🔥 ONLY ADDITION (Hybrid improvement)
    if len(scored_docs) < 2:
        all_data = books.collection.get(include=['metadatas'])

        for i in range(len(all_data['ids'])):
            data = all_data['metadatas'][i]

            text = (
                (data.get('title_en') or '') +
                (data.get('description_en') or '') +
                (data.get('keywords') or '') +
                (data.get('topic_en') or '')
            ).lower()

            if term.lower() in text:
                already = any(d['id'] == all_data['ids'][i] for d in scored_docs)

                if not already:
                    scored_docs.append({
                        "id": all_data['ids'][i],
                        "data": data,
                        "score": 0.4
                    })

    if not scored_docs:
        scored_docs = docs[:3]

    scored_docs.sort(key=lambda x: x['score'], reverse=True)

    return scored_docs[:results]