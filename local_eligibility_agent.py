import json
import re
import os
from datetime import datetime
import requests
import streamlit as st
from dotenv import load_dotenv

# Load variables from .env file into the environment
load_dotenv()

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

    # First, try a strictly filtered similarity search
    try:
        retrieved_docs = vectorstore.similarity_search(
            query,
            k=3,
            filter={
                "country": country.lower(),
                "visa_type": visa_type.lower()
            }
        )
    except Exception:
        retrieved_docs = []

    source_links = set()
    filtered_docs = []

    for doc in retrieved_docs:
        doc_country = doc.metadata.get("country", "").strip().lower()
        doc_visa = doc.metadata.get("visa_type", "").strip().lower()

        if doc_country == country.lower() and doc_visa == visa_type.lower():
            filtered_docs.append(doc)
            if "official_source" in doc.metadata:
                source_links.add(doc.metadata["official_source"])

    # Fallback to pure semantic search if strict metadata filtering isolates zero exact matches
    if not filtered_docs:
        retrieved_docs = vectorstore.similarity_search(query, k=3)
        for doc in retrieved_docs:
            filtered_docs.append(doc)
            if "official_source" in doc.metadata:
                source_links.add(doc.metadata["official_source"])

    if not filtered_docs:
        return None, None

    context = "\n\n".join([doc.page_content for doc in filtered_docs])
    return context, source_links

# -----------------------------
# Generate Response (HuggingFace Phi-3)
# -----------------------------
def generate_response(prompt):
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    
    # Retrieve the token from environment variables
    hf_token = os.getenv("HF_TOKEN", "").strip()

    if not hf_token:
        return "ERROR: HF_TOKEN environment variable is missing or empty. Please set it to a valid Hugging Face Inference token."

    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "model": "meta-llama/Meta-Llama-3-8B-Instruct",
                "messages": [
                    {"role": "system", "content": "You are a helpful immigration eligibility assessment system."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000,
                "stream": False
            }
        )

        # 🔍 Debug status
        if response.status_code != 200:
            return f"API ERROR ({response.status_code}): {response.text}"

        data = response.json()

        # ✅ Safe extraction
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]

        return str(data)

    except Exception as e:
        return f"ERROR: {str(e)}"
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
    dob = input("Enter Date of Birth (YYYY-MM-DD): ")
    sex = input("Enter Sex (Male/Female/Other): ")
    nationality = input("Enter Nationality: ")
    education = input("Enter Education Level: ")
    employment = input("Enter Employment Status: ")
    income = input("Enter Annual Income: ")
    country = input("Enter Country: ").strip().lower()
    visa_type = input("Enter Visa Type: ").strip().lower()

    user_data = {
        "age": age,
        "dob": dob,
        "sex": sex,
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
You are an expert immigration eligibility officer.

Evaluate the applicant STRICTLY using the provided policy context.

----------------------------------------
USER PROFILE:
Age: {age}
Date of Birth: {dob}
Sex: {sex}
Nationality: {nationality}
Education: {education}
Employment: {employment}
Income: {income}
Country: {country}
Visa Type: {visa_type}

----------------------------------------
POLICY CONTEXT:
{context}

----------------------------------------

IMPORTANT CONTEXT RULES:
- Date of Birth is valid only if between year 1950 and today.
- Sex must be one of: Male, Female, Other.
- If any of these inputs are missing or invalid, clearly state "Not sufficient information" in reasoning.
- Do NOT ignore missing or placeholder values.

----------------------------------------

Return output STRICTLY in this format:

Decision: <Eligible / Possibly Eligible / Not Eligible>

Confidence: <0 to 1 score>

Key Findings:
- <clear meaningful point>
- <clear meaningful point>
- <clear meaningful point>

Requirements Met:
- <specific requirement satisfied>
- <specific requirement satisfied>

Requirements Not Met:
- <specific missing requirement OR "None">

----------------------------------------

Evaluation Breakdown:

Education Assessment:
- Write a complete sentence explaining match or mismatch.

Employment Assessment:
- Write a complete sentence explaining alignment.

Income Assessment:
- Clearly state if income meets requirement.

Policy Match:
- Explain overall alignment with visa rules.

----------------------------------------

Risk Factors:
- Only mention REAL risks if they exist.
- If none, write exactly: None

Actionable Suggestions:
- Provide improvements ONLY if needed.
- If not needed, write exactly: None

Required Documents:
- Always include at least:
  - Passport
  - Educational Certificates
  - Employment Proof
  - Financial Proof

----------------------------------------

Final Assessment:
- Provide a clear and professional conclusion.

----------------------------------------

STRICT RULES:
- NEVER leave any section empty
- NEVER use placeholders like "--------"
- ALWAYS produce meaningful content
- If input is invalid or missing, explicitly mention it
- Output must be clean and structured
"""

        result = generate_response(prompt)

        print("\n=== RESULT ===\n")
        print(result)