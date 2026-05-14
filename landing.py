import streamlit as st
import streamlit.components.v1 as components
import base64
import os

def show_landing():
    # ── LOAD ASSETS ───────────────────────────────────────────────────────────
    video_path = os.path.join("assets", "Smart_Building.mov")
    video_base64 = ""
    try:
        with open(video_path, "rb") as f:
            video_base64 = base64.b64encode(f.read()).decode()
    except Exception:
        pass


    # ── GLOBAL STYLES ─────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Syne:wght@700;800&display=swap');

    /* ── Reset & Base ── */
    html { scroll-behavior: smooth; }
    [data-testid="stAppViewContainer"] { background:#ffffff !important; }
    [data-testid="stHeader"], [data-testid="stSidebarCollapsedControl"], [data-testid="stToolbar"] { display:none !important; }
    #MainMenu, footer, header { visibility:hidden !important; }
    .block-container { padding:0 !important; max-width:100% !important; }
    iframe { display:block !important; }

    /* ── Nav Link styles ── */
    .nav-link {
        text-decoration:none !important;
        font-family:'Inter',sans-serif !important;
        font-size:14px !important;
        font-weight:500 !important;
        color:#6b7280 !important;
        padding:8px 16px !important;
        border-radius:18px !important;
        transition:all 0.2s ease !important;
        display:inline-block !important;
    }
    .nav-link:hover {
        background:#f3f4f6 !important;
        color:#111827 !important;
    }

    /* ── Header specific buttons ── */
    /* Book a demo (Primary) */
    div[data-testid="column"]:nth-child(8) div[data-testid="stButton"] > button {
        background:#E8500A !important;
        color:white !important;
        height:38px !important;
        padding:0 20px !important;
        font-weight:700 !important;
        box-shadow:0 4px 12px rgba(232,80,10,0.15) !important;
        transition:0.2s !important;
    }
    div[data-testid="column"]:nth-child(8) div[data-testid="stButton"] > button:hover {
        background:#ff5f15 !important;
        transform:translateY(-1px) !important;
    }

    /* Sign in (Secondary/Clean) */
    div[data-testid="column"]:nth-child(7) div[data-testid="stButton"] > button {
        background:transparent !important;
        color:#4b5563 !important;
        height:38px !important;
        padding:0 16px !important;
        border:1px solid #d1d5db !important;
        font-weight:600 !important;
    }
    div[data-testid="column"]:nth-child(7) div[data-testid="stButton"] > button:hover {
        background:#f9fafb !important;
        border-color:#111827 !important;
        color:#111827 !important;
    }

    /* ── Layout helpers ── */
    div[data-testid="stHorizontalBlock"] { align-items:center !important; gap:0 !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding:0 !important; }

    /* ── ALL buttons: base reset ── */
    div[data-testid="stButton"] > button {
        font-family:'Inter',sans-serif !important;
        font-size:14px !important;
        font-weight:500 !important;
        line-height:1 !important;
        height:44px !important;
        padding:0 24px !important;
        border-radius:6px !important;
        border:none !important;
        cursor:pointer !important;
        transition:background 0.15s ease, box-shadow 0.15s ease, transform 0.1s ease !important;
        width:100% !important;
        white-space:nowrap !important;
        letter-spacing:-0.1px !important;
        /* Primary orange — default */
        background:#E8500A !important;
        color:#ffffff !important;
        box-shadow:0 1px 3px rgba(232,80,10,0.3) !important;
    }
    div[data-testid="stButton"] > button:hover {
        background:#d14509 !important;
        transform:translateY(-1px) !important;
    }

    /* Ghost Nav variant (pill on hover - columns 2,3,4,5) */
    div[data-testid="column"]:nth-child(2) div[data-testid="stButton"] > button,
    div[data-testid="column"]:nth-child(3) div[data-testid="stButton"] > button,
    div[data-testid="column"]:nth-child(4) div[data-testid="stButton"] > button,
    div[data-testid="column"]:nth-child(5) div[data-testid="stButton"] > button {
        background:transparent !important;
        color:#6b7280 !important;
        border:none !important;
        box-shadow:none !important;
        height:36px !important;
        border-radius: 18px !important;
    }
    div[data-testid="column"]:nth-child(2) div[data-testid="stButton"] > button:hover,
    div[data-testid="column"]:nth-child(3) div[data-testid="stButton"] > button:hover,
    div[data-testid="column"]:nth-child(4) div[data-testid="stButton"] > button:hover,
    div[data-testid="column"]:nth-child(5) div[data-testid="stButton"] > button:hover {
        background:#f3f4f6 !important;
        color:#111827 !important;
        transform:none !important;
    }

    /* Fix column padding adjustments */
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

    # ── ANNOUNCEMENT BAR ──
    st.markdown("""
    <div style="background:#111827;color:#fff;text-align:center;padding:8px;font-family:'Inter',sans-serif;font-size:12px;font-weight:500;letter-spacing:0.5px;">
        <span style="color:#fcd34d;margin-right:8px;">Upcoming Event</span>
        How AI is Transforming Building Operations — London, UK
    </div>
    """, unsafe_allow_html=True)

    # ── NAV STRIP ──
    st.markdown("""
    <div style="position: sticky; top: 0; z-index: 9999; background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(229,231,235,0.5);">
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:68px; display:flex; align-items:center; position:relative;">', unsafe_allow_html=True)
    nav_logo, nav_links1, nav_links2, nav_links3, nav_links4, nav_spacer, nav_signin, nav_cta = st.columns([2.5, 0.8, 1, 0.7, 0.9, 1.5, 0.8, 1.4])
    
    with nav_logo:
        st.markdown(f"""
        <a href="./" target="_self" class="logo-container" style="padding-left:48px;">
          <div style="font-family:'Syne',sans-serif;font-size:32px;font-weight:800;color:#111827;letter-spacing:-1.2px;line-height:1;">
            Smart<span style="color:#E8500A;">Viz</span>
          </div>
          <div style="font-family:'Inter',sans-serif;font-size:10px;color:#9ca3af;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-top:2px;">
            <span style="color:#111827;">Better</span> Buildings. <span style="color:#111827;">Better</span> Places.
          </div>
        </a>
        """, unsafe_allow_html=True)
    with nav_links1:
        st.markdown('<a href="#platform" class="nav-link">Platform ▾</a>', unsafe_allow_html=True)
    with nav_links2:
        st.markdown('<a href="#how-it-works" class="nav-link">How it works</a>', unsafe_allow_html=True)
    with nav_links3:
        st.markdown('<a href="#clients" class="nav-link">Clients</a>', unsafe_allow_html=True)
    with nav_links4:
        st.markdown('<a href="/?nav=resources" class="nav-link" target="_self">Resources ▾</a>', unsafe_allow_html=True)
    with nav_spacer:
        st.empty()
    with nav_signin:
        if st.button("Sign in", key="nav_signin"):
            st.session_state.page = "login"
            st.rerun()
    with nav_cta:
        if st.button("Book a demo", key="nav_signup"):
            st.session_state.page = "signup"
            st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

    # ── HERO HTML ──
    components.html(f"""
    <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Syne:wght@700;800&display=swap" rel="stylesheet">
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;}}
    body{{background:#0a0b14;font-family:'Inter',sans-serif;}}
    .hero{{position:relative;width:100%;height:680px;display:flex;align-items:center;overflow:hidden;}}
    .hero-video{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:1;}}
    .hero-overlay{{position:absolute;inset:0;background:linear-gradient(90deg, rgba(10,11,20,0.92) 0%, rgba(10,11,20,0.8) 45%, rgba(10,11,20,0.3) 100%);z-index:2;}}
    .hero-content{{position:relative;z-index:10;padding:0 48px;max-width:700px;color:#fff;}}
    .eyebrow{{color:#E8500A;font-weight:600;letter-spacing:1px;font-size:12px;text-transform:uppercase;margin-bottom:16px;display:block;}}
    h1{{font-family:'Syne',sans-serif;font-size:56px;font-weight:800;line-height:1.05;letter-spacing:-2px;margin-bottom:24px;}}
    h1 span{{color:#E8500A;}}
    p.sub{{font-size:18px;color:rgba(255,255,255,0.7);line-height:1.6;margin-bottom:40px;font-weight:400;}}
    .scroll-down{{position:absolute;bottom:40px;left:48px;animation:bounce 2s infinite;color:rgba(255,255,255,0.5);display:flex;flex-direction:column;align-items:center;gap:8px;font-size:12px;font-weight:500;}}
    @keyframes bounce{{0%,20%,50%,80%,100%{{transform:translateY(0);}}40%{{transform:translateY(-10px);}}60%{{transform:translateY(-5px);}}}}
    </style></head><body>
    <div class="hero">
      <video class="hero-video" autoplay loop muted playsinline>
        <source src="data:video/quicktime;base64,{video_base64}" type="video/quicktime">
        Your browser does not support the video tag.
      </video>
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <span class="eyebrow">SmartViz Platform</span>
        <h1>Ask your building <span>anything.</span></h1>
        <p class="sub">Natural language queries → validated SQL → instant charts. Our 5-agent LLM pipeline turns IoT sensor data into decisions — in seconds, not weeks.</p>
      </div>
      <div class="scroll-down">
        <span>SCROLL TO EXPLORE</span>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline></svg>
      </div>
    </div>
    </body></html>
    """, height=680, scrolling=False)

    # ── HERO CTA BUTTONS STYLES ──
    st.markdown("""
    <style>
    .hero-btn-primary div[data-testid="stButton"] > button {
        height:52px !important; padding:0 32px !important; font-size:16px !important;
        border-radius:8px !important; width:auto !important;
    }
    .hero-btn-ghost div[data-testid="stButton"] > button {
        height:52px !important; padding:0 32px !important; font-size:16px !important;
        background:rgba(255,255,255,0.1) !important; color:#fff !important;
        border:1px solid rgba(255,255,255,0.3) !important; box-shadow:none !important;
        border-radius:8px !important; width:auto !important;
    }
    .hero-btn-ghost div[data-testid="stButton"] > button:hover {
        background:rgba(255,255,255,0.2) !important; border-color:rgba(255,255,255,0.5) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="margin-top:-260px; padding-left:48px; display:flex; gap:16px; position:relative; z-index:9999; height:260px;">', unsafe_allow_html=True)
    col1, col2, _ = st.columns([1.5, 1.5, 7])
    with col1:
        st.markdown('<div class="hero-btn-primary">', unsafe_allow_html=True)
        if st.button("Get started free", key="hero_primary"):
            st.session_state.page = "signup"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="hero-btn-ghost">', unsafe_allow_html=True)
        if st.button("Book a demo", key="hero_secondary"):
            st.session_state.page = "signup"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ── SPACER TO PREVENT OVERLAP ──
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

    # ── CORE CONTENT COMPONENTS ──
    component_styles = """
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Syne:wght@700;800&display=swap" rel="stylesheet">
    <style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{font-family:'Inter',sans-serif;color:#111827;background:#fff;overflow:hidden;}
    h1,h2,h3,h4{font-family:'Syne',sans-serif;letter-spacing:-1px;}
    section{padding:100px 48px; border-bottom:1px solid #e5e7eb; position:relative; overflow:hidden;}
    .bg-gray{background:#f9fafb;}
    
    /* ── Ambient Design System (White) ── */
    
    /* Global Dot Grid Texture */
    .base-layer {
        position: fixed; inset: 0; z-index: -2;
        background-color: #fcfcfd;
        background-image: radial-gradient(#d1d5db 0.8px, transparent 0.8px);
        background-size: 24px 24px;
    }

    /* Ambient Glows (Mesh Gradients) */
    .glow {
        position: absolute; z-index: -1; width: 600px; height: 600px;
        border-radius: 50%; filter: blur(120px); opacity: 0.15; pointer-events: none;
    }
    .glow-orange { background: #E8500A; top: -200px; right: -100px; }
    .glow-blue { background: #3b82f6; bottom: -200px; left: -100px; }
    .glow-purple { background: #8b5cf6; top: 40%; left: 30%; width: 400px; height: 400px; }

    /* Technical Grid Background (Specific Section) */
    .dashboard-grid::before {
        content: ''; position: absolute; inset: 0;
        background-image: linear-gradient(#e5e7eb 1px, transparent 1px), linear-gradient(90deg, #e5e7eb 1px, transparent 1px);
        background-size: 40px 40px; opacity: 0.2; pointer-events: none;
    }

    .stats-grid{display:grid;grid-template-columns:repeat(4,1fr);max-width:1100px;margin:0 auto;text-align:center; position:relative; z-index:1;}
    .stat-box{border-right:1px solid #e5e7eb;padding:24px;}
    .stat-box:last-child{border-right:none;}
    .stat-num{font-size:48px;font-weight:800;color:#E8500A;line-height:1;}
    .stat-label{font-size:14px;color:#6b7280;margin-top:8px;font-weight:500;}
    
    .logos-wrap{overflow:hidden; background:rgba(255,255,255,0.7); backdrop-filter:blur(10px); padding:48px 0; border-bottom:1px solid #e5e7eb; display:flex; align-items:center; position:relative; z-index:1;}
    .logo-label{
        font-size:12px; text-transform:uppercase; letter-spacing:1.5px; font-weight:700; color:#9ca3af; 
        white-space:nowrap; padding:0 48px; position:sticky; left:0; z-index:100; 
        background:white; display:flex; align-items:center;
    }
    .logo-label::after {
        content:''; position:absolute; left:100%; top:0; bottom:0; width:80px;
        background:linear-gradient(90deg, white 0%, transparent 100%); pointer-events:none;
    }
    .logo-track{display:flex; gap:64px; animation:scroll 35s linear infinite; padding-left:24px;}
    @keyframes scroll{0%{transform:translateX(0);}100%{transform:translateX(-50%);}}
    .logo-item{font-weight:700;font-size:20px;color:#9ca3af;white-space:nowrap;display:flex;align-items:center;}
    
    .platform-container{max-width:1200px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:center; position:relative; z-index:1;}
    h2{font-size:48px;margin-bottom:24px;line-height:1.1;}
    p{font-size:18px;color:#4b5563;line-height:1.6;margin-bottom:24px;}
    .bullet-list{list-style:none;margin-bottom:32px;}
    .bullet-list li{display:flex;align-items:flex-start;gap:12px;margin-bottom:16px;font-size:16px;color:#374151;}
    .bullet-list li::before{content:'✓';color:#E8500A;font-weight:bold;}
    
    .glass-card {
        background: rgba(255,255,255,0.7);
        border: 1px solid #e5e7eb;
        border-radius: 20px;
        padding: 32px;
        backdrop-filter: blur(12px);
        transition: transform 0.3s ease, background 0.3s ease;
    }
    .glass-card:hover { transform: translateY(-5px); background: #fff; }

    .tabs{display:flex;gap:8px;background:rgba(0,0,0,0.05);padding:4px;border-radius:8px;margin-bottom:32px;width:fit-content;}
    .tab{padding:8px 16px;font-size:14px;font-weight:600;color:#6b7280;cursor:pointer;border-radius:6px;transition:all 0.2s; border:none; background:transparent;}
    .tab.active{background:#fff;color:#111827;box-shadow:0 1px 3px rgba(0,0,0,0.1);}
    
    /* ── Dashboard Interactive Styles (Escaped for f-strings) ── */
    .dashboard-mockup {
        background: #0a0b14; border-radius: 20px; padding: 24px;
        box-shadow: 0 40px 80px -20px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.1);
        height: 480px; position: relative; overflow: hidden;
    }
    .db-view { display: none; height: 100%; animation: fadeIn 0.4s ease; }
    .db-view.active { display: block; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    .db-header { display: flex; justify-content: space-between; margin-bottom: 24px; }
    .db-tag { background: rgba(232,80,10,0.2); color: #E8500A; padding: 4px 10px; border-radius: 4px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
    .db-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; height: calc(100% - 60px); }
    .db-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 16px; position: relative; }
    .db-chart { width: 100%; height: 140px; background: linear-gradient(180deg, rgba(232,80,10,0.1) 0%, transparent 100%); margin-top: 12px; border-radius: 4px; position: relative; }
    .db-stat { font-size: 24px; font-weight: 800; color: #fff; margin: 8px 0; }
    .db-label { font-size: 11px; color: #6b7280; letter-spacing: 0.5px; text-transform: uppercase; }
    
    .terminal { display:none; }
    
    .pipeline-flow { display: flex; flex-direction: column; gap: 12px; position:relative; margin-top:8px; }
    .pipeline-line { position: absolute; left: 15px; top: 16px; bottom: 16px; width: 2px; background: rgba(255,255,255,0.08); z-index: 1; }
    .pipeline-step { display: flex; align-items: flex-start; gap: 16px; position: relative; z-index: 2; opacity: 0; animation: stepFadeIn 0.5s ease forwards; }
    @keyframes stepFadeIn { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }

    .step-node { width: 32px; height: 32px; border-radius: 50%; background: #0a0b14; border: 2px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: center; font-size: 12px; color: #6b7280; z-index: 2; flex-shrink: 0; box-shadow: 0 0 0 4px #0a0b14; }
    .step-node.active { border-color: #E8500A; color: #E8500A; background: rgba(232,80,10,0.1); box-shadow: 0 0 0 4px #0a0b14, 0 0 12px rgba(232,80,10,0.4); }
    .step-node.done { border-color: #10b981; color: #10b981; background: rgba(16,185,129,0.1); box-shadow: 0 0 0 4px #0a0b14; }

    .step-card { flex: 1; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 10px 14px; border-radius: 8px; display: flex; flex-direction: column; gap: 4px; }
    .st-head { display: flex; justify-content: space-between; align-items: center; }
    .st-title { font-size: 12px; font-weight: 700; color: #fff; letter-spacing: 0.5px; }
    .st-status { font-size: 9px; font-weight: 700; text-transform: uppercase; padding: 2px 6px; border-radius: 4px; }
    .st-status.ok { background: rgba(16,185,129,0.15); color: #10b981; }
    .st-status.proc { background: rgba(232,80,10,0.15); color: #E8500A; animation: pulse 2s infinite; }
    .st-desc { font-size: 11px; color: #9ca3af; }

    @keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }

    .bar-chart { display: flex; align-items: flex-end; gap: 16px; height: 120px; margin-top: 16px; padding-bottom: 4px; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .bar { width: 100%; border-radius: 4px 4px 0 0; position: relative; }
    .bar.actual { background: #374151; }
    .bar.optimized { background: #E8500A; }

    .doughnut {
        width: 120px; height: 120px; border-radius: 50%;
        background: conic-gradient(#E8500A 0% 45%, #3b82f6 45% 75%, #8b5cf6 75% 100%);
        position: relative; margin: 0 auto;
    }
    .doughnut::after { content: ''; position: absolute; inset: 25%; background: #0a0b14; border-radius: 50%; }

    .section-header{text-align:center;margin-bottom:64px;}
    .hiw-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:32px;max-width:1200px;margin:0 auto;}
    .step-num{font-size:12px;font-weight:700;color:#E8500A;margin-bottom:16px;}
    .hiw-icon{font-size:32px;margin-bottom:20px;}
    
    .aud-grid{display:grid;grid-template-columns:1fr 1fr;gap:32px;max-width:1100px;margin:0 auto;}
    .tag{display:inline-block;padding:4px 12px;background:rgba(232,80,10,0.1);color:#E8500A;border-radius:100px;font-size:12px;font-weight:700;margin-bottom:16px;text-transform:uppercase;}
    
    .diff-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;max-width:1100px;margin:0 auto;}
    .diff-card{text-align:center;padding:32px;border-radius:16px;background:#f9fafb;border:1px solid #e5e7eb;}
    .diff-num{font-size:36px;font-weight:800;color:#111827;margin-bottom:8px;}
    .diff-text{font-size:14px;color:#6b7280;}

    .test-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:32px;max-width:1200px;margin:0 auto;}
    .test-card{background:white;padding:32px;border-radius:20px;border:1px solid #e5e7eb;box-shadow:0 10px 30px -10px rgba(0,0,0,0.05);}
    .quote{font-size:16px;color:#4b5563;font-style:italic;line-height:1.6;margin-bottom:24px;}
    .author{font-weight:700;color:#111827;}
    .role{font-size:12px;color:#6b7280;}

    .cta-banner{background:linear-gradient(135deg,#E8500A 0%,#111827 100%);padding:80px;border-radius:32px;display:flex;align-items:center;gap:64px;position:relative;overflow:hidden;}
    .cta-glow{position:absolute;top:-50%;right:-20%;width:400px;height:400px;background:#ff7e33;filter:blur(100px);opacity:0.3;}

    footer{padding:80px 48px;background:#f9fafb;border-top:1px solid #e5e7eb;}
    .foot-grid{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:64px;max-width:1200px;margin:0 auto;}
    .foot-brand{font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:#111827;}
    .foot-brand span{color:#E8500A;}
    .foot-col h4{font-size:14px;text-transform:uppercase;letter-spacing:1px;margin-bottom:24px;}
    .foot-col ul{list-style:none;}
    .foot-col ul li{margin-bottom:12px;}
    .foot-col ul li a{text-decoration:none;color:#6b7280;font-size:14px;transition:0.2s;}
    .foot-col ul li a:hover{color:#E8500A;}
    .foot-bottom{border-top:1px solid #e5e7eb;padding-top:32px;margin-top:64px;text-align:center;font-size:12px;color:#6b7280;}
    </style>

    <script>
    function showView(viewId, btn) {
        document.querySelectorAll('.db-view').forEach(v => v.classList.remove('active'));
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.getElementById(viewId).classList.add('active');
        btn.classList.add('active');
    }
    </script>
    """

    # 1. CLIENTS SECTION
    st.markdown('<div id="clients" style="position:relative; top:-100px;"></div>', unsafe_allow_html=True)
    components.html(f"""
    <!DOCTYPE html><html><head>{component_styles}</head><body>
    <div class="base-layer"></div>
    <section style="padding:48px;">
        <div class="glow glow-orange" style="opacity:0.08;"></div>
        <div class="stats-grid">
            <div class="stat-box"><div class="stat-num">$40M+</div><div class="stat-label">Annual property savings</div></div>
            <div class="stat-box"><div class="stat-num">£5.1M</div><div class="stat-label">Space optimization savings</div></div>
            <div class="stat-box"><div class="stat-num">15%</div><div class="stat-label">Reduction in facilities costs</div></div>
            <div class="stat-box"><div class="stat-num">£3M+</div><div class="stat-label">Consolidated space savings</div></div>
        </div>
    </section>
    <div class="logos-wrap">
        <span class="logo-label">Trusted by</span>
        <div class="logo-track">
            <span class="logo-item" style="color:#000;">Vodafone</span>
            <span class="logo-item" style="color:#A1002A;">Cardiff Metropolitan University</span>
            <span class="logo-item" style="color:#005A9C;">NHS</span>
            <span class="logo-item" style="color:#000;">University of Southampton</span>
            <span class="logo-item" style="color:#004a80;">Barnsley Council</span>
            <span class="logo-item" style="color:#000;">Royal United Hospital Bath</span>
            <span class="logo-item" style="color:#000;">Vodafone</span>
            <span class="logo-item" style="color:#A1002A;">Cardiff Metropolitan University</span>
            <span class="logo-item" style="color:#005A9C;">NHS</span>
            <span class="logo-item" style="color:#000;">University of Southampton</span>
            <span class="logo-item" style="color:#004a80;">Barnsley Council</span>
        </div>
    </div>
    </body></html>
    """, height=450)

    # 2. PLATFORM SECTION
    st.markdown('<div id="platform" style="position:relative; top:-100px;"></div>', unsafe_allow_html=True)
    components.html(f"""
    <!DOCTYPE html><html><head>{component_styles}</head><body>
    <div class="base-layer"></div>
    <section class="dashboard-grid">
        <div class="glow glow-orange" style="top:20%; right:-10%; opacity:0.1;"></div>
        <div class="glow glow-blue" style="top:60%; left:-10%; opacity:0.08;"></div>
        <div class="platform-container">
            <div>
                <div class="tabs">
                    <button class="tab active" onclick="showView('v-analytics', this)">Advanced Analytics</button>
                    <button class="tab" onclick="showView('v-pipeline', this)">5-agent Pipeline</button>
                    <button class="tab" onclick="showView('v-insights', this)">Visual Insights</button>
                </div>
                <h2>Stop guessing. Start knowing.</h2>
                <p>SmartViz connects directly to your building's IoT fabric. Ask natural language questions and get validated datasets and visualisations returned instantly.</p>
                <ul class="bullet-list">
                    <li>Agent 1 Planner & Agent 2 RAG (pgvector)</li>
                    <li>Agent 3 SQL Generator & Agent 4 Validator</li>
                    <li>Agent 5 Graph Builder for immediate insights</li>
                </ul>
                <a href="#" style="color:#E8500A;text-decoration:none;font-weight:600;font-size:16px;">Learn more →</a>
            </div>
            <div class="dashboard-mockup">
                <!-- VIEW 1: ANALYTICS -->
                <div id="v-analytics" class="db-view active">
                    <div class="db-header">
                        <div class="db-tag">LIVE TELEMETRY</div>
                        <div class="db-pulse"></div>
                    </div>
                    <div class="db-grid">
                        <div style="display:grid; gap:16px;">
                            <div class="db-card">
                                <div class="db-label">ENERGY INTENSITY (kWh/m2)</div>
                                <div class="db-stat">42.8 <span style="font-size:12px;color:#10b981;">↓ 12%</span></div>
                                <div class="db-chart">
                                    <svg width="100%" height="100%" viewBox="0 0 400 100" preserveAspectRatio="none">
                                        <path d="M0,80 Q50,20 100,50 T200,30 T300,70 T400,20" fill="none" stroke="#E8500A" stroke-width="3" />
                                    </svg>
                                </div>
                            </div>
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                                <div class="db-card">
                                    <div class="db-label">OCCUPANCY</div>
                                    <div class="db-stat">74%</div>
                                </div>
                                <div class="db-card">
                                    <div class="db-label">AIR QUALITY</div>
                                    <div class="db-stat">EXC</div>
                                </div>
                            </div>
                        </div>
                        <div class="db-card" style="display:flex; flex-direction:column; justify-content:space-between; text-align:center;">
                            <div class="db-label">BUILDING HEALTH</div>
                            <div style="height:100%; display:flex; align-items:center; justify-content:center;">
                                 <div style="width:80px; height:80px; border-radius:50%; border:8px solid rgba(232,80,10,0.1); border-top-color:#E8500A; animation: spin 2s linear infinite;"></div>
                            </div>
                            <div class="db-label">98.2% UPTIME</div>
                        </div>
                    </div>
                </div>

                <!-- VIEW 2: PIPELINE -->
                <div id="v-pipeline" class="db-view">
                    <div class="db-header"><div class="db-tag">PIPELINE EXECUTION</div></div>
                    
                    <div class="pipeline-flow">
                        <div class="pipeline-line"></div>
                        
                        <div class="pipeline-step" style="animation-delay: 0.1s;">
                            <div class="step-node done">✓</div>
                            <div class="step-card">
                                <div class="st-head"><span class="st-title">Agent 1: Planner</span><span class="st-status ok">SUCCESS</span></div>
                                <div class="st-desc">Deconstructing natural language query</div>
                            </div>
                        </div>

                        <div class="pipeline-step" style="animation-delay: 0.3s;">
                            <div class="step-node done">✓</div>
                            <div class="step-card">
                                <div class="st-head"><span class="st-title">Agent 2: RAG Retrieval</span><span class="st-status ok">SUCCESS</span></div>
                                <div class="st-desc">Searched pgvector store. Found 42 relevant docs.</div>
                            </div>
                        </div>

                        <div class="pipeline-step" style="animation-delay: 0.5s;">
                            <div class="step-node done">✓</div>
                            <div class="step-card">
                                <div class="st-head"><span class="st-title">Agent 3: SQL Gen</span><span class="st-status ok">SUCCESS</span></div>
                                <div class="st-desc">Synthesized validated PostgreSQL query.</div>
                            </div>
                        </div>

                        <div class="pipeline-step" style="animation-delay: 0.7s;">
                            <div class="step-node done">✓</div>
                            <div class="step-card">
                                <div class="st-head"><span class="st-title">Agent 4: Validator</span><span class="st-status ok">SUCCESS</span></div>
                                <div class="st-desc">Executed dry-run schema test. No hallucinations.</div>
                            </div>
                        </div>

                        <div class="pipeline-step" style="animation-delay: 0.9s;">
                            <div class="step-node active">
                                <span style="animation: pulse 1s infinite; font-size:16px;">●</span>
                            </div>
                            <div class="step-card" style="border-color:rgba(232,80,10,0.3);">
                                <div class="st-head"><span class="st-title" style="color:#E8500A;">Agent 5: Graph Builder</span><span class="st-status proc">PROCESSING</span></div>
                                <div class="st-desc">Rendering multi-series interactive SVG chart...</div>
                            </div>
                        </div>
                        
                    </div>
                </div>

                <!-- VIEW 3: INSIGHTS -->
                <div id="v-insights" class="db-view">
                    <div class="db-header">
                        <div class="db-tag">GENERATED INSIGHTS</div>
                        <div style="color:#10b981; font-size:10px; font-weight:700;">ACCURACY: 99.8%</div>
                    </div>
                    <div class="db-grid" style="grid-template-columns: 1fr 1fr;">
                        <div class="db-card">
                            <div class="db-label">Space Optimization Result</div>
                            <div class="bar-chart">
                                <div style="flex:1; display:flex; flex-direction:column; justify-content:flex-end; align-items:center; gap:8px; height: 100%;">
                                    <div class="bar actual" style="height:80%;"></div>
                                </div>
                                <div style="flex:1; display:flex; flex-direction:column; justify-content:flex-end; align-items:center; gap:8px; height: 100%;">
                                    <div class="bar optimized" style="height:45%;"></div>
                                </div>
                            </div>
                            <p style="font-size:11px; color:#10b981; margin-top:12px; font-weight:700;">Potential Savings: £1.2M</p>
                        </div>
                        <div class="db-card" style="text-align:center;">
                            <div class="db-label" style="margin-bottom:16px;">Energy Composition</div>
                            <div class="doughnut"></div>
                            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-top:16px; font-size:9px;">
                                <div style="display:flex; align-items:center; gap:4px; color:#E8500A;">● HVAC</div>
                                <div style="display:flex; align-items:center; gap:4px; color:#3b82f6;">● Lighting</div>
                                <div style="display:flex; align-items:center; gap:4px; color:#8b5cf6;">● Data</div>
                                <div style="display:flex; align-items:center; gap:4px; color:#fff;">● Other</div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </section>
    <style>
    @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
    </style>
    </body></html>
    """, height=650)

    # 3. HOW IT WORKS SECTION
    st.markdown('<div id="how-it-works" style="position:relative; top:-100px;"></div>', unsafe_allow_html=True)
    components.html("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Syne:wght@700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{
    font-family:'Inter',sans-serif;
    background-color:#fff;
    background-image: 
        radial-gradient(circle at 2% 2%, rgba(232,80,10,0.05) 0%, transparent 40%),
        radial-gradient(circle at 98% 98%, rgba(59,130,246,0.05) 0%, transparent 40%),
        radial-gradient(circle, #f1f5f9 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 32px 32px;
    background-attachment: fixed;
    -webkit-font-smoothing:antialiased;
}
.wrap{padding:80px 48px 64px; position:relative; z-index:1;}
.header{max-width:640px;margin-bottom:64px;}
.eyebrow{font-size:11px;font-weight:600;letter-spacing:2px;color:#E8500A;text-transform:uppercase;margin-bottom:10px;}
.title{font-family:'Syne',sans-serif;font-size:40px;font-weight:800;letter-spacing:-1px;color:#111827;line-height:1.1;margin-bottom:14px;}
.subtitle{font-size:16px;color:#6b7280;line-height:1.75;}
.section{display:grid;grid-template-columns:1fr 1fr;gap:72px;align-items:center;margin-bottom:72px;padding-bottom:72px;border-bottom:1px solid #f3f4f6;}
.section:last-of-type{border-bottom:none;margin-bottom:0;padding-bottom:0;}
.section.flip .text{order:2;}
.section.flip .visual{order:1;}
.step-num{font-size:11px;font-weight:700;color:#E8500A;letter-spacing:2px;text-transform:uppercase;margin-bottom:14px;}
.step-title{font-family:'Syne',sans-serif;font-size:28px;font-weight:800;letter-spacing:-0.5px;color:#111827;line-height:1.15;margin-bottom:14px;}
.step-body{font-size:15px;color:#374151;line-height:1.8;margin-bottom:20px;}
.step-result{background:#f9fafb;border-left:3px solid #E8500A;padding:14px 18px;border-radius:0 8px 8px 0;}
.step-result p{font-size:14px;color:#374151;line-height:1.65;}
.step-result p b{color:#111827;}
.visual{background:rgba(255,255,255,0.8); backdrop-filter:blur(8px); border:1px solid rgba(229,231,235,0.5); border-radius:16px; padding:28px; box-shadow:0 10px 30px -10px rgba(0,0,0,0.04);}
.v-label{font-size:10px;font-weight:600;color:#9ca3af;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:16px;}
.building-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;}
.room-card{background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:12px;text-align:center;transition:all 0.2s;cursor:default;}
.room-card:hover{border-color:#E8500A;transform:translateY(-2px);}
.room-name{font-size:11px;font-weight:600;color:#374151;margin-bottom:8px;}
.room-metrics{display:flex;flex-direction:column;gap:4px;}
.metric-row{display:flex;justify-content:space-between;align-items:center;}
.metric-key{font-size:10px;color:#9ca3af;}
.metric-val{font-size:11px;font-weight:600;}
.high{color:#dc2626;}
.good{color:#16a34a;}
.mid{color:#d97706;}
.room-dot{width:8px;height:8px;border-radius:50%;margin:0 auto 8px;}
.dot-red{background:#fecaca;border:2px solid #dc2626;}
.dot-amber{background:#fef3c7;border:2px solid #d97706;}
.dot-green{background:#dcfce7;border:2px solid #16a34a;}
.query-box{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px 18px;margin-bottom:12px;}
.query-label{font-size:10px;font-weight:600;color:#9ca3af;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;}
.query-text{font-size:14px;color:#111827;font-weight:500;line-height:1.5;}
.query-cursor{display:inline-block;width:2px;height:14px;background:#E8500A;margin-left:2px;vertical-align:middle;animation:blink 1s step-end infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:0;}}
.arrow-down{text-align:center;padding:6px 0;color:#d1d5db;font-size:18px;}
.answer-box{background:#fff;border:1.5px solid #E8500A;border-radius:10px;padding:16px 18px;}
.answer-label{font-size:10px;font-weight:600;color:#E8500A;letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;}
.chart-bars{display:flex;align-items:flex-end;gap:8px;height:60px;}
.bar{flex:1;border-radius:3px 3px 0 0;background:#e5e7eb;}
.bar-active{background:#E8500A;}
.bar-labels{display:flex;gap:8px;margin-top:6px;}
.bar-lbl{flex:1;font-size:9px;color:#9ca3af;text-align:center;}
.results-grid{display:flex;flex-direction:column;gap:10px;}
.result-row{background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:14px 16px;display:flex;align-items:center;gap:14px;transition:border-color 0.2s;cursor:default;}
.result-row:hover{border-color:#E8500A;}
.result-icon{width:36px;height:36px;border-radius:8px;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.ri-o{background:#fff3ee;border:1px solid rgba(232,80,10,0.15);}
.ri-g{background:#f0fdf4;border:1px solid rgba(22,163,74,0.15);}
.ri-b{background:#eff6ff;border:1px solid rgba(29,78,216,0.15);}
.result-text{flex:1;}
.result-title{font-size:13px;font-weight:600;color:#111827;margin-bottom:2px;}
.result-sub{font-size:11px;color:#9ca3af;}
.result-badge{font-size:11px;font-weight:600;padding:4px 10px;border-radius:20px;flex-shrink:0;}
.badge-o{background:#fff3ee;color:#c2410c;}
.badge-g{background:#f0fdf4;color:#15803d;}
.results-strip{background:linear-gradient(135deg,#111827,#1e1b4b);border-radius:16px;padding:40px 48px;display:grid;grid-template-columns:1fr 1px 1fr 1px 1fr;gap:32px;margin-top:72px;align-items:center;}
.strip-item{text-align:center;}
.strip-num{font-family:'Syne',sans-serif;font-size:40px;font-weight:800;color:#E8500A;letter-spacing:-1.5px;line-height:1;margin-bottom:8px;}
.strip-label{font-size:13px;color:rgba(255,255,255,0.45);line-height:1.6;}
.strip-div{background:rgba(255,255,255,0.08);height:60px;}
</style>
</head>
<body>
<div class="wrap">

  <div class="header">
    <div class="eyebrow">How SmartViz works</div>
    <div class="title">Three simple steps to a smarter building.</div>
    <p class="subtitle">No technical knowledge required. Just ask your building a question — and get a clear answer in seconds.</p>
  </div>

  <!-- Step 1 -->
  <div class="section">
    <div class="text">
      <div class="step-num">Step 01</div>
      <div class="step-title">Your building is already collecting data. We make sense of it.</div>
      <p class="step-body">Every room in your building has sensors quietly measuring temperature, air quality, how many people are inside, and how much energy is being used. SmartViz connects to all of it — instantly.</p>
      <div class="step-result">
        <p>No new hardware needed. No lengthy setup. <b>We connect to your existing sensors and start reading data the same day.</b></p>
      </div>
    </div>
    <div class="visual">
      <div class="v-label">Live sensor readings — PES Building</div>
      <div class="building-grid">
        <div class="room-card"><div class="room-dot dot-red"></div><div class="room-name">Boardroom</div><div class="room-metrics"><div class="metric-row"><span class="metric-key">CO2</span><span class="metric-val high">1,134 ppm</span></div><div class="metric-row"><span class="metric-key">Occupancy</span><span class="metric-val high">82%</span></div></div></div>
        <div class="room-card"><div class="room-dot dot-green"></div><div class="room-name">Seminar 5</div><div class="room-metrics"><div class="metric-row"><span class="metric-key">CO2</span><span class="metric-val good">480 ppm</span></div><div class="metric-row"><span class="metric-key">Occupancy</span><span class="metric-val good">12%</span></div></div></div>
        <div class="room-card"><div class="room-dot dot-amber"></div><div class="room-name">Open Plan</div><div class="room-metrics"><div class="metric-row"><span class="metric-key">CO2</span><span class="metric-val mid">748 ppm</span></div><div class="metric-row"><span class="metric-key">Occupancy</span><span class="metric-val mid">54%</span></div></div></div>
        <div class="room-card"><div class="room-dot dot-green"></div><div class="room-name">Meeting A</div><div class="room-metrics"><div class="metric-row"><span class="metric-key">CO2</span><span class="metric-val good">412 ppm</span></div><div class="metric-row"><span class="metric-key">Occupancy</span><span class="metric-val good">0%</span></div></div></div>
        <div class="room-card"><div class="room-dot dot-red"></div><div class="room-name">Founders</div><div class="room-metrics"><div class="metric-row"><span class="metric-key">CO2</span><span class="metric-val high">1,100 ppm</span></div><div class="metric-row"><span class="metric-key">Occupancy</span><span class="metric-val high">76%</span></div></div></div>
        <div class="room-card"><div class="room-dot dot-amber"></div><div class="room-name">Breakout</div><div class="room-metrics"><div class="metric-row"><span class="metric-key">CO2</span><span class="metric-val mid">690 ppm</span></div><div class="metric-row"><span class="metric-key">Occupancy</span><span class="metric-val mid">38%</span></div></div></div>
      </div>
    </div>
  </div>

  <!-- Step 2 -->
  <div class="section flip">
    <div class="text">
      <div class="step-num">Step 02</div>
      <div class="step-title">Ask any question in plain English. No spreadsheets, no IT team.</div>
      <p class="step-body">Just type your question the same way you'd ask a colleague. SmartViz understands what you're asking, searches through all your building data, and prepares a precise answer — in under 12 seconds.</p>
      <div class="step-result">
        <p>"Which meeting rooms are being booked but sitting empty?" <b>SmartViz finds the answer across every room, every day, in seconds.</b></p>
      </div>
    </div>
    <div class="visual">
      <div class="v-label">Plain-English query — instant result</div>
      <div class="query-box">
        <div class="query-label">You ask</div>
        <div class="query-text">Which rooms have the highest CO2 levels this week?<span class="query-cursor"></span></div>
      </div>
      <div class="arrow-down">↓</div>
      <div class="answer-box">
        <div class="answer-label">SmartViz answers</div>
        <div class="chart-bars">
          <div class="bar bar-active" style="height:100%;"></div>
          <div class="bar bar-active" style="height:92%;"></div>
          <div class="bar" style="height:65%;"></div>
          <div class="bar" style="height:58%;"></div>
          <div class="bar" style="height:50%;"></div>
        </div>
        <div class="bar-labels">
          <div class="bar-lbl">Boardroom</div>
          <div class="bar-lbl">Founders</div>
          <div class="bar-lbl">Seminar 22</div>
          <div class="bar-lbl">Open Plan</div>
          <div class="bar-lbl">Breakout</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Step 3 -->
  <div class="section">
    <div class="text">
      <div class="step-num">Step 03</div>
      <div class="step-title">Get clear answers that drive real decisions.</div>
      <p class="step-body">SmartViz turns your data into charts, reports, and recommendations you can act on immediately. Share with your team, export for a board meeting, or set up alerts so you never miss a problem.</p>
      <div class="step-result">
        <p>Vodafone used SmartViz to identify that <b>30% of their meeting rooms were consistently underused</b> — saving millions per year.</p>
      </div>
    </div>
    <div class="visual">
      <div class="v-label">Actionable outcomes</div>
      <div class="results-grid">
        <div class="result-row">
          <div class="result-icon ri-o"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#E8500A" stroke-width="2" stroke-linecap="round"><path d="M18 20V10M12 20V4M6 20v-6"/></svg></div>
          <div class="result-text"><div class="result-title">Instant charts & visualisations</div><div class="result-sub">Bar charts, heatmaps, trends — auto-generated</div></div>
          <span class="result-badge badge-o">&lt; 12s</span>
        </div>
        <div class="result-row">
          <div class="result-icon ri-g"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg></div>
          <div class="result-text"><div class="result-title">Space-saving recommendations</div><div class="result-sub">Identify rooms to consolidate or repurpose</div></div>
          <span class="result-badge badge-g">Save costs</span>
        </div>
        <div class="result-row">
          <div class="result-icon ri-b"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1d4ed8" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div>
          <div class="result-text"><div class="result-title">Exportable reports</div><div class="result-sub">Download charts for board presentations</div></div>
          <span class="result-badge badge-o">PNG export</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Results strip -->
  <div class="results-strip">
    <div class="strip-item">
      <div class="strip-num">£3m</div>
      <div class="strip-label">Saved by Royal United Hospital Bath by consolidating underused spaces</div>
    </div>
    <div class="strip-div"></div>
    <div class="strip-item">
      <div class="strip-num">30%</div>
      <div class="strip-label">Reduction in meeting room waste identified for Vodafone</div>
    </div>
    <div class="strip-div"></div>
    <div class="strip-item">
      <div class="strip-num">&lt;12s</div>
      <div class="strip-label">From typing your question to seeing a validated chart on screen</div>
    </div>
  </div>
</div>
</body>
</html>
""", height=1950)

    # 4. AUDIENCE, DIFF & FOOTER SECTION
    components.html(f"""
    <!DOCTYPE html><html><head>{component_styles}</head><body>
    <div class="base-layer"></div>
    <section>
        <div class="glow glow-orange" style="top:0; left:10%; opacity:0.08;"></div>
        <div class="aud-grid">
            <div class="glass-card aud-card">
                <span class="tag">Facilities</span>
                <h3>Estates & FM Teams</h3>
                <p>Stop waiting weeks for reports. Get instant answers about building performance and optimise your portfolio proactively.</p>
                <ul class="bullet-list" style="margin-top:24px;">
                    <li>Identify underutilised spaces</li>
                    <li>Track energy anomalies</li>
                    <li>Validate vendor SLAs</li>
                </ul>
            </div>
            <div class="glass-card aud-card accent">
                <span class="tag">Technology</span>
                <h3>IT & Data Teams</h3>
                <p>A robust, secure architecture that handles the complexities of IoT data structure while enforcing strict access controls.</p>
                <ul class="bullet-list" style="margin-top:24px;">
                    <li>Zero-hallucination semantic layer</li>
                    <li>SHA-256 Auth & pgvector RAG</li>
                    <li>Custom graph generation</li>
                </ul>
            </div>
        </div>
    </section>
    
    <section>
        <div class="diff-grid">
            <div class="glow glow-blue" style="top:20%; left:-10%; opacity:0.05;"></div>
            <div class="diff-card">
                <div class="diff-num">$40M</div>
                <div class="diff-text">Annual property savings identified</div>
            </div>
            <div class="diff-card">
                <div class="diff-num"><12s</div>
                <div class="diff-text">From typed query to chart</div>
            </div>
            <div class="diff-card">
                <div class="diff-num">15%</div>
                <div class="diff-text">Avg reduction in facilities costs</div>
            </div>
            <div class="diff-card">
                <div class="diff-num">£5.1M</div>
                <div class="diff-text">Space optimization savings identified</div>
            </div>
        </div>
    </section>

    <section>
        <div class="glow glow-orange" style="bottom:-10%; right:20%; opacity:0.05;"></div>
        <div class="section-header">
            <h2>Trusted by industry leaders</h2>
        </div>
        <div class="test-grid">
            <div class="test-card">
                <div class="stars">★★★★★</div>
                <p class="quote">"SmartViz identified £40m in potential savings across our portfolio in the first quarter alone. Incredible clarity."</p>
                <div class="divider"></div>
                <div class="author">Head of Estates</div>
                <div class="role">Vodafone</div>
            </div>
            <div class="test-card">
                <div class="stars">★★★★★</div>
                <p class="quote">"We bypassed the complex dashboards. Now my team just asks the system questions, saving £3m immediately."</p>
                <div class="divider"></div>
                <div class="author">Operations Director</div>
                <div class="role">Royal United Hospital Bath</div>
            </div>
            <div class="test-card">
                <div class="stars">★★★★★</div>
                <p class="quote">"The 5-agent pipeline caught nuances in our HVAC telemetry that our legacy systems completely missed."</p>
                <div class="divider"></div>
                <div class="author">Data Lead</div>
                <div class="role">Heathrow T5</div>
            </div>
        </div>
    </section>

    <section style="border:none;">
        <div class="cta-banner">
            <div class="cta-glow"></div>
            <div class="cta-left">
                <h2>Ready to make your building <span>smarter?</span></h2>
            </div>
            <div class="cta-right">
                <p style="color:rgba(255,255,255,0.85); margin-bottom:32px; font-size:18px;">
                    Start exploring your building data with natural language today.
                </p>
                <div style="display:flex; gap:16px;">
                    <a href="#" style="background:#E8500A; color:white; padding:14px 32px; border-radius:8px; text-decoration:none; font-weight:700; font-size:16px; transition:0.3s; box-shadow:0 10px 20px rgba(232,80,10,0.2);">
                        Book a demo
                    </a>
                </div>
            </div>
        </div>
    </section>

    <footer style="text-align:center; padding-top:40px; padding-bottom:80px;">
        <div style="max-width:800px; margin:0 auto; padding-bottom:48px; border-bottom:1px solid #e5e7eb;">
            <div style="font-family:'Syne',sans-serif; font-size:14px; font-weight:700; color:#111827; margin-bottom:16px;">TECHFEST</div>
            <div style="font-size:13px; color:#4b5563; margin-bottom:8px;">• Innovation Accelerator, 2024</div>
            <div style="font-size:13px; color:#4b5563;">• Best Use of Technology: Smart Data Collection for Asset Management, 2024</div>
        </div>

        <div class="foot-grid" style="padding-top:48px; text-align:left;">
            <div>
                <div class="foot-brand">Smart<span>Viz</span></div>
                <p style="font-size:14px; color:#6b7280; margin-top:12px;">Better Buildings. Better Places.</p>
            </div>
            <div class="foot-col">
                <h4>Platform</h4>
                <ul>
                    <li><a href="#">Our Tech</a></li>
                    <li><a href="#">Our Vision</a></li>
                    <li><a href="#">Our Clients</a></li>
                </ul>
            </div>
            <div class="foot-col">
                <h4>Resources</h4>
                <ul>
                    <li><a href="#">Case Studies</a></li>
                    <li><a href="#">Blogs</a></li>
                    <li><a href="#">News</a></li>
                    <li><a href="#">Contact</a></li>
                </ul>
            </div>
            <div class="foot-col">
                <h4>Legal</h4>
                <ul>
                    <li><a href="#">Privacy Policy</a></li>
                    <li><a href="#">Terms of Use</a></li>
                    <li><a href="#">Sitemap</a></li>
                </ul>
            </div>
        </div>
        <div class="foot-bottom" style="margin-top:48px; padding-bottom:20px;">
            <span style="font-size:12px; color:#6b7280;">© 2026 SmartViz Copyright SmartViz Ltd. Company No. 13894674 (Registered in England and Wales)</span>
        </div>
    </footer>
    </body></html>
    """, height=2550, scrolling=True)
    

