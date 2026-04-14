from google import genai
from dotenv import load_dotenv

# Loading DOTENV
load_dotenv('.env')

# Configure Client
client = genai.Client()

# Functions
def chat(text):
    return client.models.generate_content(model="gemini-3-flash-preview", contents=text)

def embed(text): 
    return client.models.embed_content(model='gemini-embedding-001', contents=text)