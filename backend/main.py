from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gemini import ask_gemini
from models import ChatReply, ChatRequest

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
