# 🌌 AURA PDF AI // Futuristic Chat & Quiz Workspace

A stunning, modern, and beginner-friendly AI-powered PDF Chatbot web application. Upload any PDF, and AURA PDF AI will instantly extract and segment its text, convert the chunks into mathematical vector representations using **Sentence Transformers** (`all-MiniLM-L6-v2`), index them in a high-speed **FAISS** vector store on your CPU, and allow you to hold context-rich conversations and take automated interactive quizzes generated from the document using Google **Gemini** or **Groq Llama 3**.

---

## 🎨 Design & Features

- **Sleek Futuristic UI**: Built on a beautiful glassmorphic dark space theme using vanilla CSS with custom glowing scrollbars, glowing neon input wrappers, and interactive floating notification toasts.
- **Offline Embeddings**: 100% local, high-speed, CPU-friendly embeddings generated with `sentence-transformers`. Avoids heavy cloud dependency or unexpected API costs for vectorization.
- **Semantic Similarity Search**: Instant lookup of document context utilizing `faiss-cpu`, mapping your questions directly to relevant sections.
- **Dual Engine AI Chat**: Connects to the robust free tiers of Google Gemini or Groq to supply deep, intelligent answers formatted in clean markdown.
- **Automated Quiz Terminal**: Scans the text and generates custom multiple-choice quizzes (JSON structured) complete with animated progress bars, real-time score tracking, instant right/wrong option highlights, and a final grade screen.
- **Dynamic Configuration**: Change the active LLM engine on the fly directly inside the UI dashboard without restarting the FastAPI server.

---

## 🏗️ Project Folder Structure

```text
├── app/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py       # Interacts with Gemini/Groq, formats prompts, handles JSON quizzes
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

### 5. Setup Environment Variables
Configure your selected LLM API keys. 
1. Duplicate the `.env.example` file and rename it to `.env`.
2. Fill in your preferred API keys:
   ```env
   # API Provider configuration (choose 'gemini' or 'groq')
   API_PROVIDER=gemini

   # For Gemini: Get your key from Google AI Studio (free tier available!): https://aistudio.google.com/
   GEMINI_API_KEY=your_actual_gemini_key_here

   # For Groq: Get your key from Groq Console (free tier available!): https://console.groq.com/
   GROQ_API_KEY=your_actual_groq_key_here
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
- **API Key Missing Alert**: Verify that your `.env` file is in the root directory (same folder as `requirements.txt`) and that your `GEMINI_API_KEY` or `GROQ_API_KEY` does not contain spaces or quotes.
- **CPU Embedding Speed**: The offline model is incredibly light and optimized. Average parsing and embedding time for a standard 10-page document is less than 3 seconds on standard modern CPU hardware.
