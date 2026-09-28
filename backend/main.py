from fastapi import FastAPI
from gemini import ask_gemini
from models import ChatReply, ChatRequest

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatReply)
def chat(payload: ChatRequest):
    return ask_gemini(payload.message, payload.previous_transaction_id)
