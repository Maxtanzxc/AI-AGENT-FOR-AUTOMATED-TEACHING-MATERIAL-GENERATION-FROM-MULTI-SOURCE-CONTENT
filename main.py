import streamlit as st
from database import init_db, login_user, register_user
from styles import GLOBAL_CSS

st.set_page_config(
    page_title="EduForge AI — Login",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)

init_db()

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user:
    st.switch_page("pages/1_generate.py")

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0;">
        <div style="font-family:'Space Grotesk',sans-serif; font-size:1.3rem; font-weight:700; color:#F8FAFC;">
            Edu<span style="color:#00F5D4;">Forge</span> AI
        </div>
        <div style="font-size:0.75rem; color:#94A3B8; margin-top:0.2rem;">
            Multi-source Teaching Material Generator
        </div>
    </div>
    <div class="glow-divider"></div>
    <div style="font-size:0.8rem; color:#94A3B8; line-height:1.6;">
        Welcome to EduForge AI! Please sign in or create an account to start generating teaching materials.
    </div>
    """, unsafe_allow_html=True)

# ── Hero Section ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 1.5rem 0 1.5rem 0;">
    <div class="hero-title">
        Edu<span>Forge</span> AI
    </div>
    <div class="hero-subtitle">
        Transform any topic or document into structured, beautiful teaching materials instantly tailored for any education level.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Radio Tab Switcher ────────────────────────────────────────────────────────
tab = st.radio(
    "tab", ["Sign In", "Create Account"],
    horizontal=True, label_visibility="collapsed"
)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── Login Form ────────────────────────────────────────────────────────────────
if tab == "Sign In":
    with st.form("login_form"):
        st.markdown('<div class="card-title" style="margin-bottom:0.5rem;">Sign In to your Account</div>', unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        submit = st.form_submit_button("Sign In to Workspace ", use_container_width=True)

    if submit:
        if not username or not password:
            st.error("Please fill in both fields.")
        else:
            result = login_user(username, password)
            if result["success"]:
                st.session_state.user = result["user"]
                st.session_state.generated_output = ""
                st.session_state.current_topic = ""
                st.session_state.current_output_type = ""
                st.session_state.current_level = "Secondary"
                st.session_state.collection = None
                st.session_state.sources_loaded = []
                st.switch_page("pages/1_generate.py")
            else:
                st.error(result["error"])

# ── Register Form ─────────────────────────────────────────────────────────────
else:
    with st.form("register_form"):
        st.markdown('<div class="card-title" style="margin-bottom:0.5rem;">Create New Account</div>', unsafe_allow_html=True)
        new_username = st.text_input("Username", placeholder="Choose a username (min 3 chars)")
        new_email    = st.text_input("Email", placeholder="your@email.com")
        new_password = st.text_input("Password", type="password", placeholder="Min 6 characters")
        confirm      = st.text_input("Confirm password", type="password", placeholder="Repeat password")
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        submit = st.form_submit_button("Create Free Account ", use_container_width=True)

    if submit:
        if not all([new_username, new_email, new_password, confirm]):
            st.error("Please fill in all fields.")
        elif new_password != confirm:
            st.error("Passwords do not match.")
        else:
            result = register_user(new_username, new_email, new_password)
            if result["success"]:
                st.success("Account created successfully! Switch to Sign In tab to log in.")
            else:
                st.error(result["error"])

# ── Feature Showcase Cards ────────────────────────────────────────────────────
st.markdown("""
<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:1rem; margin-top:2rem;">
    <div class="feature-card">
        <div class="feature-icon">📝</div>
        <div class="feature-label">Summary Notes</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-label">Lecture Slides</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">❓</div>
        <div class="feature-label">Quiz Questions</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📖</div>
        <div class="feature-label">Glossary Terms</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Footer Tagline ────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; margin-top:2.5rem; padding-bottom:1rem; animation: fadeIn 1s ease;">
    <div class="glow-divider" style="max-width:260px; margin:0 auto 1.25rem auto;"></div>
    <div style="font-size:0.76rem; color:#94A3B8; letter-spacing:0.5px; display:flex; align-items:center; justify-content:center; gap:0.5rem; flex-wrap:wrap;">
        <span>📄 Upload PDFs</span> · 
        <span>▶️ YouTube Links</span> · 
        <span>🌐 Web Pages</span> · 
        <span>🎓 Tailored Difficulty</span>
    </div>
</div>
""", unsafe_allow_html=True)