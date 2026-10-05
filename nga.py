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
from PIL import Image, ImageOps, ImageEnhance

try:
    from streamlit_cropper import st_cropper
except ImportError:
    st_cropper = None

# ==============================================================================
# 1. CẤU HÌNH BAN ĐẦU & CSS GIAO DIỆN 3D NEUMORPHIC UI
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

    .stApp {
        background-color: #EEF2F6;
    }

    /* Hero Banner 3D */
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

    /* Tab 3D Neumorphism */
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

    /* Khung viền 3D Container */
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #EEF2F6;
        border-radius: 24px;
        padding: 28px;
        margin-top: 20px;
        box-shadow: 9px 9px 18px #d1d9e6, -9px -9px 18px #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.6);
    }

    /* Nút bấm 3D */
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

# Khởi tạo Gemini AI
if 'model' not in st.session_state:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        st.session_state.model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.session_state.model = None

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluent/96/pdf-2.png", width=64)
    st.title("Pro PDF Suite 3D")
    st.caption("Phiên bản Bền Vững Stable v4.0")
    st.markdown("---")
    st.markdown("### ⚙️ Trạng thái Hệ thống")
    if st.session_state.model:
        st.success("🟢 **Gemini AI:** Đã kết nối")
    else:
        st.warning("🟡 **Gemini AI:** Đang tắt (Thiếu API Key)")
    if "REMOVE_BG_API_KEY" in st.secrets:
        st.success("🟢 **Remove.bg:** Studio HD Ready")
    else:
        st.info("🔵 **Remove.bg:** Đồ họa dự phòng")

# Banner
st.markdown("""
<div class='hero-banner'>
    <h1>🏛️ PRO PDF & AI WORKSPACE 3D</h1>
    <p>Hệ thống xử lý tài liệu, biên tập hình ảnh trực quan và trích xuất dữ liệu AI tối ưu hóa.</p>
    <div class='status-badge'>✨ Môi trường vận hành 3D ổn định tuyệt đối</div>
</div>
""", unsafe_allow_html=True)

# Khởi tạo 6 Tab
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "✂️ Băm PDF", 
    "📝 AI Tóm Tắt PDF", 
    "📊 AI Trích xuất Excel", 
    "🗜️ Gộp nhiều PDF", 
    "🔄 Đổi đuôi sang PDF",
    "✨ AI Tách Nền Ảnh"
])

# ==============================================================================
# TAB 1: BĂM PDF
# ==============================================================================
with tab1:
    st.subheader("✂️ Phân tách trang PDF thông minh")
    uploaded = st.file_uploader("Tải file PDF cần băm:", type="pdf", key="b1")
    mode = st.radio("Chế độ cắt trang:", ["Chẵn", "Lẻ", "Tùy chọn số trang"], key="m1", horizontal=True)
    pages = ""
    if mode == 'Tùy chọn số trang':
        pages = st.text_input("Nhập các trang cần lấy (Ví dụ: 1, 3, 5):", placeholder="Ví dụ: 1, 3, 5")
    
    if st.button("Kích hoạt băm file", type="primary", use_container_width=True):
        if uploaded:
            with st.spinner("Đang xử lý..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded.getvalue())
                        pdf = pikepdf.Pdf.open(tmp.name)
                        new_pdf = pikepdf.Pdf.new()
                        total = len(pdf.pages)
                        
                        if mode == 'Tùy chọn số trang':
                            idx = [int(p.strip()) - 1 for p in pages.split(',') if p.strip().isdigit()]
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
                            st.success(f"🎉 Đã trích xuất thành công {added_pages}/{total} trang.")
                            st.download_button("📥 Tải về file PDF đã cắt", out.getvalue(), "split_pages.pdf", mime="application/pdf", use_container_width=True)
                        else:
                            st.error("❌ Không tìm thấy trang hợp lệ.")
                        pdf.close()
                        os.remove(tmp.name)
                except Exception as e:
                    st.error(f"⚠️ Lỗi: {str(e)}")
        else:
            st.warning("Vui lòng tải file PDF lên.")

# ==============================================================================
# TAB 2: AI TÓM TẮT PDF
# ==============================================================================
with tab2:
    st.subheader("📝 Phân tích & AI Tóm tắt nội dung PDF")
    f_w = st.file_uploader("Tải file PDF cần đọc tóm tắt:", type="pdf", key="w_ai")
    
    if st.button("Bắt đầu Phân tích AI", type="primary", use_container_width=True):
        if f_w:
            with st.spinner("AI đang trích xuất dữ liệu văn bản..."):
                try:
                    doc_text = ""
                    with fitz.open(stream=f_w.read(), filetype="pdf") as doc:
                        for page in doc: 
                            doc_text += " " + page.get_text()
                    
                    if len(doc_text.strip()) < 15:
                        st.warning("⚠ Tài liệu không chứa lớp dữ liệu văn bản kỹ thuật số.")
                    else:
                        if st.session_state.model is None:
                            st.error("❌ Chưa cấu hình GOOGLE_API_KEY trong Secrets.")
                        else:
                            with st.spinner("Gemini AI đang phân tích luận điểm..."):
                                prompt = f"Hãy đọc toàn bộ văn bản dưới đây và tóm tắt thành các ý chính cốt lõi bằng Tiếng Việt một cách chuyên nghiệp:\n\n{doc_text[:100000]}"
                                res = st.session_state.model.generate_content(prompt)
                                st.info(f"💡 **BẢN TÓM TẮT AI:**\n\n{res.text}")
                except Exception as e:
                    st.error(f"❌ Lỗi: {str(e)}")
        else:
            st.warning("Vui lòng tải file PDF lên.")

# ==============================================================================
# TAB 3: AI PDF SANG EXCEL
# ==============================================================================
with tab3:
    st.subheader("📊 Trích xuất bảng dữ liệu từ PDF sang Excel")
    f_e = st.file_uploader("Tải file PDF chứa bảng:", type="pdf", key="e1")
    
    if st.button("Bốc tách dữ liệu Excel", type="primary", use_container_width=True):
        if f_e:
            with st.spinner("Đang quét cấu trúc bảng..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(f_e.getvalue())
                        all_table_data, header = [], None
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
                                df.to_excel(writer, index=False, sheet_name="Extracted")
                            st.success("🎉 Trích xuất bảng thành công!")
                            st.dataframe(df.head(15), use_container_width=True)
                            st.download_button("📥 Tải về file Excel (.xlsx)", out.getvalue(), "extracted.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                        else:
                            st.error("❌ Không tìm thấy bảng biểu trong tài liệu.")
                        os.remove(tmp.name)
                except Exception as e:
                    st.error(f"⚠️ Lỗi: {str(e)}")
        else:
            st.warning("Vui lòng tải file PDF lên.")

# ==============================================================================
# TAB 4: GỘP NHIỀU FILE PDF
# ==============================================================================
with tab4:
    st.subheader("🗜️ Hợp nhất nhiều file PDF")
    uploaded_merge_files = st.file_uploader("Chọn các file PDF cần gộp:", type="pdf", accept_multiple_files=True, key="merge_files")
    
    if st.button("Tiến hành gộp file", type="primary", disabled=(not uploaded_merge_files), use_container_width=True):
        with st.spinner("Đang hợp nhất các file..."):
            try:
                merged_pdf = pikepdf.Pdf.new()
                for uploaded_f in uploaded_merge_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_f.getvalue())
                        src_pdf = pikepdf.Pdf.open(tmp.name)
                        merged_pdf.pages.extend(src_pdf.pages)
                        src_pdf.close()
                        os.remove(tmp.name)
                
                out_merge = io.BytesIO()
                merged_pdf.save(out_merge)
                st.success("🎉 Đã gộp thành công tất cả file PDF!")
                st.download_button("📥 Tải về file PDF Tổng Hợp", out_merge.getvalue(), "merged.pdf", mime="application/pdf", use_container_width=True)
                merged_pdf.close()
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")

# ==============================================================================
# TAB 5: ĐỔI ĐUÔI SANG PDF (CÓ XEM TRƯỚC 30% & CHỈNH SỬA ẢNH TRỰC QUAN)
# ==============================================================================
with tab5:
    st.subheader("🔄 Chuyển đổi định dạng đa năng sang PDF")
    st.caption("Xem trước thu nhỏ 30%, co dãn, xoay góc và chỉnh màu sắc/ánh sáng ảnh trước khi đóng gói PDF.")
    
    files_convert = st.file_uploader(
        "Tải lên các file nguồn (Word, Excel, PNG, JPG):", 
        type=["docx", "xlsx", "png", "jpg", "jpeg"], 
        accept_multiple_files=True,
        key="conv_source_multi_v3"
    )
    
    modified_images_map = {}
    
    if files_convert:
        image_files = [f for f in files_convert if f.name.split('.')[-1].lower() in ["png", "jpg", "jpeg"]]
        if image_files:
            st.markdown("---")
            st.markdown("### 🖼️ BỘ BIÊN TẬP & XEM TRƯỚC HÌNH ẢNH (30% GỐC)")
            
            for idx, img_file in enumerate(image_files):
                st.markdown(f"#### 📄 Tập tin {idx + 1}: `{img_file.name}`")
                raw_img = Image.open(img_file)
                if raw_img.mode in ("RGBA", "P"):
                    raw_img = raw_img.convert("RGB")
                    
                orig_w, orig_h = raw_img.size
                preview_w, preview_h = int(orig_w * 0.3), int(orig_h * 0.3)
                
                col_editor, col_preview = st.columns([3, 2], gap="large")
                
                with col_editor:
                    st.markdown("##### 🛠️ Cắt / Co dãn vùng ảnh bằng chuột:")
                    if st_cropper is not None:
                        cropped_img = st_cropper(
                            raw_img,
                            realtime_update=True,
                            box_color="#2563EB",
                            aspect_ratio=None,
                            key=f"crop_{idx}_{img_file.name}"
                        )
                    else:
                        cropped_img = raw_img
                    
                    st.markdown("##### 🎛️ Bộ tinh chỉnh màu sắc & góc xoay:")
                    c_s1, c_s2 = st.columns(2)
                    with c_s1:
                        angle = st.slider("🔄 Xoay góc (Độ):", 0, 360, 0, step=90, key=f"rot_{idx}")
                        brightness = st.slider("☀️ Độ sáng:", 0.2, 2.0, 1.0, step=0.1, key=f"bright_{idx}")
                    with c_s2:
                        contrast = st.slider("🌓 Độ tương phản:", 0.2, 2.0, 1.0, step=0.1, key=f"contrast_{idx}")
                        color_sat = st.slider("🎨 Bão hòa màu:", 0.0, 2.0, 1.0, step=0.1, key=f"sat_{idx}")
                    
                    edited_img = cropped_img.copy()
                    if angle != 0:
                        edited_img = edited_img.rotate(-angle, expand=True)
                    if brightness != 1.0:
                        edited_img = ImageEnhance.Brightness(edited_img).enhance(brightness)
                    if contrast != 1.0:
                        edited_img = ImageEnhance.Contrast(edited_img).enhance(contrast)
                    if color_sat != 1.0:
                        edited_img = ImageEnhance.Color(edited_img).enhance(color_sat)
                    
                    modified_images_map[img_file.name] = edited_img

                with col_preview:
                    st.markdown("##### 🔍 Xem trước (30% Kích thước chuẩn):")
                    st.caption(f"Gốc: {orig_w}x{orig_h}px ➔ Hiển thị (30%): {preview_w}x{preview_h}px")
                    st.image(edited_img, width=preview_w)
                
                st.markdown("---")

    if st.button("Đóng gói tất cả thành 1 file PDF", type="primary", disabled=(not files_convert), use_container_width=True):
        with st.spinner("Đang biên dịch PDF..."):
            try:
                final_pdf_doc = fitz.open()
                processed_count = 0
                
                for f_convert in files_convert:
                    f_name = f_convert.name
                    ext = f_name.split('.')[-1].lower()
                    
                    if ext in ["png", "jpg", "jpeg"]:
                        image_to_save = modified_images_map.get(f_name, Image.open(f_convert))
                        if image_to_save.mode in ("RGBA", "P"):
                            image_to_save = image_to_save.convert("RGB")
                        img_bytes = io.BytesIO()
                        image_to_save.save(img_bytes, format="PDF")
                        img_pdf = fitz.open("pdf", img_bytes.getvalue())
                        final_pdf_doc.insert_pdf(img_pdf)
                        img_pdf.close()
                        processed_count += 1
                    
                    elif ext == "xlsx":
                        df_excel = pd.read_excel(f_convert)
                        page = final_pdf_doc.new_page()
                        page.insert_text((40, 40), f"EXCEL DATA: {f_name}\n\n" + df_excel.to_string(), fontsize=10)
                        processed_count += 1
                    
                    elif ext == "docx":
                        import docx
                        doc_word = docx.Document(f_convert)
                        page = final_pdf_doc.new_page()
                        text = f"WORD DATA: {f_name}\n\n" + "\n".join([p.text for p in doc_word.paragraphs if p.text.strip()])
                        page.insert_text((40, 40), text, fontsize=11)
                        processed_count += 1

                if len(final_pdf_doc) > 0:
                    pdf_out = io.BytesIO()
                    final_pdf_doc.save(pdf_out)
                    final_pdf_doc.close()
                    st.success(f"🎉 Chuyển đổi thành công {processed_count} tập tin!")
                    st.download_button("📥 Tải về file PDF Hoàn Chỉnh", pdf_out.getvalue(), "converted_combined.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")

# ==============================================================================
# TAB 6: AI TÁCH NỀN ẢNH
# ==============================================================================
with tab6:
    st.subheader("✨ AI Tách & Đổi Nền Ảnh Studio")
    col_config, col_display = st.columns([1, 2], gap="large")
    
    with col_config:
        img_file_raw = st.file_uploader("Tải ảnh nguồn:", type=["png", "jpg", "jpeg", "webp"], key="bg_up_v4")
        bg_mode = st.selectbox("🎨 Màu nền mới:", ["Trong suốt (Transparent)", "Nền màu đơn sắc (Solid Color)"], key="bg_m_v4")
        bg_color = "#FFFFFF"
        if bg_mode == "Nền màu đơn sắc (Solid Color)":
            bg_color = st.color_picker("Chọn màu nền:", "#FFFFFF", key="bg_c_v4")

    with col_display:
        if img_file_raw is not None:
            c1, c2 = st.columns(2)
            pure_bytes = img_file_raw.getvalue()
            with c1:
                st.markdown("🔹 **Ảnh gốc:**")
                st.image(Image.open(io.BytesIO(pure_bytes)), use_container_width=True)
            with c2:
                st.markdown("✨ **Kết quả:**")
                if st.button("🪄 TIẾN HÀNH XỬ LÝ", type="primary", use_container_width=True):
                    with st.spinner("Đang tách nền..."):
                        try:
                            result_image = None
                            if "REMOVE_BG_API_KEY" in st.secrets:
                                res = requests.post(
                                    'https://api.remove.bg/v1.0/removebg',
                                    files={'image_file': ('image.png', pure_bytes, img_file_raw.type)},
                                    data={'size': 'auto'},
                                    headers={'X-Api-Key': st.secrets["REMOVE_BG_API_KEY"]},
                                )
                                if res.status_code == 200:
                                    result_image = Image.open(io.BytesIO(res.content))
                            
                            if result_image is None:
                                img = Image.open(io.BytesIO(pure_bytes)).convert("RGBA")
                                datas = img.getdata()
                                new_data = [(255, 255, 255, 0) if item[0]>220 and item[1]>220 and item[2]>220 else item for item in datas]
                                img.putdata(new_data)
                                result_image = img

                            if bg_mode == "Nền màu đơn sắc (Solid Color)":
                                hex_s = bg_color.lstrip('#')
                                rgb = tuple(int(hex_s[i:i+2], 16) for i in (0, 2, 4))
                                bg = Image.new("RGBA", result_image.size, rgb + (255,))
                                bg.paste(result_image, (0, 0), result_image)
                                result_image = bg
                            
                            buf = io.BytesIO()
                            result_image.save(buf, format="PNG")
                            st.image(result_image, use_container_width=True)
                            st.download_button("📥 Tải ảnh kết quả (.PNG)", buf.getvalue(), "removed_bg.png", mime="image/png", use_container_width=True)
                        except Exception as e:
                            st.error(f"❌ Lỗi: {str(e)}")

# Footer
st.markdown('<div class="footer-copyright">© 2026 Pro PDF & AI Suite 3D. Powered by Streamlit.</div>', unsafe_allow_html=True)
