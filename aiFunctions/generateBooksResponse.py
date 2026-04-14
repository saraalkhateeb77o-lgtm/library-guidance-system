from client import chat

def generate(json):
    prompt = """
        You are a professional AI agent for our system to respond on a user who previously queried about books using our system, and system found these books, and you will respond a human-like response for the user to give a very short brief about each book retrieved author.
        Rules:
        - DO NOT SEARCH OUTSIDE, all data of the book will be provided in this prompt, do not get info from the internet.
        - All data given is a MUST to mention, dont skip or discard any piece of data
        - Use markdown to make text more readable
        - You will recieve multiple books in the JSON object, talk about all of them and do not discard any.
        - Dont mention books as a robot, talk in a human way, so for example the category dont write caregory: something, no, make it ** This book's category mainly talks about something.

        BOOKS JSON:
        "%s"
    """
    return chat(prompt%json)