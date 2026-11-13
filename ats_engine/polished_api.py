from fastapi import FastAPI
from fastapi.responses import JSONResponse

from ats_engine.polished_decision_service import safe_decide

app = FastAPI(title="Zecpath Decision API", version="1.1")

HTTP_FOR = {"BAD_REQUEST": 400, "UNKNOWN_ROUND": 400, "INVALID_SCORE": 422,
            "SCORE_OUT_OF_RANGE": 422, "NO_ROUND_SCORES": 422, "INTERNAL_ERROR": 500}


@app.post("/api/v1/decisions")
def decisions(payload: dict):
    result = safe_decide(payload)
    status = HTTP_FOR.get(result.get("error", {}).get("code"), 200)
    return JSONResponse(status_code=status, content=result)