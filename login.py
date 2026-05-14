import streamlit as st
import streamlit.components.v1 as components
import psycopg2
import hashlib
import os
from dotenv import load_dotenv
import base64

# HD Dashboard Image Generated for Visual Polish
CHART_IMAGE_B64 = """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"""

load_dotenv()

def get_db():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "smartviz"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost")
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(email, password):
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute(
            "SELECT id, name FROM users WHERE email=%s AND password_hash=%s",
            (email.lower().strip(), hash_password(password))
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user
    except Exception:
        return None

def show_login():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Syne:wght@700;800&display=swap');

    /* ── Reset & Base ── */
    html { scroll-behavior: smooth; }
    [data-testid="stAppViewContainer"] { 
        background-color: #ffffff !important;
        background-image: 
            radial-gradient(circle at 2% 2%, rgba(232,80,10,0.05) 0%, transparent 40%),
            radial-gradient(circle at 98% 98%, rgba(59,130,246,0.05) 0%, transparent 40%),
            radial-gradient(circle, #f1f5f9 1px, transparent 1px) !important;
        background-size: 100% 100%, 100% 100%, 32px 32px !important;
        background-attachment: fixed !important;
    }
    [data-testid="stHeader"], [data-testid="stSidebarCollapsedControl"], [data-testid="stToolbar"] { display:none !important; }
    #MainMenu, footer, header { visibility:hidden !important; }
    .block-container { padding:0 !important; max-width:100% !important; }
    iframe { display:block !important; }

    /* ── Form Inputs ── */
    div[data-testid="stTextInput"] label {
        font-family:'Inter',sans-serif !important; font-size:13px !important; font-weight:600 !important; color:#374151 !important; margin-bottom:8px !important;
    }
    div[data-testid="stTextInput"] input {
        font-family:'Inter',sans-serif !important; font-size:15px !important; font-weight:400 !important;
        color:#111827 !important; -webkit-text-fill-color:#111827 !important;
        background:#ffffff !important; border:1px solid #e5e7eb !important; border-radius:8px !important;
        padding:11px 14px !important; height:46px !important; box-shadow:0 1px 2px rgba(0,0,0,0.05) !important;
        transition:all 0.2s !important; caret-color:#111827 !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color:#9ca3af !important; -webkit-text-fill-color:#9ca3af !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color:#E8500A !important; box-shadow:0 0 0 4px rgba(232,80,10,0.1) !important; outline:none !important;
    }

    /* ── Base Buttons (Primary Orange) ── */
    div[data-testid="stButton"] > button {
        font-family:'Inter',sans-serif !important; font-size:14px !important; font-weight:600 !important;
        height:46px !important; padding:0 24px !important; border-radius:8px !important; border:none !important;
        width:100% !important; cursor:pointer !important; letter-spacing:-0.1px !important;
        transition:all 0.2s !important;
        background:#E8500A !important; color:#ffffff !important; box-shadow:0 4px 12px rgba(232,80,10,0.2) !important;
    }
    div[data-testid="stButton"] > button:hover {
        background:#ff5f15 !important; transform:translateY(-1px) !important; box-shadow:0 6px 16px rgba(232,80,10,0.25) !important;
    }

    /* Nav Sign Up (Column 3) / "Don't have an account" (Column 5) */
    div[data-testid="column"]:nth-child(3) div[data-testid="stButton"] > button,
    div[data-testid="column"]:nth-child(5) div[data-testid="stButton"] > button {
        background:#ffffff !important; color:#374151 !important; border:1px solid #e5e7eb !important; box-shadow:0 1px 2px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="column"]:nth-child(3) div[data-testid="stButton"] > button:hover,
    div[data-testid="column"]:nth-child(5) div[data-testid="stButton"] > button:hover {
        background:#f9fafb !important; border-color:#d1d5db !important; color:#111827 !important; transform:translateY(-1px) !important;
    }

    /* Back home (Column 6) */
    div[data-testid="column"]:nth-child(6) div[data-testid="stButton"] > button {
        background:transparent !important; color:#6b7280 !important; border:none !important; box-shadow:none !important; height:36px !important;
    }
    div[data-testid="column"]:nth-child(6) div[data-testid="stButton"] > button:hover {
        background:#f3f4f6 !important; color:#111827 !important; transform:none !important;
    }

    /* ── Logo Link Style ── */
    .logo-container {
        padding-left: 48px;
        text-decoration: none !important;
        transition: transform 0.2s ease !important;
        display: block;
    }
    .logo-container:hover {
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

    # ── NAV BACKGROUND (Visual only) ──
    st.markdown("""
    <div style="position:absolute; width:100%; height:68px; left:0; border-bottom:1px solid rgba(229,231,235,0.5); background:rgba(255,255,255,0.95); backdrop-filter:blur(10px); z-index:900;"></div>
    """, unsafe_allow_html=True)

    # ── NAV CONTENT ──
    st.markdown('<div style="position:relative; z-index:999; height:68px; display:flex; align-items:center;">', unsafe_allow_html=True)
    nav_logo, nav_spacer, nav_btn = st.columns([3, 4, 1.5])
    
    with nav_logo:
        st.markdown(f"""
        <a href="./" target="_self" class="logo-container">
          <div style="font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:#111827;letter-spacing:-1.2px;line-height:1;">
            Smart<span style="color:#E8500A;">Viz</span>
          </div>
          <div style="font-family:'Inter',sans-serif;font-size:9px;color:#6b7280;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;margin-top:2px;">
            <span style="color:#111827;">Better</span> Buildings. <span style="color:#111827;">Better</span> Places.
          </div>
        </a>
        """, unsafe_allow_html=True)
    with nav_spacer:
        st.markdown("""
        <div style="text-align:right; font-family:'Inter',sans-serif; font-size:14px; color:#6b7280; padding-right:16px;">
            Don't have an account?
        </div>
        """, unsafe_allow_html=True)
    with nav_btn:
        if st.button("Sign up", key="nav_signup"):
            st.session_state.page = "signup"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── MAIN LAYOUT ──
    # Top spacing to center the form vertically
    st.markdown("<div style='height: 8vh;'></div>", unsafe_allow_html=True)
    
    # We use Streamlit native columns for the actual split
    left_padding, left_side, spacer, right_side, right_padding = st.columns([0.5, 1, 0.15, 1, 0.5])
    
    with left_side:
        components.html(f"""
        <!DOCTYPE html><html><head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Syne:wght@700;800&display=swap" rel="stylesheet">
        <style>
          *{{margin:0;padding:0;box-sizing:border-box;}} 
          body{{font-family:'Inter',sans-serif; overflow:hidden;}}
          .brand-card {{
            background: url(data:image/png;base64,{CHART_IMAGE_B64}) center/cover;
            border-radius:24px; padding:56px 44px; color:#ffffff; min-height:520px; 
            position:relative; overflow:hidden; display:flex; flex-direction:column; 
            justify-content:center; box-shadow:0 24px 48px -12px rgba(17,24,39,0.25);
          }}
          .glass-overlay {{
            position:absolute; inset:0; 
            background: rgba(10,11,20,0.65); 
            backdrop-filter: blur(8px) brightness(0.8);
            z-index:1;
          }}
          .content {{ position:relative; z-index:2; }}
        </style>
        </head><body>
        <div class="brand-card">
          <div class="glass-overlay"></div>
          
          <div class="content">
            <div style="font-family:'Syne',sans-serif; font-size:12px; font-weight:700; color:#E8500A; letter-spacing:1px; margin-bottom:16px; text-transform:uppercase;">
              SmartViz Intelligence
            </div>
            <h2 style="font-family:'Syne',sans-serif; font-size:36px; font-weight:800; color:#ffffff; line-height:1.1; letter-spacing:-1.5px; margin-bottom:24px;">
              Empower your building with <span style="color:#E8500A;">data.</span>
            </h2>
            
            <p style="font-family:'Inter',sans-serif; font-size:15px; color:rgba(255,255,255,0.7); line-height:1.6; margin-bottom:40px; max-width:320px;">
              Join top organizations optimizing their space and saving millions.
            </p>
            
            <div style="background:rgba(255,255,255,0.03); backdrop-filter:blur(10px); border:1px solid rgba(255,255,255,0.1); border-radius:16px; padding:28px;">
              <div style="display:flex;flex-direction:column;gap:18px;">
                <div style="display:flex;align-items:center;gap:12px;">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/></svg>
                  <span style="font-size:14px;color:rgba(255,255,255,0.9);font-weight:500;">
                    Complete query history & saved charts</span>
                </div>
                <div style="display:flex;align-items:center;gap:12px;">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#E8500A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2v20"/><path d="M12 12h10"/><path d="M12 12H2"/></svg>
                  <span style="font-size:14px;color:rgba(255,255,255,0.9);font-weight:500;">
                    Live building sensor data — 1M+ readings</span>
                </div>
                <div style="display:flex;align-items:center;gap:12px;">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#E8500A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                  <span style="font-size:14px;color:rgba(255,255,255,0.9);font-weight:500;">
                    Validated charts in under 12 seconds</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        </body></html>
        """, height=520)
        
    with right_side:
        # We need to make the form itself look nicely padded and contained
        st.markdown("""
        <div style="padding-top:32px; padding-bottom:16px; padding-left:16px;">
            <h1 style="font-family:'Syne',sans-serif;font-size:42px;font-weight:800;color:#111827;letter-spacing:-1.5px;margin-bottom:8px;">
                Sign in
            </h1>
            <p style="font-size:16px;color:#6b7280;font-family:'Inter',sans-serif;margin-bottom:32px; font-weight:500;">
                Access your building intelligence.
            </p>
            <div style="width:40px;height:4px;background:#E8500A;border-radius:2px;margin-bottom:16px;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        email    = st.text_input("Email address", placeholder="you@university.ac.uk", key="login_email")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        if st.button("Sign in", key="login_btn"):
            if not email or not password:
                st.error("Please enter your email and password.")
            else:
                user = verify_user(email, password)
                if user:
                    st.session_state.user_id   = user[0]
                    st.session_state.user_name = user[1]
                    st.session_state.logged_in = True
                    st.session_state.page      = "app"
                    st.rerun()
                else:
                    st.error("Incorrect email or password. Please try again.")

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        if st.button("Don't have an account? Sign up", key="go_signup"):
            st.session_state.page = "signup"
            st.rerun()

        if st.button("← Back to home", key="back_home"):
            st.session_state.page = "landing"
            st.rerun()

    # Bottom spacing
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="border-top:1px solid rgba(229,231,235,0.5);padding:32px 48px;background:rgba(255,255,255,0.8); backdrop-filter:blur(10px);
    display:flex;justify-content:space-between;align-items:center; position:fixed; bottom:0; width:100%; z-index:1000;">
      <span style="font-family:'Syne',sans-serif;font-size:18px;font-weight:800;
      color:#111827;letter-spacing:-0.8px;">Smart<span style="color:#E8500A;">Viz</span></span>
      <span style="font-size:13px;color:#6b7280;font-family:'Inter',sans-serif;font-weight:500;">
        Built for Better Buildings &nbsp;·&nbsp; 2026 SmartViz Ltd.
      </span>
    </div>
    """, unsafe_allow_html=True)