import os
import requests
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = os.getenv("HF_INFERENCE_URL", "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2")


headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

VECTOR_STORE_PATH = "visa_vector_store"


def load_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


def retrieve_policy(country, visa_type, query):
    vectorstore = load_vector_store()

    results = vectorstore.similarity_search(
        query,
        k=3,
        filter={
            "country": country,
            "visa_type": visa_type
        }
    )

    return "\n\n".join([doc.page_content for doc in results])


def generate_eligibility(prompt):

    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.2,
            "max_new_tokens": 400
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        if response.status_code == 404:
            return {
                "error": "API ERROR (404): Not Found. Verify HF_INFERENCE_URL and model name, or check API access rights."
            }
        return {
            "error": f"API ERROR ({response.status_code}): {response.text}"
        }

    return response.json()


if __name__ == "__main__":

    user_data = {
        "age": 24,
        "nationality": "India",
        "education": "Bachelor's degree in Computer Science",
        "employment": "Software Engineer with 2 years experience",
        "income": "60000 USD",
        "country": "Germany",
        "visa_type": "Skilled Worker"
    }

    context = retrieve_policy(
        user_data["country"],
        user_data["visa_type"],
        "Eligibility requirements"
    )

    prompt = f"""
You are an immigration eligibility officer.

Applicant:
Age: {user_data['age']}
Nationality: {user_data['nationality']}
Education: {user_data['education']}
Employment: {user_data['employment']}
Income: {user_data['income']}
Country: {user_data['country']}
Visa Type: {user_data['visa_type']}

Policy Context:
{context}

Decide: Eligible / Possibly Eligible / Not Eligible.
Explain reasoning clearly.
"""

    print("Generating response...\n")
    result = generate_eligibility(prompt)

    print(result)
