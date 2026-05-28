import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
from pdf2docx import Converter
import io
import os

# Cấu hình trang
st.set_page_config(page_title="PDF Pro Toolkit", layout="wide")
st.title("🚀 PDF Pro Toolkit - Công cụ xử lý PDF")

# --- HÀM XỬ LÝ PDF ---
def split_pdf(uploaded_file, mode, custom_pages=None):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    new_doc = fitz.open()
    
    if mode == 'Trang chẵn':
        for i in range(1, len(doc), 2): new_doc.insert_pdf(doc, from_page=i, to_page=i)
    elif mode == 'Trang lẻ':
        for i in range(0, len(doc), 2): new_doc.insert_pdf(doc, from_page=i, to_page=i)
    elif mode == 'Tùy chọn':
        try:
            pages = [int(p.strip()) - 1 for p in custom_pages.split(',')]
            for p in pages:
                if 0 <= p < len(doc): new_doc.insert_pdf(doc, from_page=p, to_page=p)
        except: return None
    return new_doc

# --- GIAO DIỆN ---
tab1, tab2 = st.tabs(["✂️ Băm PDF", "📝 PDF sang Word"])

with tab1:
    st.subheader("Băm PDF")
    mode = st.radio("Chế độ:", ["Trang chẵn", "Trang lẻ", "Tùy chọn"])
    custom_pages = st.text_input("Trang (VD: 1,3,5):") if mode == 'Tùy chọn' else None
    
    uploaded_file = st.file_uploader("Chọn file PDF:", type="pdf")
    
    if st.button("Xử lý Băm"):
        if uploaded_file:
            result = split_pdf(uploaded_file, mode, custom_pages)
            if result:
                pdf_bytes = result.write()
                st.download_button("📥 Tải về PDF", data=pdf_bytes, file_name="split.pdf", mime="application/pdf")
            else: st.error("Lỗi xử lý trang!")

with tab2:
    st.subheader("PDF sang Word")
    docx_file = st.file_uploader("Chọn file PDF để chuyển:", type="pdf")
    if st.button("Convert sang Word"):
        if docx_file:
            with open("temp.pdf", "wb") as f: f.write(docx_file.getbuffer())
            cv = Converter("temp.pdf")
            cv.convert("output.docx", start=0, end=None)
            cv.close()
            with open("output.docx", "rb") as f:
                st.download_button("📥 Tải về Word", data=f, file_name="converted.docx")
            os.remove("temp.pdf")
            os.remove("output.docx")
