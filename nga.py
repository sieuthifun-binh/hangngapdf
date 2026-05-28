import streamlit as st
import pikepdf
import fitz
import io
import pandas as pd
import json
import google.generativeai as genai
from pdf2docx import Converter

# --- CẤU HÌNH API AI ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"Lỗi khởi tạo AI: {e}")

st.set_page_config(page_title="PDF Pro Toolkit", layout="wide")
st.title("🚀 PDF Pro Toolkit - Bản Hoàn Chỉnh & Ổn Định")

# --- HÀM XỬ LÝ PDF ---
def split_pdf_advanced(uploaded_file, mode, custom_pages=None):
    pdf = pikepdf.Pdf.open(uploaded_file)
    new_pdf = pikepdf.Pdf.new()
    
    total_pages = len(pdf.pages)
    pages_to_extract = []
    
    if mode == 'Trang chẵn':
        pages_to_extract = [i for i in range(total_pages) if (i + 1) % 2 == 0]
    elif mode == 'Trang lẻ':
        pages_to_extract = [i for i in range(total_pages) if (i + 1) % 2 != 0]
    elif mode == 'Tùy chọn':
        pages_to_extract = [int(p.strip()) - 1 for p in custom_pages.split(',')]
        
    for p in pages_to_extract:
        if 0 <= p < total_pages:
            new_pdf.pages.append(pdf.pages[p])
            
    output = io.BytesIO()
    new_pdf.save(output)
    return output.getvalue()

def ai_process_table(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    page = doc[0] 
    pix = page.get_pixmap()
    img_data = pix.tobytes("png")
    
    response = model.generate_content([
        "Hãy trích xuất bảng trong ảnh này thành định dạng JSON chuẩn, cấu trúc theo hàng và cột. Chỉ trả về JSON.",
        {"mime_type": "image/png", "data": img_data}
    ])
    raw_text = response.text.replace("```json", "").replace("```", "")
    return pd.DataFrame(json.loads(raw_text))

# --- GIAO DIỆN ---
tab1, tab2, tab3 = st.tabs(["✂️ Băm PDF (Chẵn/Lẻ)", "📝 PDF sang Word", "📊 PDF Excel (AI)"])

with tab1:
    mode = st.radio("Chế độ:", ["Trang chẵn", "Trang lẻ", "Tùy chọn"])
    custom_pages = st.text_input("Trang (VD: 1,3,5):") if mode == 'Tùy chọn' else None
    uploaded = st.file_uploader("Tải PDF:", type="pdf", key="băm")
    if st.button("Băm ngay"):
        if uploaded:
            data = split_pdf_advanced(uploaded, mode, custom_pages)
            st.download_button("📥 Tải về", data, "split.pdf", "application/pdf")

with tab2:
    st.subheader("PDF sang Word (Giữ nguyên bố cục)")
    file_word = st.file_uploader("Tải PDF:", type="pdf", key="word")
    if st.button("Convert to Word"):
        with open("temp.pdf", "wb") as f: f.write(file_word.getbuffer())
        cv = Converter("temp.pdf")
        cv.convert("out.docx", layout=True)
        cv.close()
        with open("out.docx", "rb") as f: st.download_button("📥 Tải Word", f, "output.docx")

with tab3:
    uploaded_scan = st.file_uploader("Tải PDF scan:", type="pdf", key="excel")
    if st.button("Convert AI to Excel"):
        with st.spinner("AI đang xử lý..."):
            df = ai_process_table(uploaded_scan)
            output = io.BytesIO()
            df.to_excel(output, index=False)
            st.download_button("📥 Tải Excel AI", output.getvalue(), "data_ai.xlsx")
