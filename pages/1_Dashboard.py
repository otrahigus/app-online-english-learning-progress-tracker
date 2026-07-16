import streamlit as st
from utils.gsheet import GoogleSheet, N_MEETINGS
import json

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

if not st.session_state.get("authenticated"):
    st.warning("Silakan login terlebih dahulu.")
    st.stop()

email = st.session_state.user_email
nama = st.session_state.user_name

with open("data/meeting_materials.json", encoding="utf-8") as f:
    materials = json.load(f)

st.sidebar.title("📘 Menu")
st.sidebar.write(f"👤 {nama}")
if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.switch_page("app.py")

st.title("📚 Progress Belajar Bahasa Inggris")

gs = GoogleSheet()
data = gs.get_user_data(email, nama)

completed = sum(1 for i in range(1, N_MEETINGS + 1) if data[f"meeting_{i}_status"] == "completed")

col1, col2 = st.columns([3, 1])
with col1:
    st.progress(data["total_progress"] / 100)
with col2:
    st.metric("Total Progress", f"{data['total_progress']}%")

st.write(f"Kamu sudah menyelesaikan **{completed} dari {N_MEETINGS}** meeting.")

st.divider()
st.subheader("Daftar Meeting")

STATUS_LABEL = {
    "not_started": ("⬜ Belum Dikerjakan", "gray"),
    "in_progress": ("🟡 Sedang Dikerjakan", "orange"),
    "completed": ("🟢 Selesai", "green"),
}

cols = st.columns(2)
for i in range(1, N_MEETINGS + 1):
    key = f"meeting_{i}"
    title = materials.get(key, {}).get("title", f"Meeting {i}")
    status = data.get(f"meeting_{i}_status", "not_started")
    score = data.get(f"meeting_{i}_score", 0)
    label, color = STATUS_LABEL.get(status, STATUS_LABEL["not_started"])

    with cols[(i - 1) % 2]:
        with st.container(border=True):
            st.markdown(f"**Meeting {i}: {title}**")
            st.markdown(f":{color}[{label}]")
            if status == "completed":
                st.caption(f"Skor: {score}/10")
            if st.button("Buka Meeting", key=f"open_{i}"):
                st.session_state.selected_meeting = i
                st.switch_page("pages/2_Meeting.py")
