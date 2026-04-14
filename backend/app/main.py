from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import time

from app.models.schemas import QueryRequest
from app.services.pageindex_service import (
    upload_document,
    get_tree,
    check_status
)
from app.services.rag_pipeline import run_rag

app = FastAPI()

# CORS (required for React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def health():
    return {"status": "running"}


# 🔥 UPLOAD ENDPOINT
@app.post("/upload")
def upload(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Upload to PageIndex
        doc_id = upload_document(file_path)

        # Wait for indexing
        while True:
            status = check_status(doc_id)

            if status == "completed":
                break
            elif status == "failed":
                raise HTTPException(status_code=500, detail="Indexing failed")

            time.sleep(3)

        return {"doc_id": doc_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔥 QUERY ENDPOINT
@app.post("/query")
def query(req: QueryRequest):
    try:
        tree = get_tree(req.doc_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid doc_id")

    answer = run_rag(req.query, tree)
    return {"answer": answer}