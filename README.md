# 📘 English Learning Progress Tracker

Aplikasi Streamlit untuk mengelola tugas belajar bahasa Inggris per meeting, dengan
feedback otomatis dan progress tersimpan di Google Sheets.

## Struktur Folder

```
streamlit-app/
├── app.py                        # Login
├── pages/
│   ├── 1_Dashboard.py            # Ringkasan progress semua meeting
│   ├── 2_Meeting.py              # Materi + soal + feedback (dinamis, pilih meeting di sidebar)
│   └── 3_Profile.py              # Profil & riwayat skor
├── data/
│   └── meeting_materials.json    # Materi & soal untuk 10 meeting
├── utils/
│   ├── gsheet.py                 # Koneksi & operasi Google Sheets
│   └── auth.py                   # Autentikasi sederhana via st.secrets
├── .streamlit/
│   └── secrets.toml.example      # Template kredensial (salin -> secrets.toml)
├── .gitignore
└── requirements.txt
```

> **Catatan desain:** alih-alih 10 file halaman terpisah (`2_Meeting_1.py` ... `11_Meeting_10.py`),
> dipakai **satu halaman dinamis** `2_Meeting.py` yang memuat materi dari `meeting_materials.json`
> berdasarkan meeting yang dipilih. Ini lebih mudah dipelihara — tambah/ubah meeting cukup edit JSON,
> tidak perlu bikin file Python baru.

## 1. Setup Google Sheets (Service Account)

1. Buka [Google Cloud Console](https://console.cloud.google.com/) → buat project baru.
2. Aktifkan **Google Sheets API** dan **Google Drive API**.
3. Buat **Service Account** → buat key baru (format JSON) → unduh file JSON-nya.
4. Buat spreadsheet baru di Google Sheets (nama bebas, misalnya `english_learning_progress`).
5. **Share** spreadsheet tersebut ke email `client_email` yang ada di file JSON service account
   (beri akses **Editor**).
6. Salin **Spreadsheet ID** dari URL spreadsheet:
   `https://docs.google.com/spreadsheets/d/`**`INI_SPREADSHEET_ID_NYA`**`/edit`
   → isi ke `spreadsheet_id` di `secrets.toml`.

> Kenapa pakai ID, bukan nama? Membuka spreadsheet berdasarkan **ID** jauh lebih stabil —
> tidak masalah walau namanya diganti, dan tidak ambigu kalau ada beberapa spreadsheet
> dengan nama yang mirip. Kalau `spreadsheet_id` dikosongkan, aplikasi akan fallback
> mencari/membuat spreadsheet berdasarkan `sheet_name` (kurang direkomendasikan).

## 2. Isi `secrets.toml`

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Buka `.streamlit/secrets.toml`, lalu isi bagian `[gsheet]` dengan nilai dari file JSON
service account (project_id, private_key, client_email, dst), dan bagian `[auth]`
dengan daftar user (email, password, nama) yang boleh login.

⚠️ **Jangan pernah commit `secrets.toml` yang berisi kredensial asli ke GitHub** —
file ini sudah dimasukkan ke `.gitignore`.

## 3. Jalankan secara lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 4. Push ke GitHub

```bash
git init
git add .
git commit -m "Initial commit: English Learning App"
git branch -M main
git remote add origin https://github.com/USERNAME/REPO_NAME.git
git push -u origin main
```

## 5. Deploy ke Streamlit Community Cloud

1. Buka [share.streamlit.io](https://share.streamlit.io) → login dengan GitHub.
2. Pilih repo ini, branch `main`, main file `app.py`.
3. Di menu **Advanced settings → Secrets**, paste isi `secrets.toml` kamu (kredensial asli).
4. Deploy. Aplikasi akan otomatis punya URL publik.

## Menambah/Mengubah Materi

Edit `data/meeting_materials.json`. Setiap meeting berbentuk:

```json
"meeting_1": {
  "title": "...",
  "materi": "markdown teks materi",
  "soal": [
    {"type": "multiple_choice", "question": "...", "options": [...], "answer": "..."},
    {"type": "fill_in", "question": "...", "keyword": "...", "answer": "..."},
    {"type": "essay", "question": "...", "self_assessment": true}
  ]
}
```

## Cara Kerja Feedback Otomatis

| Tipe Soal | Cara Feedback |
|-----------|---------------|
| **Multiple Choice** | Dibandingkan langsung dengan `answer` → ✅/❌ |
| **Fill-in** | Dicek apakah `keyword` (case-insensitive) ada dalam jawaban user |
| **Essay** | Ditampilkan panduan penilaian, user menilai sendiri (1-5) via slider |

Skor akhir dinormalisasi ke skala **/10** dan disimpan ke Google Sheets bersama status
`completed`, lalu `total_progress` (%) dihitung ulang otomatis.

## Pengembangan Lanjutan (opsional, belum diimplementasikan)

- Export progress ke PDF/CSV
- Leaderboard multi-user
- Koreksi esai otomatis via LLM API (OpenAI/Gemini/Claude)
- Dark mode toggle
- Admin panel untuk melihat progress semua siswa
