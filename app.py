import streamlit as st
import time
from backend.agent import GeminiPlusAgent
from backend.voice_handler import VoiceHandler

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GeminiPlus",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@300;400;500;600&display=swap');

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f;
    color: #e8e8f0;
    font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: #0a0a0f;
}

[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"] { display: none; }
[data-testid="stDecoration"] { display: none; }

/* ── Layout ── */
.main-wrap {
    max-width: 760px;
    margin: 0 auto;
    padding: 48px 24px 120px;
}

/* ── Header ── */
.site-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 4px;
}

.logo-mark {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.18em;
    color: #5b5bff;
    text-transform: uppercase;
    opacity: 0.9;
}

.tagline {
    font-size: 12px;
    color: #44445a;
    font-weight: 300;
    letter-spacing: 0.04em;
    margin-bottom: 40px;
}

/* ── Chat messages ── */
.msg-block {
    margin-bottom: 28px;
}

.msg-role {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.msg-role.user  { color: #5b5bff; }
.msg-role.agent { color: #44445a; }

.msg-text {
    font-size: 14.5px;
    line-height: 1.75;
    color: #c8c8de;
    white-space: pre-wrap;
}

/* ── Status badge ── */
.status-row {
    display: flex;
    gap: 8px;
    margin-top: 10px;
    flex-wrap: wrap;
}

.badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    padding: 3px 8px;
    border-radius: 2px;
    letter-spacing: 0.08em;
}

.badge-ok      { background: #0f2a0f; color: #4ade80; border: 1px solid #166534; }
.badge-warn    { background: #2a1a00; color: #fb923c; border: 1px solid #7c2d12; }
.badge-retry   { background: #1a0a2a; color: #a78bfa; border: 1px solid #4c1d95; }
.badge-voice   { background: #0a1a2a; color: #60a5fa; border: 1px solid #1e3a5f; }
.badge-score   { background: #111118; color: #44445a; border: 1px solid #1e1e2e; }

/* ── Divider ── */
.thread-divider {
    border: none;
    border-top: 1px solid #1a1a2e;
    margin: 32px 0;
}

/* ── Voice transcript box ── */
.transcript-box {
    background: #0e0e1a;
    border: 1px solid #1e1e3a;
    border-left: 3px solid #5b5bff;
    padding: 12px 16px;
    margin: 12px 0 16px;
    border-radius: 0 4px 4px 0;
    font-size: 14px;
    color: #a0a0c0;
    font-style: italic;
}

/* ── Streamlit widget overrides ── */
.stTextInput > div > div > input {
    background: #0e0e1a !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 4px !important;
    color: #e8e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
}

.stTextInput > div > div > input:focus {
    border-color: #5b5bff !important;
    box-shadow: 0 0 0 2px rgba(91,91,255,0.12) !important;
}

.stButton > button {
    background: #5b5bff !important;
    color: #fff !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.1em !important;
    padding: 10px 20px !important;
    text-transform: uppercase !important;
    transition: opacity 0.15s !important;
}

.stButton > button:hover { opacity: 0.85 !important; }

div[data-testid="column"] .stButton > button {
    width: 100%;
}

/* secondary buttons */
div[data-testid="column"]:nth-child(2) .stButton > button,
div[data-testid="column"]:nth-child(3) .stButton > button {
    background: #111118 !important;
    border: 1px solid #1e1e3a !important;
    color: #8080a0 !important;
}

.stSlider { padding: 0; }

/* hide streamlit branding */
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "agent" not in st.session_state:
    st.session_state.agent = GeminiPlusAgent()

if "voice" not in st.session_state:
    st.session_state.voice = None  # lazy-load only when needed

if "history" not in st.session_state:
    # each entry: { role, text, meta }
    st.session_state.history = []

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "recording" not in st.session_state:
    st.session_state.recording = False

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
st.markdown("""
<div class="site-header">
    <span class="logo-mark">✦ GeminiPlus</span>
</div>
<p class="tagline">Gemini · with repetition detection + Whisper voice input</p>
""", unsafe_allow_html=True)

# ── Chat history ──────────────────────────────────────────────────────────────
for i, entry in enumerate(st.session_state.history):
    role_label = "you" if entry["role"] == "user" else "gemini+"
    role_class = "user" if entry["role"] == "user" else "agent"

    st.markdown(f"""
    <div class="msg-block">
        <div class="msg-role {role_class}">{role_label}</div>
        <div class="msg-text">{entry["text"]}</div>
    """, unsafe_allow_html=True)

    # Show metadata badges for agent responses
    if entry["role"] == "agent" and "meta" in entry:
        meta = entry["meta"]
        badges = ""
        if meta.get("voice_input"):
            badges += '<span class="badge badge-voice">voice input</span>'
        if meta.get("repetition_detected"):
            badges += '<span class="badge badge-warn">⚠ loop detected</span>'
            if meta.get("retried"):
                badges += '<span class="badge badge-retry">↺ diversity retry</span>'
        else:
            badges += '<span class="badge badge-ok">✓ no repetition</span>'
        score = meta.get("similarity_score", 0)
        badges += f'<span class="badge badge-score">sim {score:.2f}</span>'
        st.markdown(f'<div class="status-row">{badges}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if i < len(st.session_state.history) - 1:
        st.markdown('<hr class="thread-divider">', unsafe_allow_html=True)

# ── Voice transcript preview ──────────────────────────────────────────────────
if st.session_state.transcript:
    st.markdown(f"""
    <div class="transcript-box">
        🎙 Whisper heard: <em>"{st.session_state.transcript}"</em>
    </div>
    """, unsafe_allow_html=True)

# ── Input controls ────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

text_input = st.text_input(
    label="",
    placeholder="Ask anything...",
    key="text_box",
    label_visibility="collapsed",
)

voice_duration = st.slider(
    "Voice recording duration (seconds)",
    min_value=3, max_value=20, value=8,
    label_visibility="visible"
)

col1, col2, col3 = st.columns([2, 1.2, 1])

with col1:
    send_clicked = st.button("Send →", key="send_btn")

with col2:
    voice_clicked = st.button("🎙 Record voice", key="voice_btn")

with col3:
    reset_clicked = st.button("↺ Reset", key="reset_btn")

# ── Handle: send text ─────────────────────────────────────────────────────────
def submit_message(user_text: str, voice_input: bool = False):
    if not user_text.strip():
        return

    st.session_state.history.append({
        "role": "user",
        "text": user_text,
    })

    with st.spinner("Thinking..."):
        result = st.session_state.agent.chat(user_text)

    st.session_state.history.append({
        "role": "agent",
        "text": result["response"],
        "meta": {
            "repetition_detected": result["repetition_detected"],
            "similarity_score": result["similarity_score"],
            "retried": result["retried"],
            "voice_input": voice_input,
        }
    })

    st.session_state.transcript = ""  # clear after sending


if send_clicked and text_input.strip():
    submit_message(text_input)
    st.rerun()

# ── Handle: voice record ──────────────────────────────────────────────────────
if voice_clicked:
    # Lazy-load VoiceHandler only when first used
    if st.session_state.voice is None:
        with st.spinner("Loading Whisper model..."):
            st.session_state.voice = VoiceHandler(model_size="base")

    with st.spinner(f"Recording for {voice_duration}s... speak now!"):
        transcript = st.session_state.voice.record_and_transcribe(
            duration_seconds=voice_duration
        )

    st.session_state.transcript = transcript
    st.rerun()

# ── Handle: send transcript ───────────────────────────────────────────────────
# If there's a transcript waiting, show a "Send this" button
if st.session_state.transcript:
    if st.button(f'Send: "{st.session_state.transcript[:60]}..."', key="send_transcript"):
        submit_message(st.session_state.transcript, voice_input=True)
        st.rerun()

# ── Handle: reset ─────────────────────────────────────────────────────────────
if reset_clicked:
    st.session_state.agent.reset()
    st.session_state.history = []
    st.session_state.transcript = ""
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
