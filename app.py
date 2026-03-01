import streamlit as st

# Initialize authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Redirect based on login status
if not st.session_state.authenticated:
    st.switch_page("pages/login.py")
else:
    st.switch_page("pages/1_Landing.py")