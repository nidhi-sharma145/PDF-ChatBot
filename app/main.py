import os
from typing import Dict, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.config import settings
from app.services import pdf_service
from app.services.vector_service import vector_store
from app.services import ai_service

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered PDF Chatbot",
    description="A futuristic PDF analyzer, chat partner, and quiz generator.",
    version="1.0.0"
)

# Add CORS Middleware to facilitate flexible APIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database to store raw extracted text for quiz generation
# Key is session_id (filename or random string), Value is full extracted text
extracted_documents: Dict[str, str] = {}

# Pydantic schemas for response validation and proper API error handling
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The message/question from the user")
    session_id: Optional[str] = Field(None, description="Optional specific session/file to chat with")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="The AI response based on retrieved PDF context")
    session_id: str = Field(..., description="The active session/file ID used")

class QuizRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Optional specific session ID to generate quiz from")
    num_questions: int = Field(5, ge=1, le=10, description="Number of questions to generate (1-10)")

class ConfigUpdate(BaseModel):
    provider: str = Field(..., description="The AI provider name: 'gemini' or 'groq'")

# Ensure the static files folder exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

# Mount the static directory for CSS, JS, and Images
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/api/config")
async def get_config():
    """Returns the current API provider configurations and availability status."""
    return {
        "provider": settings.API_PROVIDER,
        "has_gemini_key": bool(settings.GEMINI_API_KEY and "your_gemini_api_key" not in settings.GEMINI_API_KEY),
        "has_groq_key": bool(settings.GROQ_API_KEY and "your_groq_api_key" not in settings.GROQ_API_KEY)
    }

@app.post("/api/config")
async def update_config(config: ConfigUpdate):
    """Updates the active API provider on the fly."""
    prov = config.provider.lower().strip()
    if prov not in ["gemini", "groq"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported API provider. Choose 'gemini' or 'groq'."
        )
    settings.API_PROVIDER = prov
    return {"status": "success", "provider": settings.API_PROVIDER}


@app.get("/")
async def get_index():
    """Serves the main frontend page."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "index.html not found. Please ensure frontend static files are created."}
    )

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Receives a PDF file, extracts text, generates vector embeddings,
    and indexes them with FAISS for semantic search.
    """
    # Validate file extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a PDF (.pdf) file."
        )

    try:
        # Read uploaded file content
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded PDF file is empty."
            )

        # Extract text from the PDF
        extracted_text = pdf_service.extract_text_from_pdf(contents)
        if not extracted_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No readable text could be extracted from this PDF. It might be scanned or image-only."
            )

        # Chunk the text
        chunks = pdf_service.split_text_into_chunks(extracted_text)
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Failed to split text into chunks. PDF contains insufficient readable characters."
            )

        # Generate embeddings and store in FAISS index in-memory
        session_id = file.filename
        success = vector_store.create_session(session_id, chunks)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to build vector index from PDF content."
            )

        # Cache raw text in-memory for quiz generation
        extracted_documents[session_id] = extracted_text

        return {
            "status": "success",
            "message": "PDF uploaded and processed successfully.",
            "session_id": session_id,
            "filename": file.filename,
            "chunks_count": len(chunks),
            "characters_count": len(extracted_text)
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the PDF: {str(e) or type(e).__name__}"
        )


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_pdf(request: ChatRequest):
    """
    Queries the vector database for matching chunks and calls the AI
    service to answer the user's question using the matching context.
    """
    # Determine the target session ID
    session_id = request.session_id or vector_store.active_session_id
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active document session. Please upload a PDF document first."
        )

    try:
        # Perform semantic similarity search
        context_chunks = vector_store.search(request.message, session_id=session_id, top_k=4)
        
        # Pass context chunks and query to AI Service
        answer = ai_service.generate_answer(request.message, context_chunks)
        
        return ChatResponse(
            answer=answer,
            session_id=session_id
        )

    except ValueError as ve:
        # Catch configuration errors (like missing API Keys)
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat generation failed: {str(e)}"
        )

@app.post("/api/quiz")
async def generate_quiz(request: QuizRequest):
    """
    Generates an educational quiz based on the text of the uploaded PDF document.
    """
    # Determine the target session ID
    session_id = request.session_id or vector_store.active_session_id
    
    if not session_id or session_id not in extracted_documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active document session. Please upload a PDF document first."
        )

    try:
        raw_text = extracted_documents[session_id]
        
        # Request AI Service to generate a formatted quiz
        quiz = ai_service.generate_quiz(raw_text, num_questions=request.num_questions)
        
        return {
            "status": "success",
            "session_id": session_id,
            "quiz": quiz
        }

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quiz generation failed: {str(e)}"
        )
