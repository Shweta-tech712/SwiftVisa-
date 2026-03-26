import streamlit as st
import re
import json
import pandas as pd
from local_eligibility_agent import retrieve_policy, generate_response

# -------------------------------------------------
# Utility Functions
# -------------------------------------------------
def log_decision(user_data, decision, confidence_value, confidence_level):
    """Log the eligibility decision to a JSON file for analytics."""
    try:
        import os
        from datetime import datetime
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_profile": user_data,
            "decision": decision,
            "confidence_value": confidence_value,
            "confidence_level": confidence_level
        }
        
        if os.path.exists("decision_logs.json"):
            with open("decision_logs.json", "r") as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        with open("decision_logs.json", "w") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        pass  # Silently fail to not interrupt the user experience

# -------------------------------------------------
# Page Config & State Init
# -------------------------------------------------
st.set_page_config(
    page_title="SwiftVisa - AI Eligibility Agent",
    page_icon="🌍",
    layout="wide"
)

def init_session_state():
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    if "evaluation_done" not in st.session_state:
        st.session_state.evaluation_done = False
    if "result_data" not in st.session_state:
        st.session_state.result_data = {}

init_session_state()

# -------------------------------------------------
# Styling (Professional Black & Gold Theme)
# -------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

.stApp {
    background-color: #000000;
    color: #E2E8F0;
    font-family: 'Inter', sans-serif;
}

/* Headers */
h1, h2, h3 { 
    color: #D4AF37 !important; 
    font-weight: 600; 
}
h1 { font-size: 2.5rem !important; }

