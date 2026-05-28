import streamlit as st
import pikepdf
import fitz
import io
import pandas as pd
import json
import google.generativeai as genai
from pdf2docx import Converter # Thêm thư viện này để làm Word

# Cấu hình API
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Chưa cấu hình GOOGLE_API_KEY trong Secrets!")

st.set_page_config(page_title="PDF Pro Toolkit", layout="wide")
st.title("🚀 PDF Pro Toolkit - Bản Hoàn Chỉnh")

# --- HÀM XỬ LÝ ---
def split_pdf(input_stream, pages_list):
    pdf = pikepdf.Pdf.open(input_stream)
    new_pdf = pikepdf.Pdf.new()
    for p in pages_list:
        if 0 <= p < len(pdf.pages):
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
        "Hãy trích xuất bảng trong ảnh này thành định dạng JSON chuẩn.",
        {"mime_type": "image/png", "data": img_data}
    ])
    raw_text = response.text.replace("```json", "").replace("```", "")
    return pd.DataFrame(json.loads(raw_text))

# --- GIAO DIỆN CHÍNH ---
tab1, tab2, tab3 = st.tabs(["✂️ Băm PDF", "📝 PDF sang Word", "📊 PDF sang Excel (AI)"])

with tab1:
    uploaded = st.file_uploader("Tải PDF:", type="pdf", key="băm")
    pages_input = st.text_input("Số trang (VD: 0, 2):")
    if st.button("Băm"):
        pages = [int(p.strip()) for p in pages_input.split(',')]
        data = split_pdf(uploaded, pages)
        st.download_button("📥 Tải về", data, "split.pdf", "application/pdf")

with tab2:
    st.subheader("PDF sang Word (Giữ nguyên bố cục)")
    file_word = st.file_uploader("Tải PDF:", type="pdf", key="word")
    if st.button("Convert to Word"):
        with open("temp.pdf", "wb") as f: f.write(file_word.getbuffer())
        cv = Converter("temp.pdf")
        cv.convert("out.docx", layout=True) # layout=True giữ định dạng gốc
        cv.close()
        with open("out.docx", "rb") as f: st.download_button("📥 Tải Word", f, "output.docx")

with tab3:
    uploaded_scan = st.file_uploader("Tải PDF scan:", type="pdf", key="excel")
    if st.button("Convert AI to Excel"):
        df = ai_process_table(uploaded_scan)
        output = io.BytesIO()
        df.to_excel(output, index=False)
        st.download_button("📥 Tải Excel AI", output.getvalue(), "data_ai.xlsx")
