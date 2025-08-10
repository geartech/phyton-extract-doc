"""
API mínima com FastAPI para receber um .docx (upload) e retornar a extração.
- POST /extract -> JSON estruturado
- POST /extract?format=txt -> texto puro (text/plain)
"""

import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from app.parser import extract_docx, to_markdown, md_to_text, to_html

app = FastAPI(title="DOCX Extractor API")

# Libera CORS (útil para testar do frontend/localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrinja depois se precisar
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"ok": True, "docs": "/docs", "endpoints": ["/extract (python-docx)", "/extract/mammoth"]}

# === python-docx (JSON estruturado) ===
@app.post("/extract")  # alias
@app.post("/extract/python-docx")
async def extract_python_docx(file: UploadFile = File(...), format: str | None = None):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(400, "Envie um arquivo .docx")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    try:
        data = extract_docx(tmp_path)
    finally:
        os.remove(tmp_path)

    if (format or "").lower() in {"txt", "text", "plain"}:
        return Response(content=data["raw_text"], media_type="text/plain; charset=utf-8")
    return data

# === Mammoth (MD/HTML/TXT limpos p/ IA) ===
@app.post("/extract/mammoth")
async def extract_mammoth(file: UploadFile = File(...), fmt: str = "md"):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(400, "Envie um arquivo .docx")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    try:
        f = fmt.lower()
        if f in ("md", "markdown"):
            res = to_markdown(tmp_path)
            return {"markdown": res["markdown"], "text": md_to_text(res["markdown"]), "warnings": res["warnings"]}
        if f == "html":
            return to_html(tmp_path)
        if f in ("txt", "text", "plain"):
            res = to_markdown(tmp_path)
            return Response(content=md_to_text(res["markdown"]), media_type="text/plain; charset=utf-8")
        raise HTTPException(400, "fmt inválido. Use md|html|txt")
    finally:
        os.remove(tmp_path)