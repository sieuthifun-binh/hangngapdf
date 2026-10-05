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
# --- CẤU HÌNH TRANG STREAMLIT & CUSTOM CSS ---
# ==============================================================================
st.set_page_config(
    page_title="Pro PDF & Image AI Toolkit",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Thêm CSS tùy chỉnh cho giao diện Modern SaaS
CUSTOM_CSS = """
<style>
    /* 1. Đổi font chữ & background tổng thể */
    .main {
        background-color: #f8f9fa;
    }
    
    /* 2. Style cho Tiêu đề chính Gradient */
    .main-title {
        font-family: 'Inter', sans-serif;
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

    /* 3. Style Thẻ Card chứa nội dung */
    .css-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
    }

    /* 4. Tùy chỉnh Nút bấm Primary */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #4776E6 0%, #8E54E9 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(71, 118, 230, 0.3);
    }
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(71, 118, 230, 0.4);
    }

    /* 5. Tùy chỉnh Các Tab Header */
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

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==============================================================================
# --- SIDEBAR & TIÊU ĐỀ ---
# ==============================================================================
with st.sidebar:
    st.title("⚙️ Hệ thống")
    if "GOOGLE_API_KEY" in st.secrets:
        st.success("🟢 Gemini AI: Đã kết nối")
    else:
        st.error("🔴 Gemini AI: Chưa cấu hình Key")
        
    if "CONVERT_API_SECRET" in st.secrets:
        st.success("🟢 Cloud API: Sẵn sàng")
    else:
        st.warning("🟠 Cloud API: Dùng Chế độ Local")

st.markdown('<div class="main-title">⚡ Pro PDF & Image AI Toolkit</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Bộ công cụ xử lý tài liệu thông minh & Trí tuệ nhân tạo Multi-Model cấp doanh nghiệp</div>', unsafe_allow_html=True)

# ==============================================================================
# --- KHỞI TẠO DỮ LIỆU SESSION STATE & GEMINI AI ---
# ==============================================================================
# Danh sách mô hình Gemini theo thứ tự ưu tiên
PREFERRED_MODELS = [
    'gemini-3.8-flash',
    'gemini-2.5-flash',
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash',
    'gemini-flash'
]

if "gemini_models" not in st.session_state:
    st.session_state.gemini_models = PREFERRED_MODELS

# Cấu hình API Key nếu có trong Secrets
if "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception:
        pass

# ==============================================================================
# --- TIEU DE VA GIAO DIEN CHINH ---
# ==============================================================================
st.markdown('<div class="main-title">⚡ Pro PDF & Image AI Toolkit</div>', unsafe_style_text=True)
st.markdown('<div class="sub-title">Bộ công cụ xử lý tài liệu thông minh & Trí tuệ nhân tạo Multi-Model cấp doanh nghiệp</div>', unsafe_style_text=True)

# Khởi tạo các Tab chức năng
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "✂️️ Tách PDF", 
    "📝 PDF sang Word & AI", 
    "📊 Trích xuất Excel", 
    "🧩 Gộp PDF", 
    "🔄 Chuyển sang PDF", 
    "🖼️️ AI Xóa phông"
])

# ==============================================================================
# --- TAB 1: TÁCH PDF ---
# ==============================================================================
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
                    # Phân tích chuỗi phạm vi trang
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

# ==============================================================================
# --- TAB 2: PDF SANG WORD & AI TÓM TẮT (MULTI-MODEL + CLOUD API) ---
# ==============================================================================
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
            
            # CHẾ ĐỘ 1: DÙNG CLOUD CONVERTAPI (GIỮ 100% BỐ CỤC)
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
                                # Kiểm tra dạng Binary Stream
                                if 'application/octet-stream' in response.headers.get('Content-Type', '') or response.content.startswith(b'PK'):
                                    docx_data = response.content
                                else:
                                    # Phân tích cấu trúc JSON
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
                                doc_word.save(out_word)
                                st.download_button(
                                    label="📥 Tải file Word (Văn bản thuần)", 
                                    data=out_word.getvalue(), 
                                    file_name=f"{f_w.name.rsplit('.', 1)[0]}_text.docx", 
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    use_container_width=True
                                )
                            else:
                                st.error(f"❌ Lỗi API Convert ({response.status_code}): {response.text}")
                    except Exception as e:
                        st.error(f"❌ Lỗi xử lý Cloud API: {str(e)}")

            # CHẾ ĐỘ 2: DÙNG LOCAL PYTHON (MIỄN PHÍ & SIÊU NHANH)
            else:
                with st.spinner("⚡ Đang trích xuất văn bản bằng thư viện nội bộ..."):
                    try:
                        doc_word = docx.Document()
                        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                            for i, page in enumerate(doc):
                                doc_word.add_heading(f"Trang {i+1}", level=2)
                                text = page.get_text()
                                doc_word.add_paragraph(text if text.strip() else "[Trang không có chữ kỹ thuật số]")
                        
                        out_word = io.BytesIO()
                        doc_word.save(out_word)
                        st.success("🎉 Trích xuất văn bản Word hoàn tất!")
                        st.download_button(
                            label="📥 Tải về file Word (.docx) - Dạng văn bản", 
                            data=out_word.getvalue(), 
                            file_name=f"{f_w.name.rsplit('.', 1)[0]}_text.docx", 
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"❌ Lỗi trích xuất Local: {str(e)}")

            # --- BƯỚC 2: AI TÓM TẮT VĂN BẢN (MULTI-MODEL FALLBACK + AUTO RETRY) ---
            st.markdown("---")
            st.markdown("### 2. 🤖 Trí tuệ nhân tạo Phân tích & Tóm tắt Multi-Model")
            
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                full_text = " ".join([page.get_text() for page in doc])
            
            if len(full_text.strip()) < 15:
                st.warning("⚠ Tài liệu không chứa đủ dữ liệu chữ dạng kỹ thuật số để AI đọc.")
            else:
                has_api_key = "GOOGLE_API_KEY" in st.secrets
                if not has_api_key:
                    st.error("❌ Chưa cấu hình GOOGLE_API_KEY trong Streamlit Secrets.")
                else:
                    with st.spinner("AI đang nghiên cứu toàn bộ văn bản và viết bản tóm tắt..."):
                        prompt = f"Bạn là một chuyên gia phân tích tài liệu cao cấp. Hãy đọc toàn bộ văn bản sau và tóm tắt thành các ý chính cốt lõi bằng Tiếng Việt:\n\n{full_text[:100000]}"
                        
                        ai_success = False
                        last_error_msg = ""
                        models_to_try = st.session_state.get("gemini_models", PREFERRED_MODELS)
                        
                        # Duyệt lần lượt qua các mô hình (3.8 -> 2.5 -> 1.5)
                        for model_name in models_to_try:
                            try:
                                model_obj = genai.GenerativeModel(model_name)
                                max_attempts = 2
                                
                                for attempt in range(max_attempts):
                                    try:
                                        res = model_obj.generate_content(prompt)
                                        st.info(f"💡 **BẢN TÓM TẮT TỪ AI (Mô hình: `{model_name}`):**\n\n{res.text}")
                                        ai_success = True
                                        break
                                    except Exception as rate_err:
                                        err_txt = str(rate_err).lower()
                                        if ("429" in err_txt or "quota" in err_txt or "resourceexhausted" in err_txt) and attempt < max_attempts - 1:
                                            time.sleep(3)  # Đợi 3s nếu chạm hạn mức 5req/min
                                            continue
                                        else:
                                            raise rate_err
                                if ai_success:
                                    break
                            except Exception as m_err:
                                last_error_msg = str(m_err)
                                continue  # Chuyển sang mô hình tiếp theo trong danh sách
                        
                        if not ai_success:
                            if "quota" in last_error_msg.lower() or "429" in last_error_msg:
                                st.warning("⚠️ Tất cả mô hình Gemini đều đang chạm giới hạn 5 yêu cầu/phút của gói Free. Vui lòng đợi 30 giây rồi bấm thử lại!")
                            else:
                                st.error(f"❌ Lỗi xử lý AI: {last_error_msg}")
        else:
            st.warning("Vui lòng tải file PDF lên hệ thống.")

# ==============================================================================
# --- TAB 3: TRÍCH XUẤT EXCEL ---
# ==============================================================================
with tab3:
    st.subheader("📊 Trích xuất bảng biểu từ PDF sang Excel")
    f_excel = st.file_uploader("Tải file PDF chứa bảng biểu:", type="pdf", key="excel_pdf")
    if f_excel:
        if st.button("Bắt đầu trích xuất bảng", type="primary"):
            try:
                import pdfplumber
                all_tables = []
                with pdfplumber.open(f_excel) as pdf:
                    for i, page in enumerate(pdf.pages):
                        tables = page.extract_tables()
                        for table in tables:
                            df = pd.DataFrame(table[1:], columns=table[0])
                            all_tables.append(df)
                
                if all_tables:
                    out_excel = io.BytesIO()
                    with pd.ExcelWriter(out_excel, engine='openpyxl') as writer:
                        for idx, df_table in enumerate(all_tables):
                            df_table.to_excel(writer, sheet_name=f"Table_{idx+1}", index=False)
                    
                    st.success(f"🎉 Đã tìm thấy và trích xuất thành công {len(all_tables)} bảng biểu!")
                    st.download_button(
                        "📥 Tải về file Excel (.xlsx)",
                        out_excel.getvalue(),
                        f"{f_excel.name.rsplit('.', 1)[0]}_tables.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("⚠ Không tìm thấy cấu trúc bảng rõ ràng trong tài liệu PDF này.")
            except Exception as e:
                st.error(f"❌ Lỗi trích xuất bảng: {str(e)}")

# ==============================================================================
# --- TAB 4: GỘP PDF ---
# ==============================================================================
with tab4:
    st.subheader("🧩 Gộp nhiều file PDF thành 1 file duy nhất")
    files_merge = st.file_uploader("Tải lên danh sách các file PDF:", type="pdf", accept_multiple_files=True, key="merge_pdfs")
    if files_merge:
        if st.button("Bắt đầu gộp các file PDF", type="primary"):
            try:
                merged_pdf = fitz.open()
                for file in files_merge:
                    with fitz.open(stream=file.read(), filetype="pdf") as doc:
                        merged_pdf.insert_pdf(doc)
                
                out_bytes = io.BytesIO()
                merged_pdf.save(out_bytes)
                st.success(f"🎉 Đã gộp thành công {len(files_merge)} file PDF!")
                st.download_button(
                    "📥 Tải về file PDF đã gộp",
                    out_bytes.getvalue(),
                    "merged_document.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"❌ Lỗi trong quá trình gộp PDF: {str(e)}")

# ==============================================================================
# --- TAB 5: CHUYỂN SANG PDF ---
# ==============================================================================
with tab5:
    st.subheader("🔄 Chuyển đổi Hình ảnh (PNG/JPG) sang PDF")
    imgs_input = st.file_uploader("Tải lên các file hình ảnh:", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="imgs_pdf")
    if imgs_input:
        if st.button("Chuyển đổi thành PDF", type="primary"):
            try:
                from PIL import Image
                image_list = []
                for img_file in imgs_input:
                    img = Image.open(img_file).convert('RGB')
                    image_list.append(img)
                
                if image_list:
                    out_pdf = io.BytesIO()
                    image_list[0].save(out_pdf, format="PDF", save_all=True, append_images=image_list[1:])
                    st.success("🎉 Đã chuyển đổi hình ảnh sang PDF thành công!")
                    st.download_button(
                        "📥 Tải về file PDF",
                        out_pdf.getvalue(),
                        "converted_images.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"❌ Lỗi chuyển đổi hình ảnh: {str(e)}")

# ==============================================================================
# --- TAB 6: AI XÓA PHÔNG ---
# ==============================================================================
with tab6:
    st.subheader("🖼️ Trí tuệ nhân tạo Xóa phông hình ảnh")
    st.caption("Trích xuất chủ thể và loại bỏ nền hình ảnh tự động.")
    f_bg = st.file_uploader("Tải ảnh cần xóa phông (PNG, JPG):", type=["png", "jpg", "jpeg"], key="bg_img")
    if f_bg:
        st.image(f_bg, caption="Ảnh gốc tải lên", use_container_width=True)
        if st.button("Bắt đầu xóa phông nền", type="primary"):
            st.info("💡 Tính năng xóa phông nâng cao đang kết nối module xử lý. Vui lòng đảm bảo cấu hình dịch vụ AI background removal!")
