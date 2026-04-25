from google import genai
from groq import Groq
from dotenv import load_dotenv
from difflib import get_close_matches
import json
import os

# Loading DOTENV
load_dotenv('.env')

# Gemini Client (for embeddings)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Groq Client (for responses)
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))


# Functions
def chat(text):
    response = groq.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": text}
        ]
    )

    class Result:
        pass

    result = Result()
    result.text = response.choices[0].message.content
    return result


def embed(text):
    return client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )


def autocorrect(text):
    with open("books.json", "r", encoding="utf-8") as f:
        books = json.load(f)

    words_db = []

    # build words database from title + category + keywords
    for book in books:
        words_db += book["title"].lower().split()
        words_db += book["category"].lower().split()

        for kw in book["keywords"]:
            words_db += kw.lower().split()

    # remove duplicates
    words_db = list(set(words_db))

    user_words = text.lower().split()
    corrected_words = []

    for word in user_words:

        # if word is already correct
        if word in words_db:
            corrected_words.append(word)
            continue

        # if word is too short
        if len(word) <= 2:
            corrected_words.append(word)
            continue

        # search similar word
        match = get_close_matches(word, words_db, n=1, cutoff=0.65)

        if match:
            corrected_words.append(match[0])
        else:
            corrected_words.append(word)

    corrected = " ".join(corrected_words)

    class Result:
        pass

    result = Result()
    result.text = corrected
    return result