import streamlit as st
import streamlit.components.v1 as components

def show_resources():
    # ── GLOBAL STYLES ─────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Syne:wght@700;800&display=swap');

    /* ── Reset & Base ── */
    html { scroll-behavior: smooth; }
    [data-testid="stAppViewContainer"] { background:#f9fafb !important; }
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
        background:#E8500A !important;
        color:#ffffff !important;
        box-shadow:0 1px 3px rgba(232,80,10,0.3) !important;
    }
    div[data-testid="stButton"] > button:hover {
        background:#d14509 !important;
        transform:translateY(-1px) !important;
    }

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
        <a href="/?nav=landing" target="_self" class="logo-container" style="padding-left:48px;">
          <div style="font-family:'Syne',sans-serif;font-size:32px;font-weight:800;color:#111827;letter-spacing:-1.2px;line-height:1;">
            Smart<span style="color:#E8500A;">Viz</span>
          </div>
          <div style="font-family:'Inter',sans-serif;font-size:10px;color:#9ca3af;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-top:2px;">
            <span style="color:#111827;">Better</span> Buildings. <span style="color:#111827;">Better</span> Places.
          </div>
        </a>
        """, unsafe_allow_html=True)
    with nav_links1:
        st.markdown('<a href="/?nav=landing#platform" target="_self" class="nav-link">Platform ▾</a>', unsafe_allow_html=True)
    with nav_links2:
        st.markdown('<a href="/?nav=landing#how-it-works" target="_self" class="nav-link">How it works</a>', unsafe_allow_html=True)
    with nav_links3:
        st.markdown('<a href="/?nav=landing#clients" target="_self" class="nav-link">Clients</a>', unsafe_allow_html=True)
    with nav_links4:
        st.markdown('<a href="#" class="nav-link" style="color:#111827; font-weight:600;">Resources ▾</a>', unsafe_allow_html=True)
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

    # ── HEADER & CONTENT ──
    components.html("""
    <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Syne:wght@700;800&display=swap" rel="stylesheet">
    <style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{
        font-family:'Inter',sans-serif;color:#111827;
        background-color:#f9fafb;
        background-image: radial-gradient(circle, #e5e7eb 1px, transparent 1px);
        background-size: 32px 32px;
    }
    .hero{text-align:center;padding:120px 48px 80px;position:relative;}
    .hero-glow{position:absolute;top:-50%;left:50%;transform:translateX(-50%);width:600px;height:400px;background:rgba(232,80,10,0.1);filter:blur(80px);z-index:-1;}
    .eyebrow{color:#E8500A;font-weight:700;letter-spacing:1.5px;font-size:12px;text-transform:uppercase;margin-bottom:16px;display:block;}
    h1{font-family:'Syne',sans-serif;font-size:56px;font-weight:800;letter-spacing:-2px;margin-bottom:24px;line-height:1.1;}
    h1 span{color:#E8500A;}
    p.sub{font-size:18px;color:#6b7280;line-height:1.6;max-width:600px;margin:0 auto;}
    
    .container{max-width:1200px;margin:0 auto;padding:0 48px 120px;}
    .section-title{font-family:'Syne',sans-serif;font-size:32px;font-weight:800;letter-spacing:-1px;margin:80px 0 32px;}
    
    .grid{display:grid;grid-template-columns:repeat(3, 1fr);gap:32px;}
    .card{background:#fff;border:1px solid #e5e7eb;border-radius:16px;padding:32px;transition:all 0.2s;display:flex;flex-direction:column;box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);}
    .card:hover{transform:translateY(-4px);box-shadow:0 20px 25px -5px rgba(0,0,0,0.1),0 10px 10px -5px rgba(0,0,0,0.04);border-color:#d1d5db;}
    .card-tag{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#E8500A;margin-bottom:16px;}
    .card-title{font-size:20px;font-weight:700;color:#111827;line-height:1.4;margin-bottom:16px;font-family:'Syne',sans-serif;letter-spacing:-0.5px;}
    .card-link{margin-top:auto;color:#3b82f6;font-size:14px;font-weight:600;text-decoration:none;display:inline-flex;align-items:center;gap:4px;}
    .card-link:hover{color:#2563eb;}
    
    /* Footer */
    footer{padding:80px 48px;background:#f9fafb;border-top:1px solid #e5e7eb;margin-top:60px;}
    .foot-grid{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:64px;max-width:1200px;margin:0 auto;}
    .foot-brand{font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:#111827;}
    .foot-brand span{color:#E8500A;}
    .foot-col h4{font-size:14px;text-transform:uppercase;letter-spacing:1px;margin-bottom:24px;}
    .foot-col ul{list-style:none;}
    .foot-col ul li{margin-bottom:12px;}
    .foot-col ul li a{text-decoration:none;color:#6b7280;font-size:14px;transition:0.2s;}
    .foot-col ul li a:hover{color:#E8500A;}
    </style></head><body>
    
    <div class="hero">
        <div class="hero-glow"></div>
        <span class="eyebrow">SmartViz Hub</span>
        <h1>Discover our <span>insights</span></h1>
        <p class="sub">Explore case studies, detailed white papers, our latest news, informative videos, and more.</p>
    </div>

    <div class="container">
        <!-- CASE STUDIES -->
        <h2 class="section-title">Client Case Studies</h2>
        <div class="grid">
            <a href="https://www.smart-viz.com/case-study/university-of-southampton/" target="_blank" style="text-decoration:none; display:content;">
                <div class="card">
                    <div class="card-tag">Case Study</div>
                    <div class="card-title">How SmartViz optimised space utilisation at the University of Southampton</div>
                    <div class="card-link">Read Case Study &rarr;</div>
                </div>
            </a>
            <a href="https://www.smart-viz.com/case-study/royal-united-hospital/" target="_blank" style="text-decoration:none;">
                <div class="card">
                    <div class="card-tag">Case Study</div>
                    <div class="card-title">How SmartViz helped Royal United Hospital (RUH) improve outpatient operations</div>
                    <div class="card-link">Read Case Study &rarr;</div>
                </div>
            </a>
            <a href="https://www.smart-viz.com/case-study/vodafone/" target="_blank" style="text-decoration:none;">
                <div class="card">
                    <div class="card-tag">Case Study</div>
                    <div class="card-title">How SmartViz helped Vodafone cut multi-million dollar costs</div>
                    <div class="card-link">Read Case Study &rarr;</div>
                </div>
            </a>
            <a href="https://www.smart-viz.com/case-study/cardiff-metropolitan-university/" target="_blank" style="text-decoration:none;">
                <div class="card">
                    <div class="card-tag">Case Study</div>
                    <div class="card-title">Transforming Cardiff Met’s campus space management with IoT sensors</div>
                    <div class="card-link">Read Case Study &rarr;</div>
                </div>
            </a>
            <a href="https://www.smart-viz.com/case-study/smarter-spaces-happier-people-how-barnsley-council-transformed-buildings-with-smart-tech-for-comfort-sustainability/" target="_blank" style="text-decoration:none;">
                <div class="card">
                    <div class="card-tag">Case Study</div>
                    <div class="card-title">Smarter Spaces, Happier People: How Barnsley Council Transformed Buildings</div>
                    <div class="card-link">Read Case Study &rarr;</div>
                </div>
            </a>
        </div>

        <!-- WHITE PAPERS -->
        <h2 class="section-title">White Papers</h2>
        <div class="grid">
            <a href="https://smart-viz.com/wp-content/uploads/2025/10/Unveiling-the-Truth_-Why-Buildings-Fall-Short-of-Smart-Expectations.pdf" target="_blank" style="text-decoration:none;">
                <div class="card" style="border-top:4px solid #8b5cf6;">
                    <div class="card-tag" style="color:#8b5cf6;">White Paper</div>
                    <div class="card-title">Unleashing the true potential: Why ‘Smart Buildings’ need to get truly smart</div>
                    <div class="card-link" style="color:#8b5cf6;">Download PDF &rarr;</div>
                </div>
            </a>
            <a href="https://www.smart-viz.com/wp-content/uploads/2025/12/SmartViz-White-Paper_-Optimise-Space.pdf" target="_blank" style="text-decoration:none;">
                <div class="card" style="border-top:4px solid #8b5cf6;">
                    <div class="card-tag" style="color:#8b5cf6;">White Paper</div>
                    <div class="card-title">Optimise space management in university estates</div>
                    <div class="card-link" style="color:#8b5cf6;">Download PDF &rarr;</div>
                </div>
            </a>
            <a href="https://www.smart-viz.com/wp-content/uploads/2025/12/SmartViz-White-Paper_-Workplace-Management.pdf" target="_blank" style="text-decoration:none;">
                <div class="card" style="border-top:4px solid #8b5cf6;">
                    <div class="card-tag" style="color:#8b5cf6;">White Paper</div>
                    <div class="card-title">Unlock the future of workplace management with IoT and AI</div>
                    <div class="card-link" style="color:#8b5cf6;">Download PDF &rarr;</div>
                </div>
            </a>
        </div>

        <!-- BLOGS -->
        <h2 class="section-title">Latest Articles</h2>
        <div class="grid">
            <a href="https://www.smart-viz.com/blog/digital-twin-tech-updates/" target="_blank" style="text-decoration:none;">
                <div class="card">
                    <div class="card-tag" style="color:#10b981;">Blog</div>
                    <div class="card-title">Your buildings are full of data – but can you see what’s happening?</div>
                    <div class="card-link" style="color:#10b981;">Read Article &rarr;</div>
                </div>
            </a>
            <a href="https://www.smart-viz.com/blog/universities-smarter-buildings/" target="_blank" style="text-decoration:none;">
                <div class="card">
                    <div class="card-tag" style="color:#10b981;">Blog</div>
                    <div class="card-title">Why universities don’t need more buildings – they need smarter ones</div>
                    <div class="card-link" style="color:#10b981;">Read Article &rarr;</div>
                </div>
            </a>
            <a href="https://www.smart-viz.com/blog/data-visualisation-for-smart-buildings/" target="_blank" style="text-decoration:none;">
                <div class="card">
                    <div class="card-tag" style="color:#10b981;">Blog</div>
                    <div class="card-title">Data visualization strategy for smart buildings</div>
                    <div class="card-link" style="color:#10b981;">Read Article &rarr;</div>
                </div>
            </a>
            <a href="https://www.smart-viz.com/blog/indoor-air-quality-monitoring/" target="_blank" style="text-decoration:none;">
                <div class="card">
                    <div class="card-tag" style="color:#10b981;">Blog</div>
                    <div class="card-title">Indoor air quality monitoring: Why it’s important for your building’s health</div>
                    <div class="card-link" style="color:#10b981;">Read Article &rarr;</div>
                </div>
            </a>
            <a href="https://www.smart-viz.com/blog/the-power-of-digital-twins-transforming-building-performance-and-user-experience/" target="_blank" style="text-decoration:none;">
                <div class="card">
                    <div class="card-tag" style="color:#10b981;">Blog</div>
                    <div class="card-title">The power of digital twins: Transforming building performance</div>
                    <div class="card-link" style="color:#10b981;">Read Article &rarr;</div>
                </div>
            </a>
            <a href="https://www.smart-viz.com/blog/boosting-workplace-productivity-with-real-time-analytics-and-digital-twins/" target="_blank" style="text-decoration:none;">
                <div class="card">
                    <div class="card-tag" style="color:#10b981;">Blog</div>
                    <div class="card-title">Boosting workplace productivity with real-time analytics</div>
                    <div class="card-link" style="color:#10b981;">Read Article &rarr;</div>
                </div>
            </a>
        </div>
    </div>

    <footer>
        <div class="foot-grid">
            <div>
                <div class="foot-brand">Smart<span>Viz</span></div>
                <p style="margin-top:16px;color:#6b7280;font-size:14px;line-height:1.6;">
                    Turn building data into instant, actionable decisions.
                </p>
            </div>
            <div class="foot-col">
                <h4>Platform</h4>
                <ul>
                    <li><a href="#">How it works</a></li>
                    <li><a href="#">Agent Pipeline</a></li>
                    <li><a href="#">Integrations</a></li>
                    <li><a href="#">Security</a></li>
                </ul>
            </div>
            <div class="foot-col">
                <h4>Resources</h4>
                <ul>
                    <li><a href="#">Case Studies</a></li>
                    <li><a href="#">Blog</a></li>
                    <li><a href="#">White Papers</a></li>
                    <li><a href="#">API Docs</a></li>
                </ul>
            </div>
            <div class="foot-col">
                <h4>Company</h4>
                <ul>
                    <li><a href="#">About Us</a></li>
                    <li><a href="#">Careers</a></li>
                    <li><a href="#">Contact</a></li>
                    <li><a href="#">Privacy Policy</a></li>
                </ul>
            </div>
        </div>
        <div class="foot-bottom">
            &copy; 2026 SmartViz Ltd. All rights reserved.
        </div>
    </footer>
    </body></html>
    """, height=2200)
