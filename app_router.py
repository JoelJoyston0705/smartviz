import streamlit as st

st.set_page_config(
    page_title="SmartViz",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialise session state first
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = None

# Check URL params — must rerun after setting page
params = st.query_params
if "nav" in params:
    nav = params["nav"]
    st.query_params.clear()
    if nav == "login":
        st.session_state.page = "login"
    elif nav == "signup":
        st.session_state.page = "signup"
    elif nav == "app":
        st.session_state.page = "app"
    elif nav == "resources":
        st.session_state.page = "resources"
    st.rerun()

# Router
if st.session_state.page == "landing":
    from landing import show_landing
    show_landing()

elif st.session_state.page == "login":
    from login import show_login
    show_login()

elif st.session_state.page == "signup":
    from signup import show_signup
    show_signup()

elif st.session_state.page == "resources":
    from resources import show_resources
    show_resources()

elif st.session_state.page == "app":
    if not st.session_state.logged_in:
        st.session_state.page = "login"
        st.rerun()
    else:
        from main_app import show_main_app
        show_main_app()