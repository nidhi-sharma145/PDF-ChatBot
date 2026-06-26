# 🌌 OLLAMA LOCAL SETUP GUIDE // AURA PDF AI Offline Setup

AURA PDF AI now runs entirely offline using **Ollama** and the **llama3.2:3b** model. Follow these steps to configure your local machine for fully offline operation.

---

## 1. Install Ollama

### Windows (Recommended)
1. Download the Ollama Installer from the official website:
   👉 **[https://ollama.com/download/windows](https://ollama.com/download/windows)**
2. Run the downloaded installer (`OllamaSetup.exe`) and follow the on-screen prompts.
3. Once installation completes, Ollama will run in the background. You will see the Ollama icon (llama silhouette) in your Windows system tray.

### macOS
1. Download from: **[https://ollama.com/download/mac](https://ollama.com/download/mac)**
2. Unzip the downloaded file and drag the Ollama application into your `Applications` folder.
3. Open Ollama from your Applications folder.

### Linux
Run the official installation script:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

---

## 2. Pull the Required Model

Open a **new terminal window** (Command Prompt, PowerShell, or Bash) and execute the following command to download the model:

```bash
ollama pull llama3.2:3b
```

> **Why llama3.2:3b?**
> The `llama3.2:3b` model is a lightweight 3-billion parameter model optimized for local consumer CPUs and laptops. It consumes ~2GB of RAM, offers extremely fast inference times, and supports native JSON schema generation which ensures high-quality quizzes without formatting errors.

---

## 3. Verify Ollama Service is Running

You can check if the service is running and the model is downloaded by listing your locally available models:

```bash
ollama list
```

You should see `llama3.2:3b` listed in the output:
```text
NAME            ID              SIZE      MODIFIED
llama3.2:3b     a80c4f17d48a    2.0 GB    Just now
```

---

## 4. Cache the Embedding Model Locally

To run the application without an active internet connection, the Sentence Transformer embedding model must be downloaded and stored locally.

Run the following command in your terminal (with the virtual environment activated and internet connection active) to download and save the model to the local `models` directory:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2').save('models/all-MiniLM-L6-v2')"
```

Once this command runs, the model files will be saved under the `models/all-MiniLM-L6-v2/` directory of your project root. Subsequent launches will detect this local directory and load the model strictly offline (`local_files_only=True`).

---

## 5. Run the Project

Once the model has finished downloading, you can run the FastAPI backend server just as before:

1. **Activate Virtual Environment** (if not already active):
   - Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - macOS / Linux:
     ```bash
     source venv/bin/activate
     ```

2. **Run Server**:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

3. **Open Frontend**:
   Navigate to **`http://127.0.0.1:8000/`** in your browser. Upload your PDF and start chatting 100% offline!
