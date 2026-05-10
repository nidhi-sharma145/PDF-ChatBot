from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import shutil
import os
import asyncio

from pdf_handler import process_pdf
from vector_db import vector_db
from llm_integration import ask_question, generate_quiz

app = FastAPI(title="PDF Chatbot & Quiz Generator")

# Setup templates and static files
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="index.html"
    )

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_path = os.path.join("uploads", file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Process PDF and update Vector DB
        # Run in threadpool to avoid blocking event loop since fitz is synchronous
        chunks = await asyncio.to_thread(process_pdf, file_path)
        
        # Clear previous data and add new chunks
        # In a real app with multiple users, we would need session-based storage
        vector_db.clear()
        
        # Encode and add to FAISS
        await asyncio.to_thread(vector_db.add_texts, chunks)
        
        return {"filename": file.filename, "message": "PDF uploaded and processed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/chat")
async def chat(question: str = Form(...)):
    if vector_db.index.ntotal == 0:
        raise HTTPException(status_code=400, detail="Please upload a PDF first.")
    
    # Retrieve relevant context
    context = await asyncio.to_thread(vector_db.search, question, top_k=3)
    
    # Ask LLM
    answer = await ask_question(question, context)
    return {"answer": answer}

@app.post("/quiz")
async def get_quiz(num_questions: int = Form(3)):
    if vector_db.index.ntotal == 0:
        raise HTTPException(status_code=400, detail="Please upload a PDF first.")
    
    # Retrieve some top context chunks to form the quiz
    # Here we just take the first few chunks of the document to generate a general quiz
    # Or we can search for a general summary or just pass random chunks
    context_chunks = vector_db.chunks[:5] # Taking the first 5 chunks as context
    
    quiz_content = await generate_quiz(context_chunks, num_questions)
    return {"quiz": quiz_content}
