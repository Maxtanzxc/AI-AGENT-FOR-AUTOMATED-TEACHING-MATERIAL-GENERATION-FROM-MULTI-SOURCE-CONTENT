GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Space+Grotesk:wght@500;600;700&display=swap');

/* ── Global Canvas & Typography ── */
html, body, [class*="css"] { 
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    letter-spacing: -0.01em;
}

.stApp { 
    background: #070A11; 
    background-image: 
        radial-gradient(at 10% 10%, rgba(0, 245, 212, 0.07) 0px, transparent 50%),
        radial-gradient(at 90% 15%, rgba(0, 180, 216, 0.08) 0px, transparent 50%),
        radial-gradient(at 50% 90%, rgba(99, 102, 241, 0.05) 0px, transparent 60%);
    background-attachment: fixed;
    color: #F8FAFC; 
}

/* ── Hide Default Streamlit Elements & Ugly Auto Navigation ── */
#MainMenu, footer { 
    display: none !important; 
    visibility: hidden !important; 
}

/* Hide default unstyled multi-page sidebar navigation list (main, generate, history) */
[data-testid="stSidebarNav"], 
ul[data-testid="stSidebarNavItems"],
div[data-testid="stSidebarNavSeparator"] {
    display: none !important;
    visibility: hidden !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
    pointer-events: none !important;
    z-index: 99999 !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

/* Enable pointer-events ONLY for sidebar collapse & expand controls */
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
[data-testid="stHeader"] [data-testid="collapsedControl"],
[data-testid="stHeader"] button,
button[kind="header"] {
    pointer-events: auto !important;
    visibility: visible !important;
    display: flex !important;
    opacity: 1 !important;
    color: #00F5D4 !important;
    background: rgba(15, 23, 42, 0.9) !important;
    border: 1px solid rgba(0, 245, 212, 0.4) !important;
    border-radius: 8px !important;
    padding: 0.35rem !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
    transition: all 0.2s ease !important;
}

[data-testid="stSidebarCollapseButton"]:hover,
[data-testid="collapsedControl"]:hover,
[data-testid="stHeader"] button:hover {
    background: rgba(0, 245, 212, 0.2) !important;
    border-color: #00F5D4 !important;
    box-shadow: 0 0 12px rgba(0, 245, 212, 0.4) !important;
}

.block-container {
    padding: 2rem 2rem 3rem 2rem !important;
    max-width: 1240px !important;
}

/* ── Keyframe Animations ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}

@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 12px rgba(0, 245, 212, 0.15); }
    50%      { box-shadow: 0 0 24px rgba(0, 245, 212, 0.35); }
}

@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ── Header Bar ── */
.edu-header {
    background: rgba(15, 23, 42, 0.65) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px;
    padding: 1rem 1.6rem;
    margin: 0 0 1.75rem 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    animation: fadeIn 0.5s ease;
}

.edu-logo {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.55rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.6px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.edu-logo span { 
    background: linear-gradient(135deg, #00F5D4 0%, #00B4D8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.edu-tagline {
    font-size: 0.78rem;
    color: #94A3B8;
    font-weight: 400;
    margin-top: 0.1rem;
}

.user-chip {
    background: rgba(30, 41, 59, 0.7);
    color: #E2E8F0;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.78rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    backdrop-filter: blur(8px);
}

.edu-badge {
    background: linear-gradient(135deg, rgba(0, 245, 212, 0.12) 0%, rgba(0, 180, 216, 0.12) 100%);
    color: #00F5D4;
    border: 1px solid rgba(0, 245, 212, 0.3);
    border-radius: 20px;
    padding: 0.3rem 0.85rem;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
}

/* ── Streamlit Native Form & Expander Card Styling ── */
[data-testid="stForm"] {
    background: rgba(15, 23, 42, 0.6) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
}

[data-testid="stExpander"] {
    background: rgba(15, 23, 42, 0.6) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    overflow: hidden !important;
}

.streamlit-expanderHeader {
    background: rgba(15, 23, 42, 0.8) !important;
    color: #F8FAFC !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
}

.card-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    color: #94A3B8;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Dynamic Gradient Title ── */
.page-title-gradient {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.6rem; 
    font-weight: 700;
    letter-spacing: -0.6px;
    background: linear-gradient(135deg, #FFFFFF 20%, #E2E8F0 50%, #00F5D4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ── Buttons Overrides ── */
.stButton > button {
    background: linear-gradient(135deg, #00F5D4 0%, #00B4D8 100%) !important;
    color: #070A11 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    box-shadow: 0 4px 16px rgba(0, 245, 212, 0.25) !important;
    cursor: pointer !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(0, 245, 212, 0.4) !important;
    filter: brightness(1.08) !important;
}

.stButton > button:active { 
    transform: translateY(0) !important; 
    box-shadow: 0 2px 8px rgba(0, 245, 212, 0.2) !important;
}

/* Download Secondary Button */
.stDownloadButton > button {
    background: rgba(15, 23, 42, 0.75) !important;
    border: 1px solid rgba(0, 245, 212, 0.3) !important;
    color: #F8FAFC !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 0.55rem 1rem !important;
    transition: all 0.25s ease !important;
    backdrop-filter: blur(8px) !important;
}
.stDownloadButton > button:hover {
    background: rgba(0, 245, 212, 0.12) !important;
    border-color: #00F5D4 !important;
    color: #00F5D4 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 16px rgba(0, 245, 212, 0.15) !important;
}

/* ── Form Inputs Overrides ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(11, 15, 25, 0.85) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    color: #F8FAFC !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 0.9rem !important;
    transition: all 0.2s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #00F5D4 !important;
    box-shadow: 0 0 0 3px rgba(0, 245, 212, 0.18) !important;
    background: rgba(11, 15, 25, 0.95) !important;
}

.stSelectbox > div > div {
    background: rgba(11, 15, 25, 0.85) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    color: #F8FAFC !important;
}

.stFileUploader > div {
    background: rgba(11, 15, 25, 0.6) !important;
    border: 1px dashed rgba(0, 245, 212, 0.3) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    transition: border-color 0.2s ease !important;
}
.stFileUploader > div:hover {
    border-color: #00F5D4 !important;
    background: rgba(0, 245, 212, 0.03) !important;
}

/* Labels */
.stTextInput label, .stTextArea label,
.stSelectbox label, .stFileUploader label {
    color: #94A3B8 !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    margin-bottom: 0.3rem !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(7, 10, 17, 0.95) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(20px) !important;
}
[data-testid="stSidebar"] .stButton > button { 
    width: 100%; 
}

/* ── Messages & Toasts ── */
.stSuccess { 
    background: rgba(16, 185, 129, 0.12) !important; 
    border: 1px solid rgba(16, 185, 129, 0.3) !important; 
    color: #34D399 !important;
    border-radius: 10px !important; 
}
.stError { 
    background: rgba(239, 68, 68, 0.12) !important; 
    border: 1px solid rgba(239, 68, 68, 0.3) !important; 
    color: #FCA5A5 !important;
    border-radius: 10px !important; 
}
.stInfo { 
    background: rgba(59, 130, 246, 0.12) !important; 
    border: 1px solid rgba(59, 130, 246, 0.3) !important; 
    color: #93C5FD !important;
    border-radius: 10px !important; 
}
.stWarning { 
    background: rgba(245, 158, 11, 0.12) !important; 
    border: 1px solid rgba(245, 158, 11, 0.3) !important; 
    color: #FCD34D !important;
    border-radius: 10px !important; 
}

/* ── Stat & Metric Cards ── */
.stat-card {
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.75) 0%, rgba(30, 41, 59, 0.5) 100%);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.1rem 1rem;
    text-align: center;
    transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00F5D4, #00B4D8, #6366F1);
    background-size: 200% 100%;
    animation: gradientShift 4s ease infinite;
}
.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(0, 245, 212, 0.12);
    border-color: rgba(0, 245, 212, 0.3);
}
.stat-icon { 
    font-size: 1.4rem; 
    margin-bottom: 0.3rem; 
}
.stat-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.6rem; 
    font-weight: 700;
    color: #00F5D4; 
    line-height: 1.1;
    margin-bottom: 0.25rem;
}
.stat-label {
    font-size: 0.7rem; 
    color: #94A3B8;
    font-weight: 600; 
    text-transform: uppercase; 
    letter-spacing: 0.8px;
}

/* ── Source Pills ── */
.source-pill {
    display: inline-flex; 
    align-items: center; 
    gap: 0.4rem;
    padding: 0.3rem 0.75rem; 
    border-radius: 20px;
    font-size: 0.74rem; 
    font-weight: 600; 
    margin: 0.2rem 0.2rem 0.2rem 0;
    backdrop-filter: blur(8px);
}
.source-pill.success { 
    background: rgba(16, 185, 129, 0.15); 
    color: #34D399; 
    border: 1px solid rgba(16, 185, 129, 0.3); 
}
.source-pill.error { 
    background: rgba(239, 68, 68, 0.15); 
    color: #FCA5A5; 
    border: 1px solid rgba(239, 68, 68, 0.3); 
}

/* ── Output Viewer V2 ── */
.output-box-v2 {
    background: rgba(11, 15, 25, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1.6rem;
    font-size: 0.9rem; 
    line-height: 1.8; 
    color: #E2E8F0;
    max-height: 480px; 
    overflow-y: auto; 
    white-space: pre-wrap;
    animation: fadeIn 0.4s ease;
    box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.3);
}

.output-box-v2 table {
    width: 100% !important;
    border-collapse: collapse !important;
    margin: 1.2rem 0 !important;
    font-size: 0.86rem !important;
    background: rgba(15, 23, 42, 0.7) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid rgba(0, 245, 212, 0.25) !important;
    white-space: normal !important;
}

.output-box-v2 th {
    background: #0B132B !important;
    color: #00F5D4 !important;
    font-weight: 700 !important;
    padding: 0.75rem 1rem !important;
    text-align: left !important;
    border-bottom: 2px solid rgba(0, 245, 212, 0.3) !important;
}

.output-box-v2 td {
    padding: 0.7rem 1rem !important;
    color: #E2E8F0 !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
}

.output-box-v2 tr:nth-child(even) {
    background: rgba(30, 41, 59, 0.45) !important;
}

/* ── History Record Card ── */
.hist-record {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.65rem;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    animation: fadeInUp 0.45s ease both;
    position: relative;
    overflow: hidden;
}
.hist-record::after {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    background: transparent;
    transition: background 0.3s ease;
    border-radius: 0 4px 4px 0;
}
.hist-record:hover {
    border-color: rgba(0, 245, 212, 0.4);
    transform: translateX(4px);
    box-shadow: 0 6px 24px rgba(0, 245, 212, 0.08);
}
.hist-record:hover::after { background: #00F5D4; }
.hist-record.selected {
    border-color: #00F5D4;
    background: rgba(0, 245, 212, 0.06);
}
.hist-record.selected::after { background: #00F5D4; }
.hist-record-topic {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.92rem; 
    font-weight: 600; 
    color: #F8FAFC;
    margin-bottom: 0.35rem; 
    line-height: 1.3;
}

/* ── Type Badges ── */
.type-badge {
    display: inline-flex; 
    align-items: center; 
    gap: 0.3rem;
    padding: 0.15rem 0.55rem; 
    border-radius: 6px;
    font-size: 0.68rem; 
    font-weight: 700; 
    letter-spacing: 0.2px;
}
.type-badge.summary  { background: rgba(59, 130, 246, 0.15); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.3); }
.type-badge.slides   { background: rgba(168, 85, 247, 0.15); color: #C084FC; border: 1px solid rgba(168, 85, 247, 0.3); }
.type-badge.mcq      { background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3); }
.type-badge.glossary { background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }

/* ── Detail Panel Header ── */
.detail-header {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.6) 100%);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.1rem;
    position: relative;
    overflow: hidden;
    animation: fadeIn 0.4s ease;
}
.detail-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00F5D4, #00B4D8, #00F5D4);
    background-size: 200% 100%;
    animation: gradientShift 4s ease infinite;
}

