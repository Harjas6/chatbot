from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from pypdf import PdfReader

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


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


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 300) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


async def process_pdfs(files: list[UploadFile]):
    for file in files:
        path = await save_pdf(file)
        text = extract_text(path)
        chunks = chunk_text(text)
