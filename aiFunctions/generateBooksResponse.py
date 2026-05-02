from client import chat, chatGemini

def generate(json, q):
    prompt = f"""
You are a helpful and friendly assistant that recommends books to users.

User query:
{q}

Books data:
{json}

Instructions:
- Follow the language of the user query strictly.
- If the query is Arabic → respond ONLY in Arabic.
- If the query is English → respond ONLY in English.
- Do NOT mix languages.
- Recommend ALL books provided.
- Do NOT skip any book or any field in any book, exclude only keywords and call number
- Format your response cleanly
- Do NOT copy the description exactly.
- Do NOT show JSON.
- Response in markdown appropriately, Use titles and split books in a clean way, split books into multiple lines not one big text block.
- Write like a human, not like a robot.
"""

    return chatGemini(prompt)