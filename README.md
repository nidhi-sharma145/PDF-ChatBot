# 🌌 AURA PDF AI // Futuristic Chat & Quiz Workspace

A stunning, modern, and beginner-friendly AI-powered PDF Chatbot web application. Upload any PDF, and AURA PDF AI will instantly extract and segment its text, convert the chunks into mathematical vector representations using **Sentence Transformers** (`all-MiniLM-L6-v2`), index them in a high-speed **FAISS** vector store on your CPU, and allow you to hold context-rich conversations and take automated interactive quizzes generated from the document entirely offline using local **Ollama** (`llama3.2:3b`).

---

## 🎨 Design & Features

- **Sleek Futuristic UI**: Built on a beautiful glassmorphic dark space theme using vanilla CSS with custom glowing scrollbars, glowing neon input wrappers, and interactive floating notification toasts.
- **Offline Embeddings**: 100% local, high-speed, CPU-friendly embeddings generated with `sentence-transformers`. Avoids heavy cloud dependency or unexpected API costs for vectorization.
- **Semantic Similarity Search**: Instant lookup of document context utilizing `faiss-cpu`, mapping your questions directly to relevant sections.
- **100% Offline AI Chat**: Fully offline responses generated locally on your machine using Ollama (`llama3.2:3b`), requiring zero API keys, cost, or internet connection.
- **Automated Quiz Terminal**: Scans the text and generates custom multiple-choice quizzes (JSON structured) complete with animated progress bars, real-time score tracking, instant right/wrong option highlights, and a final grade screen.

---

## 🏗️ Project Folder Structure

```text
├── app/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py       # Interacts with local Ollama, formats prompts, handles JSON quizzes
│   │   ├── pdf_service.py      # Stable pypdf parser and text segmenter
│   │   └── vector_service.py   # SentenceTransformers loader and FAISS CPU indexing
│   ├── static/
│   │   ├── app.js              # Complete state control, AJAX fetches, quiz cards & toasts
│   │   ├── index.html          # Semantic HTML dashboard template
│   │   └── style.css           # Glassmorphism, animations, custom scrollbars, and neon glows
│   ├── __init__.py
│   ├── config.py               # Dotenv settings loader with clean fallbacks
│   └── main.py                 # FastAPI application routes, CORS, and Pydantic validation
├── .env                        # Local environment variables (API keys)
├── .env.example                # Blank template for environment variables
├── requirements.txt            # Project python package list
└── README.md                   # Installation and usage instructions (this file)
```

---

## 🚀 Installation & Local Setup

Getting AURA PDF AI up and running locally is extremely quick and straightforward. Follow these steps:

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your operating system (Windows, macOS, or Linux).

### 2. Clone or Extract the Workspace
Open your terminal or command prompt inside the project folder:
```bash
cd "c:\Users\nidhi\OneDrive\Desktop\NEW P"
```

### 3. Create and Activate a Virtual Environment (Recommended)
This keeps your global python packages isolated and clean.
- **Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Install Dependencies
Install all required libraries using `requirements.txt`:
```bash
pip install -r requirements.txt
```
> _Note: The first time you execute the chatbot, `sentence-transformers` will download the tiny 90MB `all-MiniLM-L6-v2` model locally in the background. Subsequent runs are fully cached and 100% offline!_

### 5. Setup Ollama and Environment Variables
AURA PDF AI runs entirely offline. Before starting, configure your local Ollama setup:
1. Set up Ollama on your machine and pull the required model. See the comprehensive **[OLLAMA_SETUP.md](file:///c:/Users/nidhi/OneDrive/Desktop/NEW%20P/OLLAMA_SETUP.md)** guide for step-by-step instructions.
2. Duplicate the `.env.example` file and rename it to `.env`.
3. The environment variables are set to:
   ```env
   # Ollama Configuration (Local Offline LLM)
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2:3b
   ```

---

## 💻 Running the Application

Start the FastAPI backend with **Uvicorn**:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once the terminal prints `Uvicorn running on http://127.0.0.1:8000`:
1. Open your web browser and navigate to: **`http://127.0.0.1:8000/`**
2. Drag and drop any text-readable PDF into the **Document Hub** sidebar.
3. Once the success notification slides in, navigate to **Chat Session** to ask questions, or head over to the **Quiz Terminal** to test your knowledge!

---

## 🛠️ Verification & Troubleshooting

- **No Text Extracted Error**: If you receive a warning that no text could be extracted, check if the PDF contains scanned images. Scanned PDFs require OCR software. Try using a digital text-based PDF.
- **Ollama Connection Failed**: Verify that Ollama is currently running and the server is responsive at `http://localhost:11434`.
- **Model Not Found (HTTP 404)**: Verify you downloaded the model by running `ollama pull llama3.2:3b`.
- **CPU Inference Speed**: Generating answers and quizzes runs locally on your CPU. Average response generation can take between 5 to 15 seconds depending on hardware performance.
- **CPU Embedding Speed**: The offline embedding model is incredibly light and optimized. Average parsing and embedding time for a standard 10-page document is less than 3 seconds on standard modern CPU hardware.