/* Subtitle and standard text */
p, .subtitle { color: #A0AEC0; }
.subtitle { font-size: 1.1rem; margin-bottom: 2rem; }

/* Input Labels */
label {
    color: #D4AF37 !important;
    font-weight: 500 !important;
}

/* Input Fields */
.stTextInput input,
.stNumberInput input,
.stSelectbox > div > div {
    background-color: #111111 !important;
    color: white !important;
    border: 1px solid #333333 !important;
    border-radius: 8px !important;
    transition: all 0.3s ease;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stSelectbox > div > div:focus {
    border-color: #D4AF37 !important;
    box-shadow: 0 0 0 1px #D4AF37 !important;
}

/* Form Container */
[data-testid="stForm"] {
    border: 1px solid #333333 !important;
    border-radius: 12px;
    padding: 2.5rem;
    background: #0A0A0A;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
}

/* Gradient Button */
div.stButton { margin-top: 1rem; }
.stButton > button {
    background: linear-gradient(135deg, #D4AF37 0%, #AA8A2E 100%);
    color: #000000 !important;
    border-radius: 8px;
    height: 50px;
    width: 100%;
    font-weight: 600;
    font-size: 1.1rem;
    border: none;
    box-shadow: 0 4px 14px 0 rgba(212, 175, 55, 0.2);
    transition: all 0.3s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(212, 175, 55, 0.4);
    background: linear-gradient(135deg, #F9D05F 0%, #D4AF37 100%);
}

/* Specific Sidebar Button Overrides */
[data-testid="stSidebar"] .stButton > button {
    background: #111111;
    color: #E2E8F0 !important;
    border: 1px solid #333333;
    box-shadow: none;
    height: 45px;
    justify-content: flex-start;
    padding-left: 1rem;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #1A1A1A;
    color: #D4AF37 !important;
    border-color: #D4AF37;
    transform: none;
}
/* Active Sidebar Button Mock */
.active-nav-btn {
    background: #1A1A1A !important;
    color: #D4AF37 !important;
    border-left: 4px solid #D4AF37 !important;
}

/* Cards */
.custom-card {
    background-color: #0A0A0A;
    border: 1px solid #333333;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
}

/* Metric text */
[data-testid="stMetricValue"] { color: #D4AF37; }

/* HR */
hr { border-color: #333333; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Navigation Component
# -------------------------------------------------
def sidebar_navigation():
    st.sidebar.title("🌍 SwiftVisa")
    st.sidebar.markdown('<div style="color:#A0AEC0; margin-bottom: 20px;">AI Visa Screening System</div>', unsafe_allow_html=True)
    
    st.sidebar.markdown("### 🧭 Navigation")
    
    # Custom navigation buttons
    if st.sidebar.button("🏠 Home", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()

    if st.sidebar.button("📝 User Input Form", use_container_width=True):
        st.session_state.page = "Input Form"
        st.rerun()
        
    if st.sidebar.button("📊 Eligibility Result", disabled=not st.session_state.evaluation_done, use_container_width=True):
        st.session_state.page = "Eligibility Result"
        st.rerun()
        
    if st.sidebar.button("🧠 Detailed Reasoning", disabled=not st.session_state.evaluation_done, use_container_width=True):
        st.session_state.page = "Detailed Reasoning"
        st.rerun()
        
    if st.sidebar.button("🤖 AI Visa Assistant", use_container_width=True):
        st.session_state.page = "AI Assistant"
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Tech Stack")
    st.sidebar.markdown("🎨 Streamlit<br>🐍 Python<br>🗄️ FAISS<br>🧠 Phi-3", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.session_state.dev_mode = st.sidebar.toggle("🔍 Developer / Pro Mode", value=st.session_state.get("dev_mode", False))
    st.sidebar.caption("V1.0.0 | **SwiftVisa AI System** 🚀")

# -------------------------------------------------
# Page 0: Home / Introduction
# -------------------------------------------------
def page_home():
    st.title("🌍 Dashboard & Overview")
    st.markdown('<div class="subtitle">AI-Based Visa Eligibility Screening Agent & Analytics</div>', unsafe_allow_html=True)
    
    # --- Analytics Dashboard ---
    try:
        import os
        if os.path.exists("decision_logs.json"):
            with open("decision_logs.json", "r") as f:
                logs = json.load(f)
            
            if logs:
                total = len(logs)
                eligible_count = sum(1 for log in logs if "not eligible" not in log.get("decision", "").lower() and "eligible" in log.get("decision", "").lower())
                acceptance_rate = (eligible_count / total * 100) if total > 0 else 0
                
                from collections import Counter
                countries = [log.get("user_profile", {}).get("country", "Unknown").title() for log in logs]
                top_country = Counter(countries).most_common(1)[0][0] if countries else "N/A"
                
                col1, col2, col3 = st.columns(3)
                col1.markdown(f'<div class="custom-card" style="text-align:center; padding: 1rem;"><h3 style="margin-top:0; font-size: 1.1rem;">Total Assessed</h3><h2 style="color:#D4AF37; margin:0; font-size: 2rem;">{total}</h2></div>', unsafe_allow_html=True)
                col2.markdown(f'<div class="custom-card" style="text-align:center; padding: 1rem;"><h3 style="margin-top:0; font-size: 1.1rem;">Acceptance Rate</h3><h2 style="color:#4CAF50; margin:0; font-size: 2rem;">{acceptance_rate:.1f}%</h2></div>', unsafe_allow_html=True)
                col3.markdown(f'<div class="custom-card" style="text-align:center; padding: 1rem;"><h3 style="margin-top:0; font-size: 1.1rem;">Top Destination</h3><h2 style="color:#D4AF37; margin:0; font-size: 2rem;">{top_country}</h2></div>', unsafe_allow_html=True)
    except Exception as e:
        pass

    st.markdown("""
    <div class="custom-card">
        <h3 style="margin-top: 0;">Project Overview</h3>
        <p>SwiftVisa automates visa eligibility assessment by extracting official immigration policies, structuring them into a searchable knowledge base, retrieving relevant policy sections using semantic search, and generating eligibility decisions using an LLM.</p>
        <p>Unlike rule-based systems, SwiftVisa performs context-aware reasoning grounded in real policy documents, acting as an AI visa officer providing policy-grounded decisions, transparent reasoning, and fast eligibility insights.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="custom-card">
            <h3 style="margin-top: 0;">Key Features 🌟</h3>
            <ul style="color: #A0AEC0; font-size: 1.05rem; line-height: 1.6;">
                <li>Policy-grounded decision making</li>
                <li>Metadata-based semantic retrieval</li>
                <li>Confidence scoring system</li>
                <li>Fully local AI system (no API dependency)</li>
                <li>Scalable RAG architecture</li>
                <li>Decision logging system</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="custom-card">
            <h3 style="margin-top: 0;">Supported Countries 🌎</h3>
            <p style="color: #A0AEC0;">USA, Canada, United Kingdom, Germany, France, Ireland, Netherlands, Australia, New Zealand, Sweden, Singapore, UAE</p>
            <hr/>
            <h3 style="margin-top: 0;">Tech Stack ⚙️</h3>
            <p style="color: #A0AEC0;">
            <strong>Core:</strong> Python, LangChain, FAISS<br>
            <strong>AI:</strong> HuggingFace Embeddings, Phi-3 Mini<br>
            <strong>UI/Server:</strong> Streamlit, LM Studio
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Start Eligibility Assessment", use_container_width=True):
        st.session_state.page = "Input Form"
        st.rerun()

# -------------------------------------------------
# Page 1: Input Form
# -------------------------------------------------
def page_input_form():
    st.title("📝 User Input Form")
    st.markdown('<div class="subtitle">Please provide the applicant details to evaluate their visa eligibility securely.</div>', unsafe_allow_html=True)
    
    with st.form("eligibility_form"):
        col1, col2 = st.columns(2, gap="large")

        with col1:
            age = st.number_input("👤 Age", min_value=16, max_value=70, step=1)
            nationality = st.text_input("🌎 Nationality")
            education = st.selectbox("🎓 Education Level", ["High School", "Diploma", "Bachelor's Degree", "Master's Degree", "PhD"])

        with col2:
            employment = st.text_input("💼 Employment Status")
            income = st.text_input("💵 Annual Income (e.g. 60000 USD)")
            country = st.selectbox("✈️ Destination Country", ["usa","canada","united kingdom","germany","australia","france","ireland","netherlands","sweden","new zealand","singapore","united arab emirates"])
            visa_type = st.selectbox("📜 Visa Type", ["student visa", "skilled worker", "employment visa", "eu blue card"])

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("🚀 Evaluate Eligibility")
        
    if submit:
        if not nationality or not employment or not income:
            st.warning("⚠️ All fields are required.")
            return

        user_data = {
            "age": age, "nationality": nationality, "education": education,
            "employment": employment, "income": income,
            "country": country.lower(), "visa_type": visa_type.lower()
        }

        with st.spinner("⏳ Retrieving official policy documents..."):
            context, source_links = retrieve_policy(user_data["country"], user_data["visa_type"])

        if not context:
            st.error("❌ No matching policy found in the database. Please try another combination.")
            return

        prompt = f"""
You are a Senior AI Visa Advisor. Evaluate this applicant profile against the provided policy context.
DO NOT OUTPUT JSON. Output your response STRICTLY in the following text format:

DECISION: <Eligible | Possibly Eligible | Not Eligible>
CONFIDENCE: <0 to 1 float>

REASONING:
<Write all explanations here>

EDUCATION_SCORE: <integer 0-100>
INCOME_SCORE: <integer 0-100>
EXPERIENCE_SCORE: <integer 0-100>

MISSING_QUALIFICATIONS:
- <item 1 or None>

ACTIONABLE_SUGGESTIONS:
- <item 1 or None>

DOCUMENT_CHECKLIST:
- <item 1 or None>

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
        with st.spinner("🧠 Analyzing applicant profile..."):
            result = generate_response(prompt)

        # Parse Text Response via Regex Fallback
        decision_match = re.search(r"DECISION:\s*(.*)", result, re.IGNORECASE)
        confidence_match = re.search(r"CONFIDENCE:\s*([0-9.]+)", result, re.IGNORECASE)
        
        ed_match = re.search(r"EDUCATION_SCORE:\s*([0-9]+)", result, re.IGNORECASE)
        inc_match = re.search(r"INCOME_SCORE:\s*([0-9]+)", result, re.IGNORECASE)
        exp_match = re.search(r"EXPERIENCE_SCORE:\s*([0-9]+)", result, re.IGNORECASE)

        def extract_list(header, text):
            pattern = rf"{header}:\s*(.*?)(?=\n[A-Z_]+:|$)"
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                items = re.findall(r"-\s*(.+)", match.group(1))
                return [i.strip() for i in items if i.strip().lower() != 'none']
            return []

        decision = decision_match.group(1).strip() if decision_match else "Decision Unknown"
        confidence_value = float(confidence_match.group(1)) if confidence_match else 0.0
        
        sub_scores = {
            "education_score": int(ed_match.group(1)) if ed_match else 0,
            "income_score": int(inc_match.group(1)) if inc_match else 0,
            "experience_score": int(exp_match.group(1)) if exp_match else 0
        }

        missing_quals = extract_list("MISSING_QUALIFICATIONS", result)
        suggestions = extract_list("ACTIONABLE_SUGGESTIONS", result)
        checklist = extract_list("DOCUMENT_CHECKLIST", result)

        confidence_level = "High" if confidence_value >= 0.75 else "Medium" if confidence_value >= 0.4 else "Low"

        # Bundle extracted results
        st.session_state.result_data = {
            "decision": decision,
            "confidence_value": confidence_value,
            "confidence_level": confidence_level,
            "sub_scores": sub_scores,
            "missing_quals": missing_quals,
            "suggestions": suggestions,
            "checklist": checklist,
            "source_links": list(source_links) if source_links else [],
            "user_data": user_data,
            "raw_result": result,
            "context": context,
            "prompt": prompt
        }

        log_decision(user_data, decision, confidence_value, confidence_level)
        st.session_state.evaluation_done = True
        st.session_state.page = "Eligibility Result"
        st.rerun()

# -------------------------------------------------
# Page 2: Eligibility Result
# -------------------------------------------------
def page_eligibility_result():
    res = st.session_state.result_data
    
    st.title("📊 Eligibility Result")
    st.markdown('<div class="subtitle">High-level summary of the visa eligibility assessment.</div>', unsafe_allow_html=True)
    
    decision_color = "#4CAF50" if "eligible" in res['decision'].lower() and "not" not in res['decision'].lower() else "#F44336" if "not eligible" in res['decision'].lower() else "#FF9800"
    decision_icon = "✅" if "eligible" in res['decision'].lower() and "not" not in res['decision'].lower() else "❌" if "not eligible" in res['decision'].lower() else "⚠️"

    # Main Card
    st.markdown(f"""
    <div class="custom-card" style="text-align: center; padding: 3rem;">
        <h2 style="color: {decision_color} !important; font-size: 2.5rem; margin-bottom: 5px;">{decision_icon} {res['decision']}</h2>
        <p style="color: #A0AEC0; font-size: 1.2rem;">Final AI Determination</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown(f"### 🎯 Confidence: **{res['confidence_level']}**")
        st.progress(res['confidence_value'])
        st.metric("Overall Score", f"{round(res['confidence_value']*100)}%")
        
        sub_scores = res.get('sub_scores', {})
        if sub_scores:
            st.markdown("---")
            st.markdown("#### 📈 Category Breakdown")
            
            edu = sub_scores.get('education_score', 0)
            inc = sub_scores.get('income_score', 0)
            exp = sub_scores.get('experience_score', 0)
            
            st.markdown(f"<div style='margin-bottom: -15px;'><small>🎓 Education Match: {edu}%</small></div>", unsafe_allow_html=True)
            st.progress(edu / 100)
            
            st.markdown(f"<div style='margin-bottom: -15px;'><small>💵 Financial Requirements: {inc}%</small></div>", unsafe_allow_html=True)
            st.progress(inc / 100)
            
            st.markdown(f"<div style='margin-bottom: -15px;'><small>💼 Experience Match: {exp}%</small></div>", unsafe_allow_html=True)
            st.progress(exp / 100)
            
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### 🏛️ Official Sources")
        if res['source_links']:
            for link in res['source_links']:
                st.markdown(f"- 🔗 [{link}]({link})")
        else:
            st.info("No explicit source links returned.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🧠 View Detailed Reasoning ➔", use_container_width=True):
        st.session_state.page = "Detailed Reasoning"
        st.rerun()

# -------------------------------------------------
# Page 3: Detailed Reasoning
# -------------------------------------------------
def page_detailed_reasoning():
    res = st.session_state.result_data
    
    st.title("🧠 Detailed Reasoning")
    st.markdown('<div class="subtitle">In-depth breakdown of the AI decision based on policy documents.</div>', unsafe_allow_html=True)

    with st.expander("📝 Applicant Profile Context", expanded=False):
        st.json(res["user_data"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### ❌ Missing Qualifications")
        if res.get('missing_quals'):
            for q in res['missing_quals']:
                if q.lower() != 'none':
                    st.markdown(f"- {q}")
        else:
            st.markdown("- None identified.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### 💡 Actionable Suggestions")
        if res.get('suggestions'):
            for s in res['suggestions']:
                if s.lower() != 'none':
                    st.markdown(f"- {s}")
        else:
            st.markdown("- None identified.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Required Document Checklist")
    if res.get('checklist'):
        for doc in res['checklist']:
            st.checkbox(doc, value=False, key=doc)
    else:
        st.markdown("No specific documents generated.")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get('dev_mode', False):
        st.markdown("---")
        st.markdown("### 🔍 Developer Mode Debug Logs")
        with st.expander("Raw AI JSON Output", expanded=False):
            st.code(res.get('raw_result', ''), language="json")
        with st.expander("Retrieved RAG FAISS Chunks", expanded=False):
            st.markdown(res.get('context', ''))
        with st.expander("Full Structured Prompt Sent to LLM", expanded=False):
            st.code(res.get('prompt', ''), language="text")

    if st.button("⬅️ Back to Results", use_container_width=True):
        st.session_state.page = "Eligibility Result"
        st.rerun()

# -------------------------------------------------
# Page 4: AI Assistant (Chat)
# -------------------------------------------------
def page_ai_assistant():
    st.title("🤖 AI Visa Assistant")
    st.markdown('<div class="subtitle">Ask any general immigration or visa-related questions here!</div>', unsafe_allow_html=True)
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! I am your AI Visa Advisor. How can I assist you with your immigration queries today?"}
        ]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("E.g., What is the minimum salary for an EU Blue Card in Germany?")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Basic context awareness: append the last few messages to the prompt
                conversation_context = "\\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.chat_history[-4:]])
                prompt = f"You are a helpful AI Visa Advisor. Answer the user's question clearly and professionally.\n\nConversation so far:\n{conversation_context}\n\nAssistant:"
                
                try:
                    response = generate_response(prompt)
                except Exception as e:
                    response = "I'm having trouble connecting to my AI brain right now. Please check if the local server is running."

                st.markdown(response)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# -------------------------------------------------
# App Router
# -------------------------------------------------
def main():
    sidebar_navigation()
    
    if st.session_state.page == "Home":
        page_home()
    elif st.session_state.page == "Input Form":
        page_input_form()
    elif st.session_state.page == "Eligibility Result":
        page_eligibility_result()
    elif st.session_state.page == "Detailed Reasoning":
        page_detailed_reasoning()
    elif st.session_state.page == "AI Assistant":
        page_ai_assistant()

if __name__ == "__main__":
    main()