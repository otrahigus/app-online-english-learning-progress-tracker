"""
utils/auth.py
Autentikasi sederhana berbasis daftar user di st.secrets["auth"]["users"].

Contoh isi secrets.toml:

[auth]
users = [
    {email = "student1@email.com", password = "password123", name = "Andi"},
    {email = "student2@email.com", password = "password456", name = "Siti"}
]
"""

import streamlit as st


def _get_users():
    return st.secrets.get("auth", {}).get("users", [])


def check_auth(email: str, password: str):
    """Return dict user (tanpa password) kalau kredensial cocok, else None."""
    for user in _get_users():
        if user.get("email", "").lower() == email.strip().lower() and user.get("password") == password:
            return {"email": user["email"], "nama": user.get("name", user["email"])}
    return None


def get_user_name(email: str) -> str:
    for user in _get_users():
        if user.get("email", "").lower() == email.lower():
            return user.get("name", email)
    return email
