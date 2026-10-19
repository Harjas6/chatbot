from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from gemini import ask_gemini
from models import ChatReply, ChatRequest
from rag.pdf import process_pdfs

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatReply)
def chat(payload: ChatRequest):
    return ask_gemini(payload.message, payload.previous_transaction_id)


@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    for file in files:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed",
            )

    await process_pdfs(files)
    return {
        "message": "Files received successfully",
        "filenames": [file.filename for file in files],
    }
