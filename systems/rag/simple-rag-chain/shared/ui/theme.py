"""shared.ui — design tokens and Streamlit theme helper.

Usage in any Streamlit app:

    from shared.ui.theme import apply_theme, status_badge

    apply_theme()   # call once, before any st.* calls that render content
"""

import streamlit as st

TOKENS: dict[str, str] = {
    "bg_primary":    "#0A0A0F",
    "bg_surface":    "#12121A",
    "bg_elevated":   "#1A1A26",
    "accent":        "#6C63FF",
    "accent_dim":    "#3D3880",
    "text_primary":  "#F0F0FF",
    "text_secondary":"#8888AA",
    "border":        "#2A2A3A",
    "success":       "#22C55E",
    "error":         "#EF4444",
    "warning":       "#F59E0B",
}

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg-primary:     #0A0A0F;
  --bg-surface:     #12121A;
  --bg-elevated:    #1A1A26;
  --accent:         #6C63FF;
  --accent-dim:     #3D3880;
  --text-primary:   #F0F0FF;
  --text-secondary: #8888AA;
  --border:         #2A2A3A;
  --success:        #22C55E;
  --error:          #EF4444;
  --warning:        #F59E0B;
}

/* ── Base ──────────────────────────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.main,
.block-container {
  background-color: var(--bg-primary) !important;
  color: var(--text-primary) !important;
  font-family: system-ui, sans-serif !important;
}

[data-testid="stSidebar"] {
  background-color: var(--bg-surface) !important;
  border-right: 1px solid var(--border) !important;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Space Grotesk', system-ui, sans-serif !important;
  color: var(--text-primary) !important;
}
h1 { font-size: 40px !important; font-weight: 700 !important; }
h2 { font-size: 28px !important; font-weight: 700 !important; }
h3 { font-size: 20px !important; font-weight: 600 !important; }
p, li { font-size: 16px !important; line-height: 1.6 !important; }

.stButton > button {
  background-color: var(--accent) !important;
  color: var(--text-primary) !important;
  border: none !important;
  border-radius: 6px !important;
  font-family: 'Space Grotesk', system-ui, sans-serif !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  padding: 0.5rem 1.5rem !important;
  transition: background-color 0.15s ease !important;
}
.stButton > button:hover { background-color: var(--accent-dim) !important; }
.stButton > button:disabled { opacity: 0.45 !important; cursor: not-allowed !important; }

.stTextInput > div > div > input,
.stTextArea  > div > div > textarea {
  background-color: var(--bg-elevated) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border) !important;
  border-radius: 6px !important;
  font-size: 14px !important;
}
code, pre, .stCodeBlock {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 13px !important;
  background-color: var(--bg-elevated) !important;
  color: var(--text-primary) !important;
  border-radius: 4px !important;
}
hr { border-color: var(--border) !important; }
#MainMenu, footer, header { visibility: hidden !important; }
</style>
"""

_STATUS_COLORS: dict[str, tuple[str, str]] = {
    "idle":      ("#8888AA", "#1A1A26"),
    "ingesting": ("#F59E0B", "#2A1E0A"),
    "indexing":  ("#6C63FF", "#18162E"),
    "querying":  ("#6C63FF", "#18162E"),
    "error":     ("#EF4444", "#2A0D0D"),
    "success":   ("#22C55E", "#0D2A18"),
}


def apply_theme() -> None:
    """Inject the RoboMarket design system into a Streamlit page."""
    st.markdown(_CSS, unsafe_allow_html=True)


def status_badge(state: str, message: str = "") -> str:
    """Return an HTML inline badge for a pipeline status state."""
    text_color, bg_color = _STATUS_COLORS.get(state, ("#8888AA", "#1A1A26"))
    label = message or state.upper()
    return (
        f'<span style="'
        f'display:inline-block;'
        f'padding:3px 10px;'
        f'border-radius:4px;'
        f'background:{bg_color};'
        f'color:{text_color};'
        f'font-family:\'JetBrains Mono\',monospace;'
        f'font-size:12px;'
        f'font-weight:500;'
        f'border:1px solid {text_color}55;'
        f'letter-spacing:0.04em;'
        f'">{label}</span>'
    )
