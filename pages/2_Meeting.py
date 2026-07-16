import json
import streamlit as st
from utils.gsheet import GoogleSheet, N_MEETINGS

st.set_page_config(page_title="Meeting", page_icon="📖", layout="wide")

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

# ---- pilih meeting ----
default_meeting = st.session_state.get("selected_meeting", 1)
meeting_number = st.sidebar.selectbox(
    "Pilih Meeting", options=list(range(1, N_MEETINGS + 1)),
    index=default_meeting - 1,
    format_func=lambda i: f"Meeting {i}: {materials.get(f'meeting_{i}', {}).get('title', '')}",
)
st.session_state.selected_meeting = meeting_number

meeting_key = f"meeting_{meeting_number}"
meeting = materials.get(meeting_key)

if meeting is None:
    st.error("Data meeting tidak ditemukan.")
    st.stop()

gs = GoogleSheet()
data = gs.get_user_data(email, nama)
current_status = data.get(f"{meeting_key}_status", "not_started")

st.title(f"📖 Meeting {meeting_number}: {meeting['title']}")
status_badge = {"not_started": "⬜ Belum Dikerjakan", "in_progress": "🟡 Sedang Dikerjakan", "completed": "🟢 Selesai"}
st.caption(status_badge.get(current_status, current_status))

# tandai "sedang dikerjakan" begitu dibuka, kalau belum pernah disentuh
if current_status == "not_started":
    gs.update_meeting_progress(email, meeting_number, "in_progress")

st.markdown("## 📚 Materi")
st.markdown(meeting["materi"])

st.divider()
st.markdown("## ✍️ Tugas")

with st.form(f"quiz_form_{meeting_number}"):
    user_answers = []
    for idx, soal in enumerate(meeting["soal"]):
        st.markdown(f"**{idx + 1}. {soal['question']}**")
        if soal["type"] == "multiple_choice":
            ans = st.radio("Pilih jawaban:", soal["options"], key=f"mc_{meeting_number}_{idx}", index=None, label_visibility="collapsed")
        elif soal["type"] == "fill_in":
            ans = st.text_input("Jawaban:", key=f"fi_{meeting_number}_{idx}", label_visibility="collapsed")
        else:  # essay
            ans = st.text_area("Jawaban:", key=f"es_{meeting_number}_{idx}", label_visibility="collapsed", height=100)
        user_answers.append(ans)
        st.write("")

    submitted = st.form_submit_button("✅ Cek Jawaban", use_container_width=True)

if submitted:
    total_points = 0
    max_points = len(meeting["soal"])
    st.markdown("## 💡 Feedback")

    for idx, soal in enumerate(meeting["soal"]):
        ans = user_answers[idx]
        st.markdown(f"**Soal {idx + 1}:** {soal['question']}")

        if soal["type"] == "multiple_choice":
            if ans == soal["answer"]:
                st.success("✅ Jawaban Anda benar!")
                total_points += 1
            elif ans is None:
                st.info("⚪ Belum dijawab.")
            else:
                st.error(f"❌ Jawaban Anda salah. Kunci jawaban: **{soal['answer']}**")

        elif soal["type"] == "fill_in":
            if ans and soal["keyword"].lower() in ans.lower():
                st.success("✅ Jawaban Anda benar!")
                total_points += 1
            elif not ans:
                st.info("⚪ Belum dijawab.")
            else:
                st.error(f"❌ Jawaban kurang tepat. Kunci jawaban: **{soal['answer']}**")

        else:  # essay -> self assessment
            st.info("📝 Ini soal esai. Bandingkan jawabanmu dengan panduan berikut, lalu nilai sendiri.")
            st.caption("Panduan: perhatikan grammar, kelengkapan kalimat, dan kesesuaian dengan materi.")
            self_score = st.slider(
                f"Nilai jawabanmu sendiri untuk soal {idx + 1} (1 = kurang, 5 = sangat baik)",
                1, 5, 3, key=f"self_{meeting_number}_{idx}",
            )
            total_points += self_score / 5  # dinormalisasi ke skala 1 poin

        st.divider()

    score_10 = round((total_points / max_points) * 10)
    st.markdown(f"### 🏆 Skor Meeting {meeting_number}: {score_10}/10")

    if score_10 >= 8:
        st.success("💡 Rekomendasi: Bagus sekali! Kamu sudah menguasai materi ini.")
    elif score_10 >= 5:
        st.warning("💡 Rekomendasi: Cukup baik, tapi coba ulangi beberapa bagian yang masih salah.")
    else:
        st.error("💡 Rekomendasi: Perlu diulang. Baca kembali materi dan coba lagi ya!")

    new_total = gs.update_meeting_progress(email, meeting_number, "completed", score_10)
    st.session_state.selected_meeting = meeting_number
    st.balloons()
    st.caption(f"Total progress kamu sekarang: {new_total}%")
