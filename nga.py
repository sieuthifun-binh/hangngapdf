import streamlit as st
import pikepdf
import pdfplumber
import pandas as pd
import io
from pdf2docx import Converter

st.set_page_config(page_title="PDF Tool Pro", layout="wide")
st.title("🛠 Công cụ PDF Ổn Định & Toàn Diện - BY HẰNG NGA ")

tab1, tab2, tab3 = st.tabs(["✂️ Băm PDF", "📝 PDF sang Word", "📊 PDF sang Excel"])

# --- TAB 1: BĂM PDF ---
with tab1:
    st.subheader("Băm PDF (Chẵn / Lẻ / Tùy chọn)")
    uploaded = st.file_uploader("Tải PDF:", type="pdf", key="bam")
    mode = st.radio("Chế độ:", ["Trang chẵn", "Trang lẻ", "Tùy chọn"])
    custom = st.text_input("Nhập số trang (VD: 1,3,5):") if mode == "Tùy chọn" else None
    
    if st.button("Băm ngay"):
        if uploaded:
            pdf = pikepdf.Pdf.open(uploaded)
            new_pdf = pikepdf.Pdf.new()
            total = len(pdf.pages)
            
            if mode == "Tùy chọn" and custom:
                indices = [int(p.strip()) - 1 for p in custom.split(',')]
            else:
                indices = [i for i in range(total) if (i+1)%2 == (0 if mode == 'Trang chẵn' else 1)]
            
            for i in indices: 
                if 0 <= i < total: new_pdf.pages.append(pdf.pages[i])
            
            output = io.BytesIO()
            new_pdf.save(output)
            st.download_button("📥 Tải kết quả", output.getvalue(), "result.pdf")

# --- TAB 2: PDF SANG WORD ---
with tab2:
    file_word = st.file_uploader("PDF sang Word:", type="pdf", key="word")
    if st.button("Convert to Word"):
        with open("in.pdf", "wb") as f: f.write(file_word.getbuffer())
        cv = Converter("in.pdf")
        cv.convert("out.docx", layout=True)
        cv.close()
        with open("out.docx", "rb") as f: st.download_button("📥 Tải Word", f, "out.docx")

# --- TAB 3: PDF SANG EXCEL ---
with tab3:
    file_excel = st.file_uploader("PDF sang Excel:", type="pdf", key="excel")
    if st.button("Convert to Excel"):
        output = io.BytesIO()
        with pdfplumber.open(file_excel) as pdf, pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for i, page in enumerate(pdf.pages):
                table = page.extract_table()
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df.to_excel(writer, sheet_name=f'Page_{i+1}', index=False)
        st.download_button("📥 Tải Excel", output.getvalue(), "data.xlsx")
