from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import json

from utils.searchDB import search
from aiFunctions.generateBooksResponse import generate as generateHumanResponse
from client import autocorrect
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv(".env")

# FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    limit: int = Query(15, ge=1, le=20),
    humanize: bool = Query(False)
):
    try:
        original_q = q
        fixed_query = None

        # 🔥 Autocorrect (for English mainly)
        corrected = autocorrect(q).text.strip()

        if corrected.lower() != q.lower():
            fixed_query = corrected
            q = corrected

        # 🔍 Search
        results = search(q, limit)

        # ======================================
        # 🔥 Handle Arabic response (NEW PART)
        # ======================================
        if isinstance(results, dict):

            # ❌ No results
            if "message" in results:
                return JSONResponse(
                    content={
                        "status": "fail",
                        "data": {
                            "message": results["message"],
                            "fixedQuery": results.get("fixedQuery")
                        }
                    },
                    status_code=200
                )

            # ✅ Success
            data = {
                "json": results["results"]
            }

            if results.get("fixedQuery"):
                data["fixedQuery"] = results["fixedQuery"]

            # ✅ AI response (FIXED HERE)
            try:
                generated_text = generateHumanResponse(
                    json.dumps(results["results"], ensure_ascii=False),
                    q
                ).text
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

        # ======================================
        # 🔵 ENGLISH FLOW (UNCHANGED)
        # ======================================

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
            "json": results,
        }

        if fixed_query:
            data["fixedQuery"] = fixed_query

        # ✅ AI response (FIXED HERE TOO)
        try:
            if humanize:
                generated_text = generateHumanResponse(
                    json.dumps(results, ensure_ascii=False),
                    q
                ).text
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