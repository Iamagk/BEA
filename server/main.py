from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .model import analyze_text


class AnalyzeRequest(BaseModel):
    text: str
    sender: str | None = None


class ReportRequest(BaseModel):
    text: str
    sender: str | None = None
    note: str | None = None


app = FastAPI(title="PhishGuard Prototype API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the simple frontend at /ui (files are in ../frontend)
static_dir = Path(__file__).resolve().parents[1] / "frontend"
if static_dir.exists():
    app.mount("/ui", StaticFiles(directory=str(static_dir), html=True), name="frontend")


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    result = analyze_text(req.text, req.sender)
    return {"ok": True, "result": result}


@app.post("/report")
async def report(r: ReportRequest):
    # In a real app store/report the sample, notify analysts, etc.
    return {"ok": True, "message": "Thanks — report received (prototype)."}
