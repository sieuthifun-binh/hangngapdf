import streamlit as st
import pikepdf
import pdfplumber
import pandas as pd
import io
import google.generativeai as genai
from pdf2docx import Converter
import fitz

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
    st.subheader("📝 PDF sang Word (Thông minh)")
    file_word = st.file_uploader("Tải PDF:", type="pdf", key="w_ai")
    
    if st.button("Chuyển đổi & Tóm tắt"):
        if file_word:
            with st.spinner("Đang chuyển đổi và nhờ AI phân tích..."):
                # 1. Chuyển đổi PDF sang Word
                with open("in.pdf", "wb") as f: f.write(file_word.getbuffer())
                cv = Converter("in.pdf")
                cv.convert("out.docx", layout=True)
                cv.close()
                
                # 2. Dùng AI tóm tắt nội dung
                # Lấy text từ PDF để AI đọc
                doc_text = ""
                with fitz.open("in.pdf") as doc:
                    for page in doc:
                        doc_text += page.get_text()
                
                # Gọi Gemini để tóm tắt
                prompt = f"Hãy tóm tắt ngắn gọn nội dung văn bản này trong 3-5 ý chính:\n\n{doc_text[:5000]}" # Giới hạn ký tự để tránh lỗi
                response = model.generate_content(prompt)
                
                # 3. Hiển thị kết quả
                st.success("✅ Chuyển đổi hoàn tất!")
                st.markdown("### 💡 Tóm tắt nội dung tài liệu:")
                st.info(response.text)
                
                with open("out.docx", "rb") as f: 
                    st.download_button("📥 Tải File Word", f, "output.docx")

# --- TAB 3: PDF SANG EXCEL ---
with tab3:
    f_e = st.file_uploader("PDF Scan sang Excel (AI):", type="pdf", key="e1")
    if st.button("AI Extract Data"):
        with st.spinner("AI đang phân tích..."):
            with pdfplumber.open(f_e) as pdf:
                # Trích xuất bảng bằng thư viện, nếu phức tạp sẽ đẩy cho AI phân tích
                page = pdf.pages[0]
                table = page.extract_table()
                df = pd.DataFrame(table[1:], columns=table[0])
            out = io.BytesIO()
            df.to_excel(out, index=False)
            st.download_button("📥 Tải Excel", out.getvalue(), "data.xlsx")
st.markdown("---")
st.caption("✨ Hệ thống được tối ưu hóa cho công việc văn phòng chuyên nghiệp.")
