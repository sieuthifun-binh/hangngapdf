import streamlit as st
import fitz  # PyMuPDF
import os
import io
import tabula
import pandas as pd
from pdf2docx import Converter

# Cấu hình giao diện
st.set_page_config(page_title="PDF Pro Toolkit", layout="wide", page_icon="📄")
st.title("🚀 PDF Pro Toolkit - By Nguyen Thi Hang Nga - TTYT AD")

# --- HÀM XỬ LÝ ---
def split_pdf(uploaded_file, mode, custom_pages=None):
    uploaded_file.seek(0)
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

# --- GIAO DIỆN CHÍNH ---
tab1, tab2, tab3 = st.tabs(["✂️ Băm PDF", "📝 PDF sang Word", "📊 PDF sang Excel"])

with tab1:
    st.subheader("Băm PDF")
    mode = st.radio("Chế độ:", ["Trang chẵn", "Trang lẻ", "Tùy chọn"], key="split")
    pages = st.text_input("Trang (VD: 1,3,5):") if mode == 'Tùy chọn' else None
    uploaded = st.file_uploader("Tải PDF:", type="pdf", key="file_split")
    if st.button("Băm ngay"):
        if uploaded:
            res = split_pdf(uploaded, mode, pages)
            if res:
                pdf_bytes = res.write()
                st.download_button("📥 Tải PDF", data=pdf_bytes, file_name="split.pdf", mime="application/pdf")
            else: st.error("Lỗi xử lý trang!")

with tab2:
    st.subheader("PDF sang Word")
    file_word = st.file_uploader("Tải PDF:", type="pdf", key="word")
    if st.button("Convert to Word"):
        if file_word:
            with open("temp.pdf", "wb") as f: f.write(file_word.getbuffer())
            try:
                cv = Converter("temp.pdf")
                cv.convert("out.docx", layout=True) # layout=True giữ bố cục tốt hơn
                cv.close()
                with open("out.docx", "rb") as f: st.download_button("📥 Tải Word", f, "output.docx")
                os.remove("temp.pdf"); os.remove("out.docx")
            except Exception as e: st.error(f"Lỗi: {e}")

with tab3:
    st.subheader("📊 PDF sang Excel (Sử dụng PDFPlumber)")
    excel_file = st.file_uploader("Tải PDF bảng biểu:", type="pdf", key="excel")
    if st.button("Convert sang Excel"):
        if excel_file:
            try:
                import pdfplumber
                # Mở PDF bằng pdfplumber
                with pdfplumber.open(excel_file) as pdf:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        for i, page in enumerate(pdf.pages):
                            table = page.extract_table()
                            if table:
                                df = pd.DataFrame(table[1:], columns=table[0])
                                df.to_excel(writer, sheet_name=f'Page_{i+1}', index=False)
                    
                    st.download_button(
                        label="📥 Tải về Excel",
                        data=output.getvalue(),
                        file_name="data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                st.success("✅ Chuyển đổi thành công!")
            except Exception as e:
                st.error(f"Lỗi chuyển đổi: {e}")
