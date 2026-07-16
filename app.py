"""
app.py — Entry point aplikasi English Learning Progress Tracker.
Menangani login. Setelah login, user diarahkan ke halaman Dashboard, Meeting, dan Profile
(lihat folder pages/).
"""

import streamlit as st
from utils.auth import check_auth

st.set_page_config(page_title="English Learning App", page_icon="📘", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ------------------ HALAMAN LOGIN ------------------
if not st.session_state.authenticated:
    st.title("🔐 Login — English Learning App")
    st.caption("Masuk dengan akun yang sudah didaftarkan oleh mentor/guru.")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        user = check_auth(email, password)
        if user:
            st.session_state.authenticated = True
            st.session_state.user_email = user["email"]
            st.session_state.user_name = user["nama"]
            st.success(f"Selamat datang, {user['nama']}! Mengarahkan ke Dashboard...")
            st.switch_page("pages/1_Dashboard.py")
        else:
            st.error("Email atau password salah!")

    st.stop()

# ------------------ SUDAH LOGIN ------------------
# Kalau user sudah authenticated tapi membuka app.py langsung, arahkan ke Dashboard.
st.switch_page("pages/1_Dashboard.py")
