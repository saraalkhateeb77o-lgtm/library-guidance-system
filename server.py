from dotenv import load_dotenv
from fastapi import FastAPI, Response, Query, HTTPException
import json

from utils.searchDB import search
from aiFunctions.generateBooksResponse import generate as generateHumanResponse
from client import autocorrect

load_dotenv(".env")

app = FastAPI()


@app.get("/")
def root():
    return {"message": "API is running"}


@app.get("/search")
def search_books(
    q: str = Query(..., description="Search query"),
    limit: int = Query(15, ge=1, le=20)
):
    try:
        suggestion = ""

        # Search first
        results = search(q, limit)

        # If no results OR weak score -> autocorrect
        if len(results) == 0 or results[0]["score"] < 0.4:

            fixed_q = autocorrect(q).text.strip()

            if fixed_q.lower() != q.lower():
                suggestion = f"Did you mean: {fixed_q}\n\n"
                q = fixed_q
                results = search(q, limit)

        # Try AI response
        try:
            text = generateHumanResponse(json.dumps(results)).text

        except Exception as e:
            print("Gemini Failed:", e)

            text = "Books found:\n\n"

            for i, book in enumerate(results, 1):
                text += f"{i}. {book}\n"

        return Response(
            content=suggestion + text,
            media_type="text/markdown",
            status_code=200
        )

    except Exception as e:
        print("ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )