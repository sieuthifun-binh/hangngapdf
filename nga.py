import streamlit as st
import fitz  # PyMuPDF
import docx
import io
import os
import requests
import time
import base64
import pandas as pd
import google.generativeai as genai

# ==============================================================================
# --- CẤU HÌNH TRANG STREAMLIT & CUSTOM CSS (SÁAS MODERN UI) ---
# ==============================================================================
st.set_page_config(
    page_title="Pro PDF & Image AI Toolkit",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chuỗi CSS tùy chỉnh giao diện SaaS Chuyên nghiệp
CUSTOM_CSS = """
<style>
    /* 1. Đổi background & Font chữ tổng thể */
    .main {
        background-color: #f8f9fa;
    }
    
    /* 2. Tiêu đề Gradient cao cấp */
    .main-title {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 800;
        font-size: 2.5rem;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #6c757d;
        font-size: 1.05rem;
        margin-bottom: 1.8rem;
    }

    /* 3. Style Nút bấm Primary */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #4776E6 0%, #8E54E9 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(71, 118, 230, 0.25);
    }
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(71, 118, 230, 0.4);
    }

    /* 4. Tùy chỉnh Các Tab Header */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #eef2f5;
        padding: 6px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 8px;
        font-weight: 600;
        color: #495057;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #4776E6 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
</style>
"""

# Chèn CSS với tham số unsafe_allow_html=True đúng chuẩn
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==============================================================================
# --- SIDEBAR & THÔNG TIN HỆ THỐNG ---
# ==============================================================================
with st.sidebar:
    st.title("⚙️ Trạng Thái Hệ Thống")
    if "GOOGLE_API_KEY" in st.secrets:
        st.success("🟢 Gemini AI: Đã kết nối")
    else:
        st.error("🔴 Gemini AI: Chưa cấu hình Key")
        
    if "CONVERT_API_SECRET" in st.secrets:
        st.success("🟢 Cloud API: Sẵn sàng")
    else:
        st.warning("🟠 Cloud API: Dùng Chế độ Local")
        
    st.markdown("---")
    st.caption("💡 **Mẹo:** Chọn chế độ *100% Định dạng* khi muốn chuyển PDF sang Word nguyên bố cục bản in.")

# ==============================================================================
# --- TIÊU ĐỀ TRANG CHÍNH ---
# ==============================================================================
st.markdown('<div class="main-title">⚡ Pro PDF & Image AI Toolkit</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Bộ công cụ xử lý tài liệu thông minh & Trí tuệ nhân tạo Multi-Model cấp doanh nghiệp</div>', unsafe_allow_html=True)

# ==============================================================================
# --- KHỞI TẠO SESSION STATE & GEMINI AI ---
# ==============================================================================
PREFERRED_MODELS = [
    'gemini-3.8-flash',
    'gemini-2.5-flash',
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash',
    'gemini-flash'
]

if "gemini_models" not in st.session_state:
    st.session_state.gemini_models = PREFERRED_MODELS

if "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception:
        pass

# ==============================================================================
# --- CÁC TAB CHỨC NĂNG ---
# ==============================================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "✂ Tách PDF", 
    "📝 PDF sang Word & AI", 
    "📊 Trích xuất Excel", 
    "🧩 Gộp PDF", 
    "🔄 Chuyển sang PDF", 
    "🖼 AI Xóa phông"
])

