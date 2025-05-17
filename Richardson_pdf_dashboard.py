import streamlit as st
import datetime
import os
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

# Refresh every 6 hours (6 * 60 * 60 * 1000 ms = 21,600,000 ms)
st_autorefresh(interval=21600000, key="auto_refresh")

st.set_page_config(layout="wide")

PDF_FOLDER = "path/to/your/pdf/folder"  # 🔁 Update this to your real folder path

def get_latest_pdf(folder_path):
    pdfs = list(Path(folder_path).glob("*.pdf"))
    if not pdfs:
        return None
    latest_pdf = max(pdfs, key=os.path.getmtime)
    return latest_pdf

latest_pdf = get_latest_pdf(PDF_FOLDER)

if latest_pdf:
    st.markdown(f"### 📄 Displaying: `{latest_pdf.name}`")
    st.components.v1.html(f"""
        <embed src="file://{latest_pdf.resolve()}" type="application/pdf" width="100%" height="900px">
    """, height=900)
else:
    st.warning("No PDF files found in the folder.")

st.caption(f"Last refreshed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
