import io
import re
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document
from fastapi import UploadFile, HTTPException

async def extract_text_from_pdf(file: UploadFile) -> str:
    contents = await file.read()
    text = extract_pdf_text(io.BytesIO(contents))
    if not text.strip():
        raise ValueError("Empty text")
    return text.strip()

async def extract_text_from_docx(file: UploadFile) -> str:
    contents = await file.read()
    doc = Document(io.BytesIO(contents))
    text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    if not text.strip():
        raise ValueError("Empty text")
    return text.strip()

async def parse_resume(file: UploadFile):
    if file.filename.endswith(".pdf"):
        text = await extract_text_from_pdf(file)
    else:
        text = await extract_text_from_docx(file)
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    return {
        "filename": file.filename,
        "extracted_text": text,
        "email": emails[0] if emails else None,
        "word_count": len(text.split())
    }
