# backend/llm.py
from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface.chat_models import ChatHuggingFace
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")

def get_huggingface_chat(
    model: str = "meta-llama/Meta-Llama-3-8B-Instruct",
    temperature: float = 0.3,
    max_new_tokens: int = 2048
):
    """
    Return a LangChain ChatModel for Hugging Face Inference API
    with configurable parameters.
    """
    llm = HuggingFaceEndpoint(
        repo_id=model,
        task="conversational",  # ✅ Important
        huggingfacehub_api_token=api_key,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
    )
    return ChatHuggingFace(llm=llm)
