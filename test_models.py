import os
import requests
from dotenv import load_dotenv

load_dotenv()
hf_token = os.getenv("HF_TOKEN")

headers = {
    "Authorization": f"Bearer {hf_token}",
    "Content-Type": "application/json"
}

url = "https://router.huggingface.co/v1/chat/completions"

models_to_test = [
    "Qwen/Qwen2.5-72B-Instruct",
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "HuggingFaceH4/zephyr-7b-beta",
    "mistralai/Mistral-7B-Instruct-v0.2"
]

res = []

for model in models_to_test:
    json_payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Hi"}
        ],
        "max_tokens": 10
    }
    r = requests.post(url, headers=headers, json=json_payload)
    res.append(f"{model}: {r.status_code} - {r.text}")

with open("test_results.txt", "w") as f:
    f.write("\n".join(res))
