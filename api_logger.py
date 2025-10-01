# file: app.py
from __future__ import annotations
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

LOG_PATH = "incoming.log"
app = FastAPI(title="Simple Ingest API")

async def _append_log(text: str) -> None:
    # Why: use a thread to avoid blocking the event loop with disk I/O.
    def _write():
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{text}\n")
    await run_in_threadpool(_write)

def _is_nonempty_string(value) -> bool:
    return isinstance(value, str) and value.strip() != ""

@app.post("/ingest")
async def ingest(request: Request) -> JSONResponse:
    ctype = (request.headers.get("content-type") or "").split(";")[0].strip().lower()

    text: str | None = None
    if ctype == "text/plain":
        body = (await request.body()).decode("utf-8", errors="replace")
        text = body if _is_nonempty_string(body) else None
    elif ctype == "application/json":
        data = await request.json()
        candidate = data.get("text")
        text = candidate if _is_nonempty_string(candidate) else None
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide text/plain body or JSON {'text': '...'}",
        )

    if text is None:
        raise HTTPException(
            status_code=400,
            detail="Text must be a non-empty string.",
        )

    try:
        await _append_log(text)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"I/O error: {exc}") from exc
    return JSONResponse({"status": "ok", "written": len(text)})

if __name__ == "__main__":
    # Run: `uvicorn app:app --host 0.0.0.0 --port 8000`
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
