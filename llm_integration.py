import os
import httpx
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "HuggingFaceH4/zephyr-7b-beta")
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

if not HUGGINGFACE_API_TOKEN:
    raise ValueError(
        "HUGGINGFACE_API_TOKEN environment variable is required for Hugging Face Inference API. "
        "Set it in your .env file or environment before running the application."
    )

async def _hf_generate(prompt: str, temperature: float = 0.3, max_new_tokens: int = 512) -> str:
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": temperature,
            "max_new_tokens": max_new_tokens,
            "return_full_text": False,
        }
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        print(HUGGINGFACE_API_URL)

    response = await client.post(
        url=HUGGINGFACE_API_URL,
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Hugging Face API error ({response.status_code}): {response.text}"
        )

    data = response.json()
    if isinstance(data, dict) and data.get("error"):
        raise RuntimeError(f"Hugging Face API error: {data['error']}")

    if not isinstance(data, list) or not data or "generated_text" not in data[0]:
        raise RuntimeError(f"Unexpected Hugging Face API response: {data}")

    return data[0]["generated_text"].strip()

async def ask_question(question: str, context: list[str]) -> str:
    """Uses Hugging Face Inference API to answer a question based on provided context."""
    context_str = "\n\n".join(context)
    prompt = (
        "You are a helpful assistant that answers questions based on the provided PDF context. "
        "If the answer is not contained in the context, say 'I cannot find the answer in the provided document.' "
        "Keep your answers concise and accurate.\n\n"
        f"Context:\n{context_str}\n\nQuestion: {question}"
    )

    try:
        return await _hf_generate(prompt, temperature=0.3, max_new_tokens=256)
    except Exception as e:
        return f"Error communicating with Hugging Face API: {str(e)}"

async def generate_quiz(context: list[str], num_questions: int = 3) -> str:
    """Uses Hugging Face Inference API to generate a multiple-choice quiz based on context."""
    context_str = "\n\n".join(context)
    prompt = (
        f"You are a teacher. Create a multiple-choice quiz with {num_questions} questions based on the provided text. "
        "For each question, provide 4 options (A, B, C, D) and specify the correct answer at the end of the question. "
        "Format the output clearly.\n\n"
        f"Context:\n{context_str}"
    )

    try:
        return await _hf_generate(prompt, temperature=0.7, max_new_tokens=512)
    except Exception as e:
        return f"Error communicating with Hugging Face API: {str(e)}"
