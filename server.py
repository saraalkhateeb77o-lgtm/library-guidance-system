from dotenv import load_dotenv
from fastapi import FastAPI, Response, Query, HTTPException
from typing import Optional
import json

import database.collections.books as books
from utils.searchDB import search
from aiFunctions.generateBooksResponse import generate as generateHumanResponse

# Load env
load_dotenv('.env')

app = FastAPI()


@app.get("/")
def root():
    return {"message": "API is running"}


@app.get("/search")
def search_books(
    q: str = Query(..., description="Search query"),
    limit: int = Query(5, ge=1, le=20)
):
    try:
        results = search(q, limit)

        text = generateHumanResponse(json.dumps(results)).text

        if not type(text) == str:
            raise HTTPException(status_code=500, detail='Unexpected error')

        return Response(
            content=text,
            media_type="text/markdown",
            status_code=200
        )

    except Exception as e:
        print("ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )