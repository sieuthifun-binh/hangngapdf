import streamlit as st
import pikepdf
import pdfplumber
import pandas as pd
import io
import fitz  # PyMuPDF
import google.generativeai as genai
import tempfile
import os
import requests
from PIL import Image, ImageOps

# ==============================================================================
# 1. CẤU HÌNH BAN ĐẦU & CSS GIAO DIỆN 3D CAO CẤP (3D NEUMORPHIC UI)
# ==============================================================================
st.set_page_config(
    page_title="Pro PDF & AI Suite 3D", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Môi trường nền xám nhạt để làm nổi bật hiệu ứng 3D */
    .stApp {
        background-color: #EEF2F6;
    }

    /* Header Banner hiệu ứng 3D dập nổi */
    .hero-banner {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 32px 24px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 28px;
        box-shadow: 8px 8px 16px rgba(166, 180, 200, 0.7), 
                    -8px -8px 16px rgba(255, 255, 255, 0.9),
                    inset 0px 1px 1px rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .hero-banner h1 {
        font-size: 36px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin-bottom: 8px !important;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }
    .hero-banner p {
        font-size: 16px;
        color: #94A3B8;
        max-width: 650px;
        margin: 0 auto 12px auto;
    }
    .status-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(8px);
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        box-shadow: inset 0 1px 2px rgba(255,255,255,0.2);
    }

    /* ĐỊNH DẠNG TAB 3D DẬP NỔI CAO CẤP */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #EEF2F6;
        padding: 10px;
        border-radius: 16px;
        box-shadow: inset 4px 4px 8px #d1d9e6, inset -4px -4px 8px #ffffff;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        font-size: 15px !important;
        font-weight: 700 !important;
        color: #475569 !important;
        border-radius: 12px !important;
        padding: 0px 22px !important;
        background-color: #EEF2F6;
        border: none !important;
        box-shadow: 4px 4px 8px #d1d9e6, -4px -4px 8px #ffffff;
        transition: all 0.2s ease-in-out;
    }
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px);
        color: #2563EB !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(145deg, #ffffff, #e6e6e6) !important;
        color: #2563EB !important;
        box-shadow: inset 2px 2px 5px #d1d9e6, inset -2px -2px 5px #ffffff, 0px 4px 10px rgba(37, 99, 235, 0.2) !important;
        border: 1px solid rgba(37, 99, 235, 0.2) !important;
    }

    /* KHUNG NỘI DUNG 6 CHỨC NĂNG DẠNG KHỐI BO VIỀN 3D */
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #EEF2F6;
        border-radius: 24px;
        padding: 28px;
        margin-top: 20px;
        box-shadow: 9px 9px 18px #d1d9e6, -9px -9px 18px #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.6);
    }

    /* NÚT BẤM 3D (BUTTON) */
    .stButton>button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        height: 48px !important;
        background: linear-gradient(145deg, #2563EB, #1D4ED8) !important;
        color: white !important;
        border: none !important;
        box-shadow: 4px 4px 10px rgba(37, 99, 235, 0.3), -2px -2px 6px #ffffff !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 6px 6px 14px rgba(37, 99, 235, 0.4), -2px -2px 6px #ffffff !important;
    }
    .stButton>button:active {
        transform: translateY(1px);
        box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Footer Copyright */
    .footer-copyright {
        text-align: center;
        margin-top: 60px;
        padding: 24px 0;
        font-size: 13px;
        color: #64748B;
        border-top: 1px solid #CBD5E1;
    }
</style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO GOOGLE GEMINI AI ---
if 'model' not in st.session_state:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        st.session_state.model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.session_state.model = None

# ==============================================================================
# 2. THANH SIDEBAR 3D
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluent/96/pdf-2.png", width=64)
    st.title("Pro PDF Suite 3D")
    st.caption("Phiên bản Doanh nghiệp 3D v3.0")
    
    st.markdown("---")
    st.markdown("### ⚙️ Trạng thái Hệ thống")
    
    # Kiểm tra API Gemini
    if st.session_state.model:
        st.success("🟢 **Gemini AI:** Đã kết nối")
    else:
        st.warning("🟡 **Gemini AI:** Đang tắt (Thiếu API Key)")
        
    # Kiểm tra API Remove BG
    if "REMOVE_BG_API_KEY" in st.secrets:
        st.success("🟢 **Remove.bg:** Studio HD Ready")
    else:
        st.info("🔵 **Remove.bg:** Đồ họa dự phòng")
        
    st.markdown("---")
    st.markdown("### 💡 Hướng dẫn nhanh")
    st.markdown("""
    - **Cắt PDF:** Tách các trang chẵn/lẻ hoặc theo danh sách tùy chọn.
    - **Đổi sang PDF:** Tải nhiều file Word, Excel, Ảnh để gộp thành 1 PDF duy nhất.
    - **AI Tóm tắt:** Đọc tự động toàn bộ nội dung PDF và xuất ý chính.
    """)

# ==============================================================================
# 3. HEADER BANNER 3D
# ==============================================================================
st.markdown("""
<div class='hero-banner'>
    <h1>🏛️ PRO PDF & AI WORKSPACE 3D</h1>
    <p>Nền tảng xử lý tài liệu, bốc tách dữ liệu Excel và tách nền ảnh tự động với giao diện dập nổi 3D.</p>
    <div class='status-badge'>✨ Không gian làm việc 3D Neumorphic Interactive</div>
</div>
""", unsafe_allow_html=True)

# Khởi tạo 6 tab chức năng
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "✂️ Băm PDF", 
    "📝 PDF sang Word & AI", 
    "📊 AI Trích xuất Excel", 
    "🗜️ Gộp nhiều PDF", 
    "🔄 Đổi đuôi sang PDF",
    "✨ AI Tách Nền Ảnh"
])

