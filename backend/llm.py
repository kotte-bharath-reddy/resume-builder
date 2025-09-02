from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("HUGGINGFACE_API_KEY")

def get_huggingface_client(model: str = "meta-llama/Meta-Llama-3-8B-Instruct"):
    """Return a Hugging Face Inference client for the given model"""
    return InferenceClient(model=model, token=api_key)