"""
utils/gsheet.py
Modul koneksi & operasi Google Sheets untuk menyimpan progress belajar user.

Sheet yang dipakai (dibuat otomatis kalau belum ada) punya kolom:
email | nama | meeting_1_status | meeting_1_score | ... | meeting_10_status | meeting_10_score | total_progress
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

N_MEETINGS = 10

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADER = ["email", "nama"]
for i in range(1, N_MEETINGS + 1):
    HEADER += [f"meeting_{i}_status", f"meeting_{i}_score"]
HEADER += ["total_progress"]


class GoogleSheet:
    """Wrapper sederhana di atas gspread untuk baca/tulis progress user."""

    def __init__(self):
        self._client = self._connect()
        self._sheet = self._open_sheet()

    # ---------- koneksi ----------
    @st.cache_resource(show_spinner=False)
    def _connect(_self):
        creds_dict = dict(st.secrets["gsheet"])
        # sheet_name & spreadsheet_id bukan bagian dari service account credentials
        creds_dict.pop("sheet_name", None)
        creds_dict.pop("spreadsheet_id", None)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(creds)

    def _open_sheet(self):
        gsheet_secrets = st.secrets["gsheet"]
        spreadsheet_id = gsheet_secrets.get("spreadsheet_id", "").strip()
        sheet_name = gsheet_secrets.get("sheet_name", "english_learning_progress")

        if spreadsheet_id:
            # Cara paling stabil: buka langsung berdasarkan Spreadsheet ID.
            # ID diambil dari URL: docs.google.com/spreadsheets/d/<INI_ID_NYA>/edit
            try:
                spreadsheet = self._client.open_by_key(spreadsheet_id)
            except gspread.SpreadsheetNotFound:
                raise RuntimeError(
                    f"Spreadsheet dengan ID '{spreadsheet_id}' tidak ditemukan atau belum "
                    f"di-share ke email service account. Cek kembali spreadsheet_id di secrets.toml "
                    f"dan pastikan spreadsheet sudah di-share (akses Editor) ke client_email."
                )
        else:
            # Fallback lama: cari/buat berdasarkan nama (kurang stabil, hanya dipakai
            # kalau spreadsheet_id tidak diisi di secrets.toml).
            try:
                spreadsheet = self._client.open(sheet_name)
            except gspread.SpreadsheetNotFound:
                spreadsheet = self._client.create(sheet_name)

        worksheet = spreadsheet.sheet1
        # pastikan header ada
        existing_header = worksheet.row_values(1)
        if existing_header != HEADER:
            worksheet.clear()
            worksheet.append_row(HEADER)
        return worksheet

    # ---------- helper internal ----------
    def _find_row(self, email: str):
        """Return (row_index, row_values) atau (None, None) kalau belum ada.

        Catatan: tergantung versi gspread, .find() bisa RETURN None kalau tidak
        ketemu (versi baru) ATAU melempar CellNotFound (versi lama). Kita handle
        dua-duanya supaya tidak crash dengan AttributeError.
        """
        try:
            cell = self._sheet.find(email, in_column=1)
        except gspread.exceptions.CellNotFound:
            cell = None

        if cell is None:
            return None, None

        row_values = self._sheet.row_values(cell.row)
        return cell.row, row_values

    def _row_to_dict(self, row_values):
        row_values = row_values + [""] * (len(HEADER) - len(row_values))
        data = dict(zip(HEADER, row_values))
        for i in range(1, N_MEETINGS + 1):
            if not data.get(f"meeting_{i}_status"):
                data[f"meeting_{i}_status"] = "not_started"
            score = data.get(f"meeting_{i}_score")
            data[f"meeting_{i}_score"] = int(score) if str(score).isdigit() else 0
        try:
            data["total_progress"] = int(float(data.get("total_progress") or 0))
        except ValueError:
            data["total_progress"] = 0
        return data

    def _compute_total_progress(self, data: dict) -> int:
        completed = sum(
            1 for i in range(1, N_MEETINGS + 1)
            if data.get(f"meeting_{i}_status") == "completed"
        )
        return round(completed / N_MEETINGS * 100)

    # ---------- API publik ----------
    def get_user_data(self, email: str, nama: str = ""):
        """Ambil data user. Kalau belum ada, buat baris baru."""
        row_idx, row_values = self._find_row(email)
        if row_idx is None:
            new_row = [email, nama] + ["not_started", 0] * N_MEETINGS + [0]
            self._sheet.append_row(new_row)
            row_idx, row_values = self._find_row(email)
        data = self._row_to_dict(row_values)
        data["_row_idx"] = row_idx
        data["progress"] = data["total_progress"]
        return data

    def update_meeting_progress(self, email: str, meeting_number: int, status: str, score: int = None):
        """Update status (dan skor opsional) satu meeting untuk user, lalu hitung ulang total_progress."""
        data = self.get_user_data(email)
        row_idx = data["_row_idx"]

        col_status = HEADER.index(f"meeting_{meeting_number}_status") + 1
        self._sheet.update_cell(row_idx, col_status, status)
        data[f"meeting_{meeting_number}_status"] = status

        if score is not None:
            col_score = HEADER.index(f"meeting_{meeting_number}_score") + 1
            self._sheet.update_cell(row_idx, col_score, score)
            data[f"meeting_{meeting_number}_score"] = score

        total = self._compute_total_progress(data)
        col_total = HEADER.index("total_progress") + 1
        self._sheet.update_cell(row_idx, col_total, total)

        return total