.saved-badge {
    background: rgba(16, 185, 129, 0.15); 
    color: #34D399; 
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 12px; 
    padding: 0.2rem 0.6rem;
    font-size: 0.7rem; 
    font-weight: 700; 
    white-space: nowrap;
}

/* ── Glow Divider ── */
.glow-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 245, 212, 0.4), transparent);
    margin: 1.5rem 0;
    border: none;
}

/* ── Empty State ── */
.empty-state {
    border: 1px dashed rgba(0, 245, 212, 0.3);
    border-radius: 20px;
    padding: 4.5rem 2rem;
    text-align: center;
    background: radial-gradient(ellipse at center, rgba(0, 245, 212, 0.03) 0%, transparent 70%);
    animation: fadeInUp 0.5s ease forwards;
}
.empty-icon {
    font-size: 3.2rem; 
    margin-bottom: 1rem;
    display: inline-block;
    filter: drop-shadow(0 0 12px rgba(0, 245, 212, 0.4));
}

/* ── Login Feature Cards ── */
.feature-card {
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.75) 0%, rgba(30, 41, 59, 0.5) 100%);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.25rem;
    text-align: center;
    min-width: 140px;
    flex: 1;
    transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    position: relative;
    overflow: hidden;
}
.feature-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00F5D4, transparent);
    opacity: 0;
    transition: opacity 0.35s ease;
}
.feature-card:hover {
    transform: translateY(-5px);
    border-color: rgba(0, 245, 212, 0.35);
    box-shadow: 0 10px 30px rgba(0, 245, 212, 0.12);
}
.feature-card:hover::after { opacity: 1; }
.feature-icon { 
    font-size: 1.6rem; 
    margin-bottom: 0.5rem; 
}
.feature-label {
    font-size: 0.8rem; 
    color: #F8FAFC; 
    font-weight: 700;
}

