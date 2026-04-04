import os
import requests
from dotenv import load_dotenv

load_dotenv()
hf_token = os.getenv("HF_TOKEN")

headers = {
    "Authorization": f"Bearer {hf_token}",
    "Content-Type": "application/json"
}

# Test direct model endpoint
url1 = "https://api-inference.huggingface.co/models/microsoft/Phi-3.5-mini-instruct/v1/chat/completions"
json_payload1 = {
    "model": "microsoft/Phi-3.5-mini-instruct",
    "messages": [
        {"role": "user", "content": "Hello"}
    ],
    "max_tokens": 10
}

r1 = requests.post(url1, headers=headers, json=json_payload1)
print(f"Direct API: {r1.status_code} - {r1.text}")

# Test generic router with a different, proven model
url2 = "https://router.huggingface.co/v1/chat/completions"
json_payload2 = {
    "model": "HuggingFaceH4/zephyr-7b-beta",
    "messages": [
        {"role": "user", "content": "Hello"}
    ],
    "max_tokens": 10
}

r2 = requests.post(url2, headers=headers, json=json_payload2)
print(f"Router API (Zephyr): {r2.status_code} - {r2.text}")
