from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
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
    return {
        "status": "success",
        "data": {
            "message": "API is running"
        }
    }


@app.get("/search")
def search_books(
    q: str = Query(..., description="Search query"),
    limit: int = Query(15, ge=1, le=20)
):
    try:
        original_q = q
        fixed_query = None

        # Autocorrect first
        corrected = autocorrect(q).text.strip()

        if corrected.lower() != q.lower():
            fixed_query = corrected
            q = corrected

        # Search after correction
        results = search(q, limit)

        # Final filter (only good results)
        min_score = 0.18
        if len(original_q.split()) >= 4:
            min_score = 0.12

        results = [r for r in results if r["score"] >= min_score]

        # No results
        if len(results) == 0:
            payload = {
                "status": "fail",
                "data": {
                    "message": "No relevant books found."
                }
            }

            if fixed_query:
                payload["data"]["fixedQuery"] = fixed_query

            return JSONResponse(content=payload, status_code=200)

        # Build success response
        data = {
            "json": results
        }

        if fixed_query:
            data["fixedQuery"] = fixed_query

        # Try AI text generation
        try:
            generated_text = generateHumanResponse(json.dumps(results)).text
            data["text"] = generated_text

        except Exception as e:
            print("AI Failed:", e)

        return JSONResponse(
            content={
                "status": "success",
                "data": data
            },
            status_code=200
        )

    except Exception as e:
        print("ERROR:", e)

        return JSONResponse(
            content={
                "status": "error",
                "message": "Internal server error"
            },
            status_code=500
        )