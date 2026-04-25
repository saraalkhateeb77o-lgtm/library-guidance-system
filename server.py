from dotenv import load_dotenv
from fastapi import FastAPI, Response, Query, HTTPException
import json

from utils.searchDB import search
from aiFunctions.generateBooksResponse import generate as generateHumanResponse
from client import autocorrect

# Load environment variables
load_dotenv(".env")

# FastAPI app
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

        # Remove weak results
        results = [r for r in results if r["score"] >= 0.08]

        # If no results or first result is weak -> try autocorrect
        if len(results) == 0 or results[0]["score"] < 0.35:

            fixed_q = autocorrect(q).text.strip()

            if fixed_q.lower() != q.lower():
                suggestion = f"Did you mean: {fixed_q}\n\n"
                q = fixed_q
                results = search(q, limit)

                # Remove weak results after autocorrect
                results = [r for r in results if r["score"] >= 0.08]

        # If still no results
        if len(results) == 0:
            return Response(
                content=suggestion + "No relevant books found.",
                media_type="text/plain",
                status_code=200
            )

        # Try AI response
        try:
            text = generateHumanResponse(json.dumps(results)).text

        except Exception as e:
            print("Gemini Failed:", e)

            text = "📚 Books Found:\n\n"

            for i, book in enumerate(results, 1):
                data = book["data"]

                text += f"{i}. {data['title']}\n"
                text += f"👤 Author: {data['author']}\n"
                text += f"📂 Category: {data['category']}\n"
                text += f"📍 Location: {data['location']}\n"
                text += f"📝 {data['description']}\n"
                text += f"⭐ Score: {round(book['score'], 2)}\n\n"

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