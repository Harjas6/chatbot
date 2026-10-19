from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = SentenceTransformer(MODEL_NAME)


async def save_pdf(file: UploadFile) -> Path:
    original_filename = file.filename or "uploaded_file.pdf"
    filename = f"{uuid4().hex}_{original_filename}"
    file_path = UPLOAD_DIR / filename
    contents = await file.read()
    file_path.write_bytes(contents)
    return file_path


def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 30) -> list[str]:
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size > overlap >= 0")
    chunks = []
    tokens = tokenizer.encode(text, add_special_tokens=False)
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunks.append(tokenizer.decode(tokens[start:end], skip_special_tokens=True))
        start += chunk_size - overlap

    return chunks


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    embeddings = model.encode(chunks)
    return embeddings.tolist()


async def process_pdfs(files: list[UploadFile]):
    for file in files:
        path = await save_pdf(file)
        text = extract_text(path)
        chunks = chunk_text(text)
        embeddings = embed_chunks(chunks)