# ==============================================================================
# --- TAB 1: BĂM PDF ---
# ==============================================================================
with tab1:
    st.subheader("✂️ Phân tách trang PDF thông minh")
    st.caption("Cắt hoặc tách các trang cụ thể từ file PDF một cách chính xác.")
    
    uploaded = st.file_uploader("Tải file PDF cần băm:", type="pdf", key="b1")
    mode = st.radio("Chế độ cắt trang:", ["Chẵn", "Lẻ", "Tùy chọn số trang"], key="m1", horizontal=True)
    
    pages = ""
    if mode == 'Tùy chọn số trang':
        pages = st.text_input("Nhập các trang cần lấy (Ví dụ: 1, 3, 5):", placeholder="Phân tách các trang bằng dấu phẩy")
    
    if st.button("Kích hoạt băm file", type="primary", use_container_width=True):
        if uploaded:
            with st.spinner("Đang xử lý tài liệu..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded.getvalue())
                        pdf = pikepdf.Pdf.open(tmp.name)
                        new_pdf = pikepdf.Pdf.new()
                        total = len(pdf.pages)
                        
                        if mode == 'Tùy chọn số trang':
                            idx = []
                            for p in pages.split(','):
                                clean_p = p.strip()
                                if clean_p.isdigit():
                                    idx.append(int(clean_p) - 1)
                        else:
                            idx = [i for i in range(total) if (i+1)%2 == (0 if mode == 'Chẵn' else 1)]
                        
                        added_pages = 0
                        for i in idx:
                            if 0 <= i < total: 
                                new_pdf.pages.append(pdf.pages[i])
                                added_pages += 1
                        
                        if added_pages > 0:
                            out = io.BytesIO()
                            new_pdf.save(out)
                            st.success(f"🎉 Trích xuất thành công {added_pages}/{total} trang.")
                            st.download_button("📥 Tải về file PDF đã cắt", out.getvalue(), "split_pages.pdf", mime="application/pdf", use_container_width=True)
                        else:
                            st.error("❌ Không có trang hợp lệ nào được tìm thấy.")
                        
                        pdf.close()
                        os.remove(tmp.name)
                except Exception as e:
                    st.error(f"⚠️ Lỗi xử lý: {str(e)}")
        else:
            st.warning("Vui lòng tải file PDF lên hệ thống trước.")

# ==============================================================================
# --- TAB 2: PDF SANG WORD & AI TÓM TẮT ---
# ==============================================================================
with tab2:
    st.subheader("📝 Chuyển đổi PDF sang Word kết hợp AI Tóm tắt")
    st.caption("Trích xuất văn bản PDF sang file Word (.docx) và sử dụng Gemini AI để cô đọng nội dung.")
    
    f_w = st.file_uploader("Tải file PDF cần chuyển đổi & tóm tắt:", type="pdf", key="w_ai")
    
    if st.button("Bắt đầu chuyển đổi & Phân tích AI", type="primary", use_container_width=True):
        if f_w:
            with st.spinner("⚡ Bước 1: Đang trích xuất nội dung sang file Word (.docx)..."):
                try:
                    import docx
                    
                    # Đọc văn bản từ PDF bằng PyMuPDF
                    doc_text = ""
                    doc_word = docx.Document()
                    
                    with fitz.open(stream=f_w.read(), filetype="pdf") as doc:
                        for page_idx, page in enumerate(doc):
                            text = page.get_text()
                            doc_text += " " + text
                            
                            # Ghi vào file Word
                            doc_word.add_heading(f"Trang {page_idx + 1}", level=2)
                            doc_word.add_paragraph(text if text.strip() else "[Trang không chứa văn bản kỹ thuật số]")
                    
                    # Xuất file Word ra bộ nhớ RAM
                    out_word = io.BytesIO()
                    doc_word.save(out_word)
                    word_bytes = out_word.getvalue()
                    
                    st.success("🎉 Đã chuyển đổi nội dung sang Word hoàn tất!")
                    st.download_button(
                        "📥 Tải về file Word (.docx)", 
                        word_bytes, 
                        f"{f_w.name.rsplit('.', 1)[0]}.docx", 
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                    
                    st.markdown("---")
                    st.subheader("🤖 Trí tuệ nhân tạo Phân tích sâu")
                    
                    if len(doc_text.strip()) < 15:
                        st.warning("⚠ Tài liệu không chứa dữ liệu văn bản kỹ thuật số.")
                    else:
                        if st.session_state.model is None:
                            st.error("❌ Chưa cấu hình GOOGLE_API_KEY trong Secrets.")
                        else:
                            with st.spinner("AI đang đọc toàn văn và cô đọng nội dung..."):
                                prompt = f"Bạn là một chuyên gia phân tích tài liệu cao cấp. Hãy đọc toàn bộ văn bản dưới đây và tóm tắt thành các luận điểm, ý chính cốt lõi một cách khoa học, chuyên nghiệp bằng Tiếng Việt:\n\n{doc_text[:100000]}"
                                res = st.session_state.model.generate_content(prompt)
                                st.info(f"💡 **BẢN TÓM TẮT TỪ AI:**\n\n{res.text}")
                except Exception as e:
                    st.error(f"❌ Lỗi hệ thống: {str(e)}")
        else:
            st.warning("Vui lòng cung cấp file PDF nguồn.")

# ==============================================================================
# --- TAB 3: AI PDF SANG EXCEL ---
# ==============================================================================
with tab3:
    st.subheader("📊 Trích xuất bảng biểu dữ liệu từ PDF sang Excel")
    st.caption("Quét ma trận cột/dòng để bốc tách bảng tính từ PDF sang file Excel.")
    
    f_e = st.file_uploader("Tải file PDF chứa bảng dữ liệu:", type="pdf", key="e1")
    
    if st.button("Kích hoạt bốc tách dữ liệu Excel", type="primary", use_container_width=True):
        if f_e:
            with st.spinner("Đang quét và bốc tách cấu trúc ma trận bảng..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(f_e.getvalue())
                        
                        all_table_data = []
                        header = None
                        
                        with pdfplumber.open(tmp.name) as pdf:
                            for page in pdf.pages:
                                table = page.extract_table()
                                if table:
                                    if not all_table_data:
                                        header = table[0]
                                        all_table_data.extend(table[1:])
                                    else:
                                        all_table_data.extend(table[1:])
                        
                        if all_table_data and header:
                            df = pd.DataFrame(all_table_data, columns=header)
                            out = io.BytesIO()
                            with pd.ExcelWriter(out, engine='openpyxl') as writer:
                                df.to_excel(writer, index=False, sheet_name="AI_Extracted")
                            
                            st.success(f"🎉 Bốc tách dữ liệu bảng thành công!")
                            st.dataframe(df.head(20), use_container_width=True)
                            st.download_button("📥 Tải về file Excel (.xlsx)", out.getvalue(), "extracted_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                        else:
                            st.error("❌ Không tìm thấy bảng biểu hợp lệ nào trong tài liệu.")
                        
                        os.remove(tmp.name)
                except Exception as e:
                    st.error(f"⚠️ Lỗi trích xuất: {str(e)}")
        else:
            st.warning("Vui lòng tải lên file PDF chứa bảng tính.")

# ==============================================================================
# --- TAB 4: GỘP NHIỀU FILE PDF ---
# ==============================================================================
with tab4:
    st.subheader("🗜️ Hợp nhất (Merge) nhiều file PDF")
    st.caption("Nối hàng loạt các tập tin PDF riêng lẻ thành một file hoàn chỉnh.")
    
    uploaded_merge_files = st.file_uploader("Chọn danh sách file PDF cần gộp:", type="pdf", accept_multiple_files=True, key="merge_files")
    
    if st.button("Bắt đầu tiến trình gộp file", type="primary", disabled=(not uploaded_merge_files), use_container_width=True):
        with st.spinner("Hệ thống đang hợp nhất tài liệu..."):
            try:
                merged_pdf = pikepdf.Pdf.new()
                count_files = 0
                total_pages_merged = 0
                
                for uploaded_f in uploaded_merge_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_f.getvalue())
                        src_pdf = pikepdf.Pdf.open(tmp.name)
                        for page in src_pdf.pages:
                            merged_pdf.pages.append(page)
                            total_pages_merged += 1
                        count_files += 1
                        src_pdf.close()
                        os.remove(tmp.name)
                
                if total_pages_merged > 0:
                    out_merge = io.BytesIO()
                    merged_pdf.save(out_merge)
                    st.success(f"🎉 Đã gộp {count_files} file thành 1 tài liệu ({total_pages_merged} trang).")
                    st.download_button("📥 Tải về file PDF Tổng Hợp", out_merge.getvalue(), "merged_document.pdf", mime="application/pdf", use_container_width=True)
                merged_pdf.close()
            except Exception as e:
                st.error(f"❌ Lỗi gộp file: {str(e)}")

# ==============================================================================
# --- TAB 5: CHUYỂN ĐỔI ĐA NĂNG SANG PDF ---
# ==============================================================================
with tab5:
    st.subheader("🔄 Bộ chuyển đổi định dạng đa năng sang PDF")
    st.caption("Hỗ trợ tải lên nhiều file (Word, Excel, PNG, JPG) cùng lúc để tạo thành 1 file PDF hoàn chỉnh.")
    
    files_convert = st.file_uploader(
        "Tải lên các file nguồn (Word, Excel, Ảnh):", 
        type=["docx", "xlsx", "png", "jpg", "jpeg"], 
        accept_multiple_files=True,
        key="conv_source_multi"
    )
    
    if st.button("Chuyển đổi & Ghép thành 1 PDF hoàn chỉnh", type="primary", disabled=(not files_convert), use_container_width=True):
        with st.spinner("Đang chuyển đổi và đóng gói tất cả file vào 1 bản PDF..."):
            try:
                final_pdf_doc = fitz.open()
                processed_count = 0
                
                for f_convert in files_convert:
                    f_name = f_convert.name
                    ext = f_name.split('.')[-1].lower()
                    
                    # Xử lý file Ảnh
                    if ext in ["png", "jpg", "jpeg"]:
                        image = Image.open(f_convert)
                        if image.mode in ("RGBA", "P"): 
                            image = image.convert("RGB")
                        
                        img_bytes = io.BytesIO()
                        image.save(img_bytes, format="PDF")
                        img_pdf = fitz.open("pdf", img_bytes.getvalue())
                        final_pdf_doc.insert_pdf(img_pdf)
                        img_pdf.close()
                        processed_count += 1
                    
                    # Xử lý file Excel
                    elif ext == "xlsx":
                        df_excel = pd.read_excel(f_convert)
                        page = final_pdf_doc.new_page()
                        string_data = df_excel.to_string()
                        page.insert_text((40, 40), f"TÀI LIỆU KẾT XUẤT TỪ FILE EXCEL: {f_name}\n\n" + string_data, fontsize=10)
                        processed_count += 1
                    
                    # Xử lý file Word
                    elif ext == "docx":
                        import docx
                        doc_word = docx.Document(f_convert)
                        page = final_pdf_doc.new_page()
                        text_lines = [f"TÀI LIỆU KẾT XUẤT TỪ VĂN BẢN WORD: {f_name}\n"]
                        for p in doc_word.paragraphs:
                            if p.text.strip(): 
                                text_lines.append(p.text)
                        page.insert_text((50, 50), "\n".join(text_lines), fontsize=12)
                        processed_count += 1

                if len(final_pdf_doc) > 0:
                    pdf_out = io.BytesIO()
                    final_pdf_doc.save(pdf_out)
                    final_pdf_doc.close()
                    
                    st.success(f"🎉 Đã chuyển đổi thành công {processed_count} file thành 1 tài liệu PDF!")
                    st.download_button(
                        "📥 Tải về file PDF Hoàn Chỉnh", 
                        pdf_out.getvalue(), 
                        "converted_combined.pdf", 
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Không có file hợp lệ nào được chuyển đổi.")
                    
            except Exception as e:
                st.error(f"❌ Phát sinh lỗi: {str(e)}")

# ==============================================================================
# --- TAB 6: AI XÓA VÀ ĐỔI NỀN ẢNH ---
# ==============================================================================
with tab6:
    st.subheader("✨ AI Tách & Đổi Nền Ảnh Studio (Remove BG Pro)")
    st.caption("Công nghệ bóc tách dữ liệu Raw Bytes nguyên bản - Cách ly tên file gốc để triệt tiêu lỗi mã hóa hệ thống.")
    
    col_config, col_display = st.columns([1, 2], gap="large")
    
    with col_config:
        st.markdown("##### 🛠️ Cài đặt bộ lọc")
        img_file_raw = st.file_uploader("Tải ảnh nguồn lên:", type=["png", "jpg", "jpeg", "webp"], key="bg_uploader_raw_bytes_v6")
        
        bg_mode = st.selectbox(
            "🎨 Chọn kiểu nền mới:",
            ["Trong suốt (Transparent)", "Nền màu đơn sắc (Solid Color)"],
            key="bg_mode_v6"
        )
        
        bg_color = "#FFFFFF"
        if bg_mode == "Nền màu đơn sắc (Solid Color)":
            bg_color = st.color_picker("Chọn màu nền mong muốn:", "#FFFFFF", key="bg_col_v6")
            
        has_api = "REMOVE_BG_API_KEY" in st.secrets

    with col_display:
        if img_file_raw is not None:
            c1, c2 = st.columns(2, gap="medium")
            
            image_pure_bytes = img_file_raw.getvalue()
            image_mime_type = img_file_raw.type
            
            with c1:
                st.markdown("🔹 **Ảnh gốc:**")
                original_image = Image.open(io.BytesIO(image_pure_bytes))
                st.image(original_image, use_container_width=True)
                
            with c2:
                st.markdown("✨ **Kết quả xử lý:**")
                
                if st.button("🪄 TIẾN HÀNH XỬ LÝ ẢNH", type="primary", use_container_width=True, key="btn_run_v6"):
                    with st.spinner("Đang tách nền điểm ảnh..."):
                        try:
                            final_bytes = None
                            result_image = None
                            
                            # 1. AI API Cloud
                            if has_api:
                                response = requests.post(
                                    'https://api.remove.bg/v1.0/removebg',
                                    files={'image_file': ('image_file.png', image_pure_bytes, image_mime_type)},
                                    data={'size': 'auto'},
                                    headers={'X-Api-Key': st.secrets["REMOVE_BG_API_KEY"]},
                                )
                                if response.status_code == 200:
                                    result_image = Image.open(io.BytesIO(response.content))
                                else:
                                    st.warning("⚠️ API bận. Tự động chuyển sang Đồ họa dự phòng.")
                            
                            # 2. Engine đồ họa dự phòng
                            if result_image is None:
                                img = Image.open(io.BytesIO(image_pure_bytes)).convert("RGBA")
                                datas = img.getdata()
                                new_data = []
                                for item in datas:
                                    if item[0] > 220 and item[1] > 220 and item[2] > 220:
                                        new_data.append((255, 255, 255, 0))
                                    else:
                                        new_data.append(item)
                                img.putdata(new_data)
                                result_image = img

                            # 3. Đổ màu nền mới
                            if bg_mode == "Nền màu đơn sắc (Solid Color)":
                                hex_str = bg_color.lstrip('#')
                                rgb_tuple = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
                                background = Image.new("RGBA", result_image.size, rgb_tuple + (255,))
                                background.paste(result_image, (0, 0), result_image)
                                result_image = background
                            
                            # 4. Xuất kết quả RAM
                            buffer = io.BytesIO()
                            result_image.save(buffer, format="PNG")
                            final_bytes = buffer.getvalue()
                            
                            st.image(result_image, use_container_width=True)
                            st.success("🎉 Tách nền hoàn tất!")
                            
                            st.download_button(
                                label="📥 Tải ảnh kết quả (.PNG)",
                                data=final_bytes,
                                file_name="ai_studio_output.png",
                                mime="image/png",
                                use_container_width=True,
                                key="btn_download_v6"
                            )
                        except Exception as e:
                            st.error(f"❌ Lỗi xử lý ảnh: {str(e)}")
        else:
            st.info("📌 Vui lòng chọn và tải ảnh lên ở cột cấu hình bên trái để bắt đầu.")

# ==============================================================================
# --- DÒNG BẢN QUYỀN (COPYRIGHT) FOOTER ---
# ==============================================================================
st.markdown(
    """
    <div class="footer-copyright">
        © 2026 Pro PDF & AI Suite 3D. All rights reserved. Powered by Streamlit & AI Cloud Services.
    </div>
    """, 
    unsafe_allow_html=True
)
