import streamlit as st
import pikepdf
import pdfplumber
import pandas as pd
import io
from pdf2docx import Converter

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="PDF Pro Toolkit", layout="wide")

# --- CSS CHUYÊN NGHIỆP ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #f8f9fa; }
    div[data-testid="stVerticalBlock"] { 
        background-color: white; 
        padding: 2rem; 
        border-radius: 15px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
    }
    .stButton>button { 
        width: 100%; border-radius: 5px; background-color: #007bff; color: white; font-weight: bold; 
    }
    h1 { color: #2c3e50; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("🚀 PDF Pro Toolkit - By Nga Rồng Vui Vẻ")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["✂️ Băm PDF", "📝 PDF sang Word", "📊 PDF sang Excel"])

# --- TAB 1: BĂM PDF ---
with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded = st.file_uploader("Tải tệp PDF:", type="pdf", key="bam")
    with col2:
        mode = st.radio("Chế độ chọn trang:", ["Trang chẵn", "Trang lẻ", "Tùy chọn"])
        custom = st.text_input("Nhập số trang (VD: 1,3,5):") if mode == "Tùy chọn" else None
    
    if st.button("🚀 Bắt đầu Băm"):
        if uploaded:
            with st.spinner("Đang tách trang..."):
                pdf = pikepdf.Pdf.open(uploaded)
                new_pdf = pikepdf.Pdf.new()
                total = len(pdf.pages)
                indices = [int(p.strip()) - 1 for p in custom.split(',')] if mode == "Tùy chọn" else [i for i in range(total) if (i+1)%2 == (0 if mode == 'Trang chẵn' else 1)]
                for i in indices: 
                    if 0 <= i < total: new_pdf.pages.append(pdf.pages[i])
                output = io.BytesIO()
                new_pdf.save(output)
                st.download_button("📥 Tải kết quả", output.getvalue(), "result.pdf")

# --- TAB 2: PDF SANG WORD ---
with tab2:
    file_word = st.file_uploader("Tải PDF để chuyển sang Word:", type="pdf", key="word")
    if st.button("Convert to Word"):
        if file_word:
            with st.spinner("Đang chuyển đổi định dạng..."):
                with open("in.pdf", "wb") as f: f.write(file_word.getbuffer())
                cv = Converter("in.pdf")
                cv.convert("out.docx", layout=True)
                cv.close()
                with open("out.docx", "rb") as f: st.download_button("📥 Tải file Word", f, "output.docx")

# --- TAB 3: PDF SANG EXCEL ---
with tab3:
    file_excel = st.file_uploader("Tải PDF chứa bảng:", type="pdf", key="excel")
    if st.button("Convert to Excel"):
        if file_excel:
            with st.spinner("Đang trích xuất dữ liệu bảng..."):
                output = io.BytesIO()
                with pdfplumber.open(file_excel) as pdf, pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    for i, page in enumerate(pdf.pages):
                        table = page.extract_table()
                        if table:
                            df = pd.DataFrame(table[1:], columns=table[0])
                            df.to_excel(writer, sheet_name=f'Page_{i+1}', index=False)
                st.download_button("📥 Tải Excel", output.getvalue(), "data.xlsx")

st.markdown("---")
st.caption("✨ Hệ thống được tối ưu hóa cho công việc văn phòng chuyên nghiệp.")
