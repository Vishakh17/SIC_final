import streamlit as st
from auth import create_user, login_user

st.set_page_config(page_title="Login", layout="centered")

# Session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user_role" not in st.session_state:
    st.session_state.user_role = None

st.title("🔐 Login to AI Energy Platform")

tab1, tab2 = st.tabs(["Login", "Create Account"])

# =========================
# LOGIN TAB
# =========================
with tab1:
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        role = login_user(email, password)

        if role:
            st.session_state.authenticated = True
            st.session_state.user_role = role
            st.success("Login Successful!")
            st.switch_page("pages/1_Landing.py")
        else:
            st.error("Invalid credentials")

# =========================
# CREATE ACCOUNT TAB
# =========================
with tab2:
    new_email = st.text_input("New Email", key="reg_email")
    new_password = st.text_input("New Password", type="password", key="reg_pass")

    role = st.selectbox(
        "Select User Type",
        ["Residential", "Industrial"]
    )

    if st.button("Create Account"):
        try:
            create_user(new_email, new_password, role)
            st.success("Account Created! Please login.")
        except:
            st.error("User already exists.")