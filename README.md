# ✨ SwiftVisa - Premium AI Visa Eligibility Dashboard

SwiftVisa is a cutting-edge, AI-powered visa eligibility screening system built using an advanced Retrieval-Augmented Generation (RAG) architecture. Featuring a premium SaaS-grade user interface, SwiftVisa bypasses generic language models by actively searching official local policy data and passing it to a structured AI reasoning engine to emulate a real-world Visa Eligibility Officer.

---

## 🚀 Project Overview

Understanding visa eligibility across international borders is traditionally complex, time-consuming, and difficult to verify. SwiftVisa solves this by automating eligibility assessment:

- **Semantic Policy Extraction**: Actively searches the integrated vector database for official government policies.
- **Deep AI Reasoning Engine**: Uses a highly formulated 10-point evaluation protocol to break down applicant profiles into structural reports.
- **Interactive Checklists**: Employs live session states to generate dynamic required document checklists that users must confirm before unlocking final assessments.
- **SaaS Glassmorphism UI**: A beautifully fluid, animated, single-page application experience replacing the legacy Streamlit sidebar flow.

---

## 🧠 Advanced AI Features

1. **Top Navbar Application Routing**: A custom-injected CSS navbar seamlessly switches contexts without relying on clunky boxed limits or Streamlit's native sidebar.
2. **Professional Visa Officer Model**: Replaced qualitative score tracking with a structured LLM output targeting specific risk factors, actionable insights, and missing profile traits.
3. **Mandatory Interactive Flow**: Forces applicants to engage with AI-identified documents via a dynamic UI Gatekeeper, preventing users from seeing final judgments without validating document readiness.
4. **Transparent Policy Grounding**: Citations back to the precise official source links the AI utilized natively render beneath the generated report.
5. **Conversational AI Assistant**: An integrated side-dashboard allows free-form contextual chats regarding global immigration policies, powered directly via the RAG database.

---

## ⚙️ System Architecture (The RAG Pipeline)

1. **Policy Embedding & Vectorization**
   - **Model**: `sentence-transformers/all-MiniLM-L6-v2`
   - Maps normalized real-world JSON policy chunks into dense embeddings, stored locally within **FAISS**.
2. **Semantic Context Retrieval**
   - Queries the applicant's input parameters (Visa Type, Destination Country, etc.) to fetch the Top-K relevant policy nodes.
3. **AI Inference Layer**
   - **Model Engine**: Hugging Face Inference API (`meta-llama/Meta-Llama-3-8B-Instruct`).
   - Replaces local constrained deployment with a scalable remote LLM model handling a strict 10-part instruction payload.
4. **Streamlit Execution Flow**
   - Intercepts the generated JSON matrices and visually renders the Markdown via cached memory (Streamlit Session State).

---

## 🛠️ Tech Stack

**Core Technologies**
- **Python** (Backend scripting)
- **LangChain** (RAG Orchestration)
- **FAISS** (Local Vector Database)
- **Sentence Transformers** (Policy Embedding Generation)

**AI & Deployment**
- **Hugging Face Router API** (Zero-configuration LLM backend inference)
- **Meta Llama 3 (8B)** (Target generation model)

**Interface**
- **Streamlit** (Web UI Framework)
- Custom raw **CSS/HTML** injections for Native UI/SaaS conversions.

---

## 💡 How to Run the Project

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
You must connect to the Hugging Face Serverless endpoint. Create a file named `.env` in the root directory and add your key:
```env
HF_TOKEN=your_hugging_face_api_token_here
```

### Step 3: Vector Store Generation
Build the initial mathematical embeddings database out of your locally stored JSON policy sets:
```bash
python build_vector_store.py
```

### Step 4: Run the SwiftVisa Application
Launch the premium web dashboard:
```bash
streamlit run streamlit_app.py
```
*(The app will automatically open a tab in your local default browser connected to `localhost:8501`)*

---

## 🌍 Supported Routing Countries

- USA, Canada, United Kingdom, Germany, France, Ireland, Netherlands, Australia, New Zealand, Sweden, Singapore, UAE.
*(All contextual policies are gathered globally from official government frameworks).*

---

## 📈 Future Roadmaps & Improvements

- **Scalable Database Backing**: Switch structured local logs (`decision_logs.json`) into PostgreSQL or MongoDB arrays for true production environments.
- **Model Agnosticism**: Allow UI toggle configurations to natively switch the inference pipeline to Anthropic Claude 3 or OpenAI GPT-4 if Hugging Face limits are reached.

---

**Author**  
Shweta Kharat  
*Infosys Internship Program*