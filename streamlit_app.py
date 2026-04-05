import streamlit as st
import re
import json
import os
from datetime import datetime
from local_eligibility_agent import retrieve_policy, generate_response

# -------------------------------------------------
# Page Config & State Init
# -------------------------------------------------
st.set_page_config(
    page_title="SwiftVisa - Premium AI System",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def init_session_state():
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    if "evaluation_done" not in st.session_state:
        st.session_state.evaluation_done = False
    if "result_data" not in st.session_state:
        st.session_state.result_data = {}
    if "dev_mode" not in st.session_state:
        st.session_state.dev_mode = False

init_session_state()

# -------------------------------------------------
# Utility Functions
# -------------------------------------------------
def log_decision(user_data, decision, confidence_value, confidence_level):
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_profile": user_data,
            "decision": decision,
            "confidence_value": confidence_value,
            "confidence_level": confidence_level
        }
        logs = []
        if os.path.exists("decision_logs.json"):
            with open("decision_logs.json", "r") as f:
                logs = json.load(f)
        logs.append(log_entry)
        with open("decision_logs.json", "w") as f:
            json.dump(logs, f, indent=2)
    except Exception:
        pass

def extract_section(header, text):
    pattern = rf"(?:\d+\.\s*)?{header}[:\s]*(.*?)(?=\n\s*(?:\d+\.)?\s*[A-Z_ ]+:|$)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""

def extract_list(header, text):
    block = extract_section(header, text)
    if block:
        items = re.findall(r"(?:-|\•|\d+\.)\s*(.+)", block)
        if not items:
            lines = [line.strip() for line in block.split("\n") if line.strip()]
            return [l for l in lines if l.lower() != "none"]
        return [i.strip() for i in items if i.strip().lower() != "none"]
    return []

def extract_subfield(section_text, field_name):
    pattern = rf"(?:-\s*)?{field_name}[:\s]+(.*?)(?=\n(?:-\s*)?[A-Za-z ]+[:\s]|$)"
    match = re.search(pattern, section_text, re.DOTALL | re.IGNORECASE)
    if match:
        val = match.group(1).strip()
        if val.startswith('-'):
            val = val[1:].strip()
        return val
    return "Not explicitly detailed."

# -------------------------------------------------
# Premium Theming (Glassmorphism & Navbar Core)
# -------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Obliterate Sidebar entirely */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
button[title="View fullscreen"] { display: none !important; }
[data-testid="stHeader"] { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }

/* Push content to edge removing native header gap */
.block-container { padding-top: 0 !important; }

/* Background Base */
.stApp {
    background-color: #050505;
    background-image: radial-gradient(circle at 10% 20%, rgba(138, 43, 226, 0.15) 0%, transparent 40%),
                      radial-gradient(circle at 90% 80%, rgba(0, 191, 255, 0.15) 0%, transparent 40%);
    background-attachment: fixed;
    color: #E2E8F0;
    font-family: 'Inter', sans-serif;
}