# ------------------------------------------------------------------------------
# TAB 1: TÁCH PDF
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("✂️ Tách các trang từ file PDF")
    f_split = st.file_uploader("Tải file PDF cần tách:", type="pdf", key="split_pdf")
    if f_split:
        with fitz.open(stream=f_split.read(), filetype="pdf") as doc_split:
            total_pages = len(doc_split)
            st.info(f"📄 Tổng số trang trong tài liệu: **{total_pages}**")
            
            page_range = st.text_input("Nhập phạm vi trang cần tách (VD: 1-3, 5, 7-10):", value=f"1-{total_pages}")
            
            if st.button("Bắt đầu tách PDF", type="primary"):
                try:
                    out_pdf = fitz.open()
                    selected_pages = set()
                    parts = page_range.split(",")
                    for part in parts:
                        part = part.strip()
                        if "-" in part:
                            s, e = map(int, part.split("-"))
                            selected_pages.update(range(s - 1, e))
                        else:
                            selected_pages.add(int(part) - 1)
                    
                    valid_pages = sorted([p for p in selected_pages if 0 <= p < total_pages])
                    
                    if not valid_pages:
                        st.error("❌ Phạm vi trang không hợp lệ.")
                    else:
                        for p in valid_pages:
                            out_pdf.insert_pdf(doc_split, from_page=p, to_page=p)
                        
                        out_bytes = io.BytesIO()
                        out_pdf.save(out_bytes)
                        st.success(f"🎉 Đã tách thành công {len(valid_pages)} trang!")
                        st.download_button(
                            "📥 Tải về PDF đã tách",
                            out_bytes.getvalue(),
                            f"{f_split.name.rsplit('.', 1)[0]}_split.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"❌ Lỗi xử lý tách PDF: {str(e)}")

# ------------------------------------------------------------------------------
# TAB 2: PDF SANG WORD & AI TÓM TẮT
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("📝 Chuyển đổi PDF sang Word & AI Tóm tắt Chuyên sâu")
    st.caption("Tùy chọn xuất file Word giữ 100% định dạng hoặc trích xuất văn bản nhanh, kết hợp Gemini AI đa mô hình.")
    
    f_w = st.file_uploader("Tải file PDF cần xử lý:", type="pdf", key="w_ai")
    
    mode_docx = st.radio(
        "Chọn chế độ xuất file Word (.docx):",
        ["✨ Giữ nguyên 100% định dạng (Qua Cloud API)", "⚡ Trích xuất văn bản nhanh (Miễn phí local)"],
        horizontal=True
    )
    
    if st.button("🚀 Bắt đầu Chuyển đổi & Phân tích AI", type="primary", use_container_width=True):
        if f_w:
            pdf_bytes = f_w.getvalue()
            
            # --- BƯỚC 1: XUẤT FILE WORD ---
            st.markdown("### 1. File Word xuất ra")
            
            if "100%" in mode_docx:
                with st.spinner("⚡ Đang gửi file lên Cloud API để tái tạo 100% bố cục gốc..."):
                    try:
                        api_secret = st.secrets.get("CONVERT_API_SECRET", None)
                        if not api_secret:
                            st.error("❌ Chưa cấu hình CONVERT_API_SECRET trong Streamlit Secrets.")
                        else:
                            endpoint = f"https://v2.convertapi.com/convert/pdf/to/docx?Secret={api_secret}&StoreFile=true"
                            response = requests.post(
                                endpoint,
                                files={"File": (f_w.name, pdf_bytes, "application/pdf")}
                            )
                            
                            if response.status_code == 200:
                                docx_data = None
                                if 'application/octet-stream' in response.headers.get('Content-Type', '') or response.content.startswith(b'PK'):
                                    docx_data = response.content
                                else:
                                    result_json = response.json()
                                    files_list = result_json.get('Files', [])
                                    if files_list:
                                        file_info = files_list[0]
                                        file_url = file_info.get('Url') or file_info.get('url')
                                        if file_url:
                                            docx_data = requests.get(file_url).content
                                        elif 'FileData' in file_info:
                                            docx_data = base64.b64decode(file_info['FileData'])
                                
                                if docx_data:
                                    st.success("🎉 Chuyển đổi giữ nguyên 100% định dạng thành công!")
                                    st.download_button(
                                        label="📥 Tải về file Word (.docx) - Chuẩn định dạng", 
                                        data=docx_data, 
                                        file_name=f"{f_w.name.rsplit('.', 1)[0]}_formatted.docx", 
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                        use_container_width=True
                                    )
                                else:
                                    st.error("❌ Không thể trích xuất dữ liệu file từ phản hồi API.")
                            
                            elif response.status_code in [400, 401, 402, 500] and ("quota" in response.text.lower() or "limit" in response.text.lower()):
                                st.warning("⚠️ Tài khoản API đã hết lượt miễn phí! Tự động chuyển sang chế độ trích xuất nội bộ...")
                                doc_word = docx.Document()
                                with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                                    for page in doc:
                                        t = page.get_text()
                                        if t.strip(): doc_word.add_paragraph(t)
                                out_word = io.BytesIO()
                                doc
