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

    for book in books:
        words_db += book["title"].lower().split()

    user_words = text.lower().split()
    corrected_words = []

    for word in user_words:

        if word in words_db:
            corrected_words.append(word)
            continue

        match = get_close_matches(word, words_db, n=1, cutoff=0.90)

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