import json
import re
import os
from datetime import datetime
import requests
import streamlit as st

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# -----------------------------
# CONFIG
# -----------------------------
VECTOR_STORE_PATH = "visa_vector_store"
HF_TOKEN = os.getenv("HF_TOKEN")

# -----------------------------
# Load Vector Store
# -----------------------------
@st.cache_resource(show_spinner=False)
def load_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

# -----------------------------
# Retrieve Policy
# -----------------------------
@st.cache_data(show_spinner=False)
def retrieve_policy(country, visa_type):
    vectorstore = load_vector_store()

    query = f"{country} {visa_type}"

    retrieved_docs = vectorstore.similarity_search(
        query,
        k=3,
        filter={
            "country": country.lower(),
            "visa_type": visa_type.lower()
        }
    )

    source_links = set()
    filtered_docs = []

    for doc in retrieved_docs:
        doc_country = doc.metadata.get("country", "").strip().lower()
        doc_visa = doc.metadata.get("visa_type", "").strip().lower()

        if doc_country == country.lower() and doc_visa == visa_type.lower():
            filtered_docs.append(doc)

            if "official_source" in doc.metadata:
                source_links.add(doc.metadata["official_source"])

    if not filtered_docs:
        return None, None

    context = "\n\n".join([doc.page_content for doc in filtered_docs])
    return context, source_links

# -----------------------------
# Generate Response (HuggingFace)
# -----------------------------
def generate_response(prompt):
    API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={
            "inputs": prompt,
            "parameters": {
            "max_length": 512
        }
}
        )

        # ✅ Debug info (very important)
        if response.status_code != 200:
            return f"API ERROR ({response.status_code}): {response.text}"

        try:
            result = response.json()
        except Exception:
            return f"INVALID JSON RESPONSE:\n{response.text}"

        # ✅ Correct extraction
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]

        # fallback
        return str(result)

    except Exception as e:
        return f"ERROR CONNECTING TO MODEL: {str(e)}"
# -----------------------------
# Log Decision
# -----------------------------
def log_decision(user_data, decision, confidence_value, confidence_level):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_profile": user_data,
        "decision": decision,
        "confidence_score": confidence_value,
        "confidence_level": confidence_level
    }

    logs = []

    try:
        with open("decision_logs.json", "r") as file:
            content = file.read().strip()
            if content:
                logs = json.loads(content)
    except Exception:
        logs = []

    logs.append(log_entry)

    with open("decision_logs.json", "w") as file:
        json.dump(logs, file, indent=4)

# -----------------------------
# MAIN (CLI MODE - optional)
# -----------------------------
if __name__ == "__main__":

    print("=== Visa Eligibility Screening System ===\n")

    age = input("Enter Age: ")
    nationality = input("Enter Nationality: ")
    education = input("Enter Education Level: ")
    employment = input("Enter Employment Status: ")
    income = input("Enter Annual Income: ")
    country = input("Enter Country: ").strip().lower()
    visa_type = input("Enter Visa Type: ").strip().lower()

    user_data = {
        "age": age,
        "nationality": nationality,
        "education": education,
        "employment": employment,
        "income": income,
        "country": country,
        "visa_type": visa_type
    }

    print("\nRetrieving relevant policy...\n")

    context, source_links = retrieve_policy(country, visa_type)

    if not context:
        print("No matching policy found.")
    else:

        prompt = f"""
You are an immigration eligibility assessment system.

Based ONLY on the provided policy context, evaluate the applicant.

Return output in this format:

Decision: Eligible / Possibly Eligible / Not Eligible
Confidence: 0 to 1
Reasoning: Explain clearly

User Profile:
Age: {age}
Nationality: {nationality}
Education: {education}
Employment: {employment}
Income: {income}
Country: {country}
Visa Type: {visa_type}

Policy Context:
{context}
"""

        result = generate_response(prompt)

        print("\n=== RESULT ===\n")
        print(result)