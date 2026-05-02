from google import genai
from groq import Groq
from dotenv import load_dotenv
from difflib import get_close_matches
import database.collections.books as books
import os

# Loading DOTENV
load_dotenv('.env')

# Gemini Client (for embeddings) - (مش رح نستخدمه حالياً)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Groq Client (for responses)
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ✅ Chat function (زي قبل - بدون أي تعديل)
def chat(text):
    response = groq.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": text
            }
        ]
    )

    class Result:
        pass

    result = Result()
    result.text = response.choices[0].message.content
    return result

def chatGemini(text): 
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=text,
    )

    return response

# ✅ embedding
from chromadb.utils import embedding_functions

embedding_function = embedding_functions.DefaultEmbeddingFunction()

def embed(text):
    return embedding_function([text])


# Autocorrect (زي ما هو)
def autocorrect(text):
    result = books.collection.get(include=['metadatas'])

    words_db = []

    # Build vocabulary from Chroma metadata
    for data in result['metadatas']:
        words_db += (data.get('title_en') or '').lower().split()
        words_db += (data.get('category_en') or '').lower().split()
        words_db += (data.get('keywords_en') or '').lower().split()

    words_db = list(set(words_db))  # remove duplicates

    user_words = text.lower().split()
    corrected_words = []

    for word in user_words:
        # keep correct words
        if word in words_db:
            corrected_words.append(word)
            continue

        # skip short words
        if len(word) <= 2:
            corrected_words.append(word)
            continue

        # find closest match
        match = get_close_matches(word, words_db, n=1, cutoff=0.65)

        if match:
            corrected_words.append(match[0])
        else:
            corrected_words.append(word)

    corrected = " ".join(corrected_words)

    # mimic your original return structure
    class Result:
        pass

    result = Result()
    result.text = corrected
    return result