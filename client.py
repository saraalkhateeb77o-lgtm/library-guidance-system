from google import genai
from dotenv import load_dotenv
from difflib import get_close_matches
import json

# Loading DOTENV
load_dotenv('.env')

# Configure Client
client = genai.Client()


# Functions
def chat(text):
    return client.models.generate_content(
        model="gemini-2.0-flash",
        contents=text
    )


def embed(text):
    return client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )


def autocorrect(text):
    with open("books.json", "r", encoding="utf-8") as f:
        books = json.load(f)

    words_db = []

    # 🔥 build words database from title + category + keywords
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

        # إذا الكلمة صحيحة
        if word in words_db:
            corrected_words.append(word)
            continue

        # إذا قصيرة جدا
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