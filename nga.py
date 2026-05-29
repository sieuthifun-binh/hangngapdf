import streamlit as st
import pikepdf
import pdfplumber
import pandas as pd
import io
import fitz
import google.generativeai as genai
from pdf2docx import Converter
import tempfile
import os

st.set_page_config(page_title="Pro PDF AI Suite", layout="wide")

# --- KHỞI TẠO AI ---
if 'model' not in st.session_state:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        st.session_state.model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🏛️ Pro PDF AI Toolkit")
tab1, tab2, tab3 = st.tabs(["✂️ Băm PDF", "📝 PDF sang Word", "📊 AI PDF sang Excel"])

# --- TAB 1: BĂM PDF ---
with tab1:
    uploaded = st.file_uploader("Tải PDF:", type="pdf", key="b1")
    mode = st.radio("Chế độ:", ["Chẵn", "Lẻ", "Tùy chọn"], key="m1")
    pages = st.text_input("Trang (VD: 1,3,5):") if mode == 'Tùy chọn' else ""
    
    if st.button("Xử lý Băm"):
        if uploaded:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded.getvalue())
                pdf = pikepdf.Pdf.open(tmp.name)
                new_pdf = pikepdf.Pdf.new()
                total = len(pdf.pages)
                idx = [int(p.strip())-1 for p in pages.split(',')] if mode == 'Tùy chọn' else [i for i in range(total) if (i+1)%2 == (0 if mode == 'Chẵn' else 1)]
                for i in idx:
                    if 0 <= i < total: new_pdf.pages.append(pdf.pages[i])
                out = io.BytesIO()
                new_pdf.save(out)
                st.download_button("📥 Tải về", out.getvalue(), "split.pdf")
                os.remove(tmp.name)

# --- TAB 2: PDF SANG WORD ---
with tab2:
    f_w = st.file_uploader("PDF sang Word:", type="pdf", key="w_ai")
    if st.button("Chuyển đổi & Tóm tắt"):
        if f_w:
            with tempfile.TemporaryDirectory() as tmp_dir:
                in_path = os.path.join(tmp_dir, "in.pdf")
                out_path = os.path.join(tmp_dir, "out.docx")
                with open(in_path, "wb") as f: f.write(f_w.getbuffer())
                
                # Chuyển đổi
                cv = Converter(in_path)
                cv.convert(out_path, layout=True)
                cv.close()
                
                # Tóm tắt AI
                try:
                    doc_text = ""
                    with fitz.open(in_path) as doc:
                        for page in doc: doc_text += page.get_text()
                    prompt = f"Tóm tắt 3 ý chính của văn bản này:\n\n{doc_text[:2000]}"
                    res = st.session_state.model.generate_content(prompt)
                    st.info(f"💡 Tóm tắt: {res.text}")
                except:
                    st.warning("AI không thể tóm tắt được (có thể do API Key hoặc nội dung quá ngắn).")
                
                with open(out_path, "rb") as f: 
                    st.download_button("📥 Tải File Word", f, "output.docx")

# --- TAB 3: AI PDF SANG EXCEL ---
with tab3:
    f_e = st.file_uploader("PDF Scan sang Excel:", type="pdf", key="e1")
    if st.button("AI Extract Data"):
        if f_e:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(f_e.getvalue())
                with pdfplumber.open(tmp.name) as pdf:
                    table = pdf.pages[0].extract_table()
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        out = io.BytesIO()
                        df.to_excel(out, index=False)
                        st.download_button("📥 Tải Excel", out.getvalue(), "data.xlsx")
                    else:
                        st.error("Không tìm thấy bảng dữ liệu nào trong PDF!")
                os.remove(tmp.name)
