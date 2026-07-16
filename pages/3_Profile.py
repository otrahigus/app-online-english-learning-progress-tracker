import json
import streamlit as st
from utils.gsheet import GoogleSheet, N_MEETINGS

st.set_page_config(page_title="Profile", page_icon="🙍", layout="wide")

if not st.session_state.get("authenticated"):
    st.warning("Silakan login terlebih dahulu.")
    st.stop()

email = st.session_state.user_email
nama = st.session_state.user_name

with open("data/meeting_materials.json", encoding="utf-8") as f:
    materials = json.load(f)

st.sidebar.title("📘 Menu")
st.sidebar.write(f"👤 {nama}")
if st.sidebar.button("⬅️ Kembali ke Dashboard"):
    st.switch_page("pages/1_Dashboard.py")
if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.switch_page("app.py")

st.title("🙍 Profil Saya")
st.write(f"**Nama:** {nama}")
st.write(f"**Email:** {email}")

gs = GoogleSheet()
data = gs.get_user_data(email, nama)

st.metric("Total Progress", f"{data['total_progress']}%")
st.progress(data["total_progress"] / 100)

st.divider()
st.subheader("Riwayat Skor per Meeting")

rows = []
for i in range(1, N_MEETINGS + 1):
    title = materials.get(f"meeting_{i}", {}).get("title", f"Meeting {i}")
    status = data.get(f"meeting_{i}_status", "not_started")
    score = data.get(f"meeting_{i}_score", 0)
    rows.append({"Meeting": f"{i}. {title}", "Status": status, "Skor": f"{score}/10" if status == "completed" else "-"})

st.table(rows)