/* ── Hero Components ── */
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3rem; 
    font-weight: 700;
    color: #FFFFFF; 
    letter-spacing: -1.5px;
    margin-bottom: 0.6rem;
    animation: fadeInUp 0.6s ease;
    line-height: 1.1;
}
.hero-title span { 
    background: linear-gradient(135deg, #00F5D4 0%, #00B4D8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-subtitle {
    font-size: 0.95rem; 
    color: #94A3B8;
    max-width: 440px; 
    margin: 0 auto;
    animation: fadeInUp 0.7s ease;
    line-height: 1.6;
}
.hero-badge {
    display: inline-flex; 
    align-items: center; 
    gap: 0.5rem;
    background: rgba(0, 245, 212, 0.1); 
    color: #00F5D4;
    border: 1px solid rgba(0, 245, 212, 0.3);
    border-radius: 20px;
    padding: 0.35rem 0.95rem;
    font-size: 0.75rem; 
    font-weight: 700;
    margin-bottom: 1.5rem;
    animation: pulseGlow 3s infinite ease-in-out, fadeInUp 0.5s ease;
}

/* ── Scrollbar Styling ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(7, 10, 17, 0.5); }
::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.15); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #00F5D4; }

html { scroll-behavior: smooth; }
</style>
"""


def render_header(username: str = None):
    user_html = (
        f'<span class="user-chip">👤 {username}</span>'
        if username else ""
    )
    return f"""
    <div class="edu-header">
        <div>
            <div class="edu-logo">Edu<span>Forge</span> AI</div>
            <div class="edu-tagline">
                AI-powered teaching material generation · Multi-source RAG Engine
            </div>
        </div>
    </div>"""


def render_step_nav(current_step: int):
    """Render the 4-step navigation bar. current_step: 1, 2, 3, or 4."""
    steps = [
        (1, "Add Sources"),
        (2, "Generate"),
        (3, "Export"),
        (4, "History"),
    ]

    def state(n):
        if n < current_step:
            return "done"
        if n == current_step:
            return "current"
        return "future"

    html = '<div style="display:flex; gap:0.75rem; background:rgba(15,23,42,0.6); border:1px solid rgba(255,255,255,0.08); border-radius:14px; padding:0.9rem 1.4rem; margin-bottom:1.75rem; align-items:center;">'
    for i, (num, name) in enumerate(steps):
        s = state(num)
        icon = "✓" if s == "done" else str(num)
        bg = "#00F5D4" if s == "current" else ("rgba(0, 245, 212, 0.15)" if s == "done" else "rgba(30, 41, 59, 0.5)")
        fg = "#070A11" if s == "current" else ("#00F5D4" if s == "done" else "#94A3B8")
        border = "none" if s == "current" else ("1px solid #00F5D4" if s == "done" else "1px solid rgba(255,255,255,0.1)")

        html += f"""
        <div style="display:flex; align-items:center; gap:0.5rem; flex:1;">
            <div style="width:26px; height:26px; border-radius:50%; background:{bg}; color:{fg}; border:{border}; display:flex; align-items:center; justify-content:center; font-size:0.72rem; font-weight:700; font-family:'Space Grotesk',sans-serif; flex-shrink:0;">{icon}</div>
            <span style="font-size:0.82rem; font-weight:600; color:{'#F8FAFC' if s=='current' else ('#00F5D4' if s=='done' else '#94A3B8')};">{name}</span>
        </div>"""
        if i < len(steps) - 1:
            html += '<div style="width:24px; height:1px; background:rgba(255,255,255,0.1); flex-shrink:0;"></div>'
    html += "</div>"
    return html