import asyncio

from db.connection import get_db
from db.model import Message
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from gemini import ask_gemini
from models import ChatReply, ChatRequest
from rag.pdf import process_pdfs
from sqlalchemy.ext.asyncio import AsyncSession

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
async def chat(payload: ChatRequest, db: AsyncSession = Depends(get_db)):

    reply = await asyncio.to_thread(
        ask_gemini, payload.message, payload.previous_transaction_id
    )
    db.add_all(
        [
            Message(
                role="user",
                message=payload.message,
                interaction_id=reply.transaction_id,
            ),
            Message(
                role="assistant",
                message=reply.response,
                interaction_id=reply.transaction_id,
            ),
        ]
    )
    await db.commit()
    return reply


@app.post("/upload")
async def upload_files(
    files: list[UploadFile] = File(...), db: AsyncSession = Depends(get_db)
):
    for file in files:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed",
            )

    await process_pdfs(files)
    db.add(
        Message(
            role="Upload",
            message=f"Uploaded: {', '.join(file.filename or '' for file in files)}",
        )
    )
    await db.commit()
    return {
        "message": "Files received successfully",
        "filenames": [file.filename for file in files],
    }