/* Base Headings */
h1, h2, h3, h4 { color: #FFFFFF !important; font-weight: 700; margin-top:0; }
h1 { font-size: 3rem !important; background: -webkit-linear-gradient(45deg, #F9D05F, #D4AF37); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
p, li { color: #A0AEC0; font-size: 1rem; line-height: 1.6; }
.subtitle { font-size: 1.2rem; color: #8A9CA8; margin-bottom: 2rem; font-weight: 300; }

/* -------------------------------------
   SAAS TOP NAVBAR INJECTION 
-------------------------------------- */
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type {
    position: sticky;
    top: 0;
    z-index: 9999;
    background: rgba(5, 5, 5, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding: 1.5rem 2rem 0.5rem 2rem;
    margin-left: -3rem;
    margin-right: -3rem;
    margin-bottom: 2rem;
    align-items: center; /* Vertically align items */
}

/* Nav Link overrides - Strip buttons to pristine text logic */
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #E0E0E0 !important;
    font-weight: 500 !important;
    font-size: 1.1rem !important;
    padding: 0 !important;
    height: auto !important;
    min-height: 0 !important;
    transition: color 0.3s ease, text-shadow 0.3s ease !important;
}
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type button p {
    margin: 0 !important;
    padding: 0 !important;
}
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-of-type button:hover {
    color: #D4AF37 !important;
    text-shadow: 0 0 12px rgba(212,175,55,0.4) !important;
    transform: none !important;
}

/* Isolated Static HTML Blocks */
.glass-card {
    background: rgba(20, 20, 20, 0.5);
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}
.glass-card:hover {
    transform: translateY(-4px);
    border-color: rgba(212, 175, 55, 0.4);
    box-shadow: 0 12px 40px rgba(212, 175, 55, 0.1);
}

/* Base form interactions */
[data-testid="stForm"] {
    background: rgba(15, 15, 15, 0.6) !important;
    backdrop-filter: blur(15px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px;
    padding: 3rem 2.5rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
}
[data-testid="stForm"] h4 { color: #D4AF37 !important; margin-top: 15px; margin-bottom: 10px; }
[data-testid="stForm"] hr { border-color: rgba(255,255,255,0.1); margin: 20px 0; }

label { color: #D4AF37 !important; font-weight: 500 !important; font-size: 0.95rem !important; }

/* Responsive Input Resets */
[data-testid="stTextInput"] input, 
[data-testid="stNumberInput"] input, 
[data-testid="stSelectbox"] > div > div {
    background-color: rgba(5,5,5,0.8) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
    transition: all 0.3s ease;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] * { color: white !important; }

[data-testid="stTextInput"] input:focus, 
[data-testid="stNumberInput"] input:focus, 
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: #D4AF37 !important;
    box-shadow: 0 0 10px rgba(212, 175, 55, 0.3) !important;
}
ul[role="listbox"] { background-color: #1A1A1A !important; }
ul[role="listbox"] li { color: #FFFFFF !important; }

/* Core Animated Button */
/* This ensures non-navbar buttons look bold and clear (like form submit) */
div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div:not(:first-child) div.stButton > button {
    background: linear-gradient(135deg, #111 0%, #000 100%);
    color: #D4AF37 !important;
    border: 1px solid #D4AF37;
    border-radius: 8px;
    height: 50px;
    width: 100%;
    font-weight: 600;
    font-size: 1.1rem;
    box-shadow: 0 4px 15px rgba(212, 175, 55, 0.1);
    transition: all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
}
div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div:not(:first-child) div.stButton > button:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 10px 25px rgba(212, 175, 55, 0.3);
    background: linear-gradient(135deg, #D4AF37 0%, #B89620 100%);
    color: #000 !important;
    border-color: transparent;
}

/* Specific Glowing Badges for Results */
.glow-badge-eligible { text-align: center; padding: 2rem; border-radius: 16px; background: rgba(76, 175, 80, 0.05); border: 1px solid rgba(76, 175, 80, 0.5); box-shadow: 0 0 30px rgba(76, 175, 80, 0.3); }
.glow-badge-ineligible { text-align: center; padding: 2rem; border-radius: 16px; background: rgba(244, 67, 54, 0.05); border: 1px solid rgba(244, 67, 54, 0.5); box-shadow: 0 0 30px rgba(244, 67, 54, 0.3); }
.glow-badge-warning { text-align: center; padding: 2rem; border-radius: 16px; background: rgba(255, 152, 0, 0.05); border: 1px solid rgba(255, 152, 0, 0.5); box-shadow: 0 0 30px rgba(255, 152, 0, 0.3); }

/* Animations */
@keyframes fadeInSlide {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-in-section {
    animation: fadeInSlide 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

/* glowing checklist selector */
div[data-testid="stVerticalBlockBorderWrapper"]:has(div.checklist-marker) {
    box-shadow: 0 0 30px rgba(212, 175, 55, 0.25) !important;
    border: 1px solid #D4AF37 !important;
    background: rgba(20,20,20,0.85) !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Top Sticky Navbar UI
# -------------------------------------------------
def top_navbar():
    current = st.session_state.page
    
    # st.columns structure to align correctly with padding logic.
    nav_cols = st.columns([6, 1, 1.5, 1.2, 1.2])
    
    with nav_cols[0]:
        st.markdown('<p style="font-size:1.6rem; font-weight:700; margin:0; padding-top:4px; line-height:1; letter-spacing: -0.5px; background: -webkit-linear-gradient(45deg, #F9D05F, #D4AF37); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">SwiftVisa AI</p>', unsafe_allow_html=True)
        
    def nav_link(col, label, target_page):
        with col:
            st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
            if st.button(label, use_container_width=True):
                # Ensure validation tracking
                if target_page == "Master Result" and not st.session_state.get('evaluation_done', False):
                    st.session_state.page = "Input Form"
                else:
                    st.session_state.page = target_page
                st.rerun()
            
            # Active Indicator UI Gold Line
            if current == target_page:
                st.markdown('<div style="height:2px; background:#D4AF37; width:60%; max-width:80px; margin: 6px auto 0 auto; box-shadow:0 0 10px rgba(212,175,55,0.8);"></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    nav_link(nav_cols[1], "Home", "Home")
    nav_link(nav_cols[2], "New Evaluation", "Input Form")
    nav_link(nav_cols[3], "Dashboard", "Master Result")
    nav_link(nav_cols[4], "AI Assistant", "AI Assistant")


# -------------------------------------------------
# Page Views
# -------------------------------------------------
def page_home():
    st.markdown('<h1 style="text-align: center;">Visa Screening Reimagined.</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle" style="text-align: center;">Advanced AI semantic retrieval replacing the guesswork.</div>', unsafe_allow_html=True)
    
    colA, colB, colC = st.columns([1,2,1])
    with colB:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Begin Evaluation Setup", use_container_width=True):
            st.session_state.page = "Input Form"
            st.rerun()
            
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.markdown("""<div class="glass-card" style="text-align: center;"><p style="font-size:2.5rem; margin-bottom:0;">⚡</p><h3 style="font-size:1.3rem;">Lightning Fast</h3><p>Real-time eligibility via vector retrieval.</p></div>""", unsafe_allow_html=True)
    c2.markdown("""<div class="glass-card" style="text-align: center;"><p style="font-size:2.5rem; margin-bottom:0;">🏛️</p><h3 style="font-size:1.3rem;">Policy Grounded</h3><p>Direct database mapping for accurate truths.</p></div>""", unsafe_allow_html=True)
    c3.markdown("""<div class="glass-card" style="text-align: center;"><p style="font-size:2.5rem; margin-bottom:0;">🧠</p><h3 style="font-size:1.3rem;">AI Reasoning</h3><p>Actionable extraction for immediate profile improvements.</p></div>""", unsafe_allow_html=True)


def page_input_form():
    st.title("User Profile Setup")
    st.markdown('<div class="subtitle">Securely enter the primary applicant details below.</div>', unsafe_allow_html=True)
    
    with st.form("eligibility_form"):
        st.markdown("#### 1. Personal Information", unsafe_allow_html=True)
        colP1, colP2, colP3 = st.columns(3, gap="medium")
        with colP1:
            full_name = st.text_input("👤 Full Name", placeholder="e.g. John Doe")
        with colP2:
            age = st.number_input("📅 Age", min_value=16, max_value=80, step=1)
        with colP3:
            nationality = st.text_input("🌍 Nationality", placeholder="e.g. Indian")
            
        colP4, colP5 = st.columns(2, gap="medium")
        with colP4:
            dob = st.date_input("🎂 Date of Birth")
        with colP5:
            sex = st.selectbox("⚤ Sex", ["Male", "Female", "Other"])

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("#### 2. Education Details", unsafe_allow_html=True)
        colE1, colE2 = st.columns(2, gap="medium")
        with colE1:
            education = st.selectbox("🎓 Highest Education Level", ["High School", "Diploma", "Bachelor's Degree", "Master's Degree", "PhD"])
        with colE2:
            field_study = st.text_input("📚 Field of Study", placeholder="e.g. Computer Science")

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("#### 3. Employment Details", unsafe_allow_html=True)
        colW1, colW2 = st.columns(2, gap="medium")
        with colW1:
            employment = st.selectbox("💼 Employment Status", ["Employed", "Self-Employed", "Student", "Unemployed"])
        with colW2:
            experience = st.number_input("⏳ Years of Experience", min_value=0, max_value=50, step=1)

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("#### 4. Financial & Visa Information", unsafe_allow_html=True)
        colV1, colV2, colV3 = st.columns(3, gap="medium")
        with colV1:
            income = st.text_input("💰 Annual Income", placeholder="e.g. 60000 USD")
        with colV2:
            country = st.selectbox("✈️ Destination Country", ["USA","Canada","United Kingdom","Germany","Australia","France","Ireland","Netherlands","Sweden","New Zealand","Singapore","United Arab Emirates"])
        with colV3:
            visa_type = st.selectbox("📜 Visa Type", ["Student Visa", "Skilled Worker", "Employment Visa", "EU Blue Card"])

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("#### 5. Pre-Evaluation Confirmation", unsafe_allow_html=True)
        cb1 = st.checkbox("I confirm that the provided information is accurate")
        cb2 = st.checkbox("I agree to AI-based eligibility modeling extraction")
        cb3 = st.checkbox("I understand this is a preliminary non-legal assessment")

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("Generate AI Master Report ➔")
        
    if submit:
        if not (cb1 and cb2 and cb3):
            st.error("⚠️ Requirements Missing: You must manually check all confirmation boxes.")
            return

        if not full_name or not nationality or not field_study or not income:
            st.error("⚠️ Invalid Form: All text fields are strictly required.")
            return

        user_data = {
            "full_name": full_name, "age": age, "dob": dob.strftime("%Y-%m-%d"), "sex": sex, "nationality": nationality, 
            "education": education, "field_study": field_study,
            "employment": employment, "experience": experience,
            "income": income, "country": country.lower(), "visa_type": visa_type.lower()
        }

        with st.spinner("⏳ Vectorizing profile directly against policy databases..."):
            context, source_links = retrieve_policy(user_data["country"], user_data["visa_type"])

        if not context:
            st.error("❌ Vector Sync Error: No matching official policy found under this tier layout.")
            return

        prompt = f"""
You are an expert immigration eligibility officer.

Evaluate the applicant STRICTLY using the provided policy context.

----------------------------------------
USER PROFILE:
Name: {full_name}
Age: {age}
Date of Birth: {dob.strftime("%Y-%m-%d")}
Sex: {sex}
Nationality: {nationality}
Education: {education}
Field of Study: {field_study}
Employment: {employment} ({experience} years of experience)
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
        with st.spinner(f"🧠 Computing Master Reasoning Tree for {full_name}..."):
            result = generate_response(prompt)
            result = re.sub(r"-{4,}", "", result)

        decision_raw = extract_section("Decision", result)
        if "not eligible" in decision_raw.lower(): decision = "Not Eligible"
        elif "possibly eligible" in decision_raw.lower(): decision = "Possibly Eligible"
        else: decision = "Eligible"
        
        conf_match = re.search(r"([0-9.]+)", extract_section("Confidence", result))
        try: confidence_value = float(conf_match.group(1)) if conf_match else 0.5
        except ValueError: confidence_value = 0.5

        st.session_state.result_data = {
            "decision": decision,
            "decision_raw": decision_raw,
            "confidence_value": confidence_value,
            "confidence_level": "High" if confidence_value >= 0.75 else "Medium" if confidence_value >= 0.4 else "Low",
            "edu_text": extract_subfield(result, "Education Assessment"),
            "emp_text": extract_subfield(result, "Employment Assessment"),
            "inc_text": extract_subfield(result, "Income Assessment"),
            "pol_text": extract_subfield(result, "Policy Match"),
            "reqs_met": extract_list("Requirements Met", result),
            "reqs_not_met": extract_list("Requirements Not Met", result),
            "risks": extract_list("Risk Factors", result),
            "suggestions": extract_list("Actionable Suggestions", result),
            "checklist": extract_list("Required Documents", result),
            "conclusion_text": extract_section("Final Assessment", result),
            "source_links": list(source_links) if source_links else [],
            "user_data": user_data
        }

        log_decision(user_data, decision, confidence_value, st.session_state.result_data["confidence_level"])
        st.session_state.evaluation_done = True
        
        st.session_state.page = "Master Result"
        st.rerun()


def page_master_result():
    res = st.session_state.result_data
    
    # [A. HEADER]
    st.markdown(f'<h1 style="color:#D4AF37 !important;">Hello, {res["user_data"]["full_name"]}</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Here is your AI-based consolidated visa eligibility report.</div>', unsafe_allow_html=True)

    # [B. FINAL DECISION CARD] & [C. CONFIDENCE] mapped to raw strings
    dt = res['decision'].lower()
    if "not eligible" in dt:  badge, icon, color = "glow-badge-ineligible", "⛔", "#F44336"
    elif "possibly" in dt: badge, icon, color = "glow-badge-warning", "⚠️", "#FF9800"
    else: badge, icon, color = "glow-badge-eligible", "✅", "#4CAF50"

    justification_match = re.search(r"\n(.+)", res['decision_raw'])
    short_justification = justification_match.group(1) if justification_match else ""

    top_card_html = f"""
    <div class="{badge}" style="margin-bottom: 2rem;">
        <h2 style="color: {color} !important; font-size: 3rem; margin-bottom: 5px;">{icon} {res['decision'].upper()}</h2>
        <p style="color: rgba(255,255,255,0.85); font-size: 1.1rem; margin-bottom:0;">{short_justification}</p>
    </div>
    """
    
    cc1, cc2 = st.columns([1, 3])
    with cc1:
        st.metric(label="AI Confidence Match", value=f"{round(res['confidence_value']*100)}%")
        st.progress(res['confidence_value'])
    with cc2:
        st.markdown(f"<p style='margin-top:10px; color:#A0AEC0;'>Confidence Band: <span style='color:{color}; font-weight:700;'>{res['confidence_level']}</span>. This assessment reflects model alignment accuracy strictly tied to official semantic vectors retrieved for {res['user_data']['country'].title()}.</p>", unsafe_allow_html=True)

    st.markdown(top_card_html, unsafe_allow_html=True)

    # [D. ELIGIBILITY BREAKDOWN]
    st.markdown("### 🔍 Evaluation Breakdown")
    b1, b2 = st.columns(2)
    with b1:
        st.markdown(f'<div class="glass-card"><h4 style="margin-top:0;">🎓 Education Assessment</h4><p>{res.get("edu_text", "Not explicitly detailed.")}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="glass-card"><h4 style="margin-top:0;">💰 Income Assessment</h4><p>{res.get("inc_text", "Not explicitly detailed.")}</p></div>', unsafe_allow_html=True)
    with b2:
        st.markdown(f'<div class="glass-card"><h4 style="margin-top:0;">💼 Employment Assessment</h4><p>{res.get("emp_text", "Not explicitly detailed.")}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="glass-card"><h4 style="margin-top:0;">🌍 Policy Match</h4><p>{res.get("pol_text", "Not explicitly detailed.")}</p></div>', unsafe_allow_html=True)

    # [E. REQUIREMENTS SECTION]
    st.markdown("### ⚖️ Protocol Requirements")
    r1, r2 = st.columns(2)
    
    met_html = '<div class="glass-card"><h4 style="color:#4CAF50 !important; margin-top:0;">✅ Requirements Met</h4>'
    if res['reqs_met']: 
        for i in res['reqs_met']: met_html += f"<div style='margin-bottom:5px;'>• {i}</div>"
    else: met_html += "<div>None explicitly confirmed.</div>"
    met_html += '</div>'
    
    notmet_html = '<div class="glass-card"><h4 style="color:#F44336 !important; margin-top:0;">❌ Missing Attributes</h4>'
    if res['reqs_not_met']:
        for i in res['reqs_not_met']: notmet_html += f"<div style='margin-bottom:5px;'>• {i}</div>"
    else: notmet_html += "<div>✅ *No structural missing traits identified.*</div>"
    notmet_html += '</div>'
    
    r1.markdown(met_html, unsafe_allow_html=True)
    r2.markdown(notmet_html, unsafe_allow_html=True)

    # [F. RISK FACTORS & G. ACTIONABLE SUGGESTIONS]
    sr1, sr2 = st.columns(2)
    risk_html = '<div class="glass-card"><h4 style="color:#FF9800 !important; margin-top:0;">⚠️ Associated Risk Factors</h4>'
    if res['risks']: 
        for i in res['risks']: risk_html += f"<div style='margin-bottom:5px; color:#E2E8F0;'>• {i}</div>"
    else: risk_html += "<div style='color:#A0AEC0;'>No isolated risks flagged.</div>"
    risk_html += '</div>'
    
    sugg_html = '<div class="glass-card"><h4 style="color:#60A5FA !important; margin-top:0;">✨ Actionable Suggestions</h4>'
    if res['suggestions']: 
        for i in res['suggestions']: sugg_html += f"<div style='margin-bottom:5px; color:#E2E8F0;'>• {i}</div>"
    else: sugg_html += "<div style='color:#A0AEC0;'>No strategic upgrades required.</div>"
    sugg_html += '</div>'

    sr1.markdown(risk_html, unsafe_allow_html=True)
    sr2.markdown(sugg_html, unsafe_allow_html=True)

    # [H. DOCUMENT CHECKLIST (GATEKEEPER)]
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown('<div class="checklist-marker" style="display:none;"></div>', unsafe_allow_html=True) # CSS targeted hook
        st.markdown("<h3 style='margin-top:0; color:#D4AF37;'>📂 Official Verification Protocol</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#E2E8F0; font-size:1.1rem; margin-bottom:15px;'>Please confirm the following documents are ready to view your final official assessment.</p>", unsafe_allow_html=True)
        
        all_checked = True
        if res.get('checklist'):
            # Generate checkboxes linked to Session State memory to prevent screen reset
            for i, doc in enumerate(res['checklist']):
                c_key = f"chk_{i}"
                if c_key not in st.session_state:
                    st.session_state[c_key] = False
                st.checkbox(doc, key=c_key)
                if not st.session_state[c_key]:
                    all_checked = False
        else:
            st.info("No interactive documents were mathematically extracted.")

    if not all_checked:
        return # Soft stop, gracefully halting execution without throwing error blocks!

    # [I. FINAL CONCLUSION] & [J. SOURCES] (Unlocks smoothly behind checklist)
    conclusion_html = f"""
    <div class="glass-card fade-in-section" style="border-left: 4px solid #D4AF37; margin-top:2rem;">
        <h3 style="color:#D4AF37; margin-top:0;">📋 Final Conclusion Summary</h3>
        <p style="font-size:1.15rem; color:#E2E8F0; line-height:1.6; margin-bottom:0;">{res.get('conclusion_text', 'No conclusion provided.')}</p>
    </div>
    """
    
    links_html = ""
    if res['source_links']:
        for link in res['source_links']: links_html += f"<div style='margin-bottom:8px;'>🔗 <a href='{link}' style='color:#60A5FA; text-decoration:none;' target='_blank'>{link}</a></div>"
    else: links_html = "<p style='color:#A0AEC0;'>No explicit source links extracted securely by vector storage.</p>"

    source_html = f"""
    <div class="glass-card fade-in-section" style="animation-delay: 0.15s;">
        <h3 style="margin-top:0;">🏛️ Grounding Citations (Sources)</h3>
        {links_html}
    </div>
    """
    st.markdown(conclusion_html + source_html, unsafe_allow_html=True)


def page_ai_assistant():
    st.title("💬 Legal & Policy Assistant")
    st.markdown('<div class="subtitle">Ask interactive conversational queries regarding global policies.</div>', unsafe_allow_html=True)
    
    with st.container(border=True):
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Hello! I am your SwiftVisa AI companion hooked directly into immigration rules. What can I clarify for you today?"}
            ]
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    st.markdown("<br>", unsafe_allow_html=True)
    user_input = st.chat_input("E.g., What are the standard requirements for an EU Blue Card in Germany?")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing semantic rules..."):
                conversation_context = "\\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.chat_history[-4:]])
                prompt = f"You are an AI Visa Advisor answering questions cleanly.\n\nContext:\n{conversation_context}\n\nAssistant:"
                try: response = generate_response(prompt)
                except Exception: response = "I encountered an error connecting to my contextual brain network."
                st.markdown(response)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

# -------------------------------------------------
# Main Entry Loop
# -------------------------------------------------
def main():
    top_navbar()
    
    # Route interceptor
    pg = st.session_state.page
    if pg == "Home":
        page_home()
    elif pg == "Input Form":
        page_input_form()
    elif pg == "Master Result":
        if not st.session_state.evaluation_done:
            st.warning("⚠️ Invalid Access: You have no active profile setup globally initialized.")
            st.stop()
        page_master_result()
    elif pg == "AI Assistant":
        page_ai_assistant()

if __name__ == "__main__":
    main()