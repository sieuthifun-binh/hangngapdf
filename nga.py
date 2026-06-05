import streamlit as st
import pikepdf
import pdfplumber
import pandas as pd
import io
import fitz  # PyMuPDF
import google.generativeai as genai
from pdf2docx import Converter
import tempfile
import os
from PIL import Image
from rembg import remove  # Thư viện AI xóa nền chuyên dụng

# ==============================================================================
# CẤU HÌNH BAN ĐẦU & LAYOUT HIỆN ĐẠI
# ==============================================================================
st.set_page_config(page_title="Pro PDF & Image AI Suite", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .main-title {
        font-size: 45px !important;
        font-weight: 800 !important;
        color: #1E3A8A !important;
        text-align: center;
        margin-bottom: 30px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 18px !important;
        font-weight: bold !important;
        padding: 12px 24px !important;
    }
    .stButton>button {
        font-weight: bold !important;
        border-radius: 8px !important;
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

st.markdown("<div class='main-title'>🏛️ PRO PDF & IMAGE AI TOOLKIT (6 IN 1)</div>", unsafe_allow_html=True)

# Khởi tạo 6 tab chức năng hiện đại theo yêu cầu mới nhất
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "✂️ Băm PDF", 
    "📝 PDF sang Word & AI Tóm tắt", 
    "📊 AI Trích xuất Excel", 
    "🗜️ Gộp nhiều file PDF", 
    "🔄 Đổi đuôi sang PDF",
    "✨ AI Xóa Nền Ảnh (Remove BG)"
])

# ==============================================================================
# --- TAB 1: BĂM PDF ---
# ==============================================================================
with tab1:
    st.subheader("✂️ Phân tách trang PDF thông minh")
    uploaded = st.file_uploader("Tải file PDF cần băm:", type="pdf", key="b1")
    mode = st.radio("Chế độ cắt trang:", ["Chẵn", "Lẻ", "Tùy chọn số trang"], key="m1", horizontal=True)
    
    pages = ""
    if mode == 'Tùy chọn số trang':
        pages = st.text_input("Nhập các trang cần lấy (Ví dụ: 1, 3, 5):", placeholder="Lưu ý: Phân tách bằng dấu phẩy")
    
    if st.button("Kích hoạt băm file", type="primary"):
        if uploaded:
            with st.spinner("Đang băm nhỏ tài liệu..."):
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
                            st.success(f"🎉 Đã băm xong! Trích xuất thành công {added_pages}/{total} trang.")
                            st.download_button("📥 Tải về file PDF đã cắt", out.getvalue(), "split_pages.pdf", mime="application/pdf")
                        else:
                            st.error("❌ Không có trang hợp lệ nào được tìm thấy dựa trên cấu hình của bạn.")
                        
                        pdf.close()
                        os.remove(tmp.name)
                except Exception as e:
                    st.error(f"⚠️ Đã xảy ra lỗi khi băm file: {str(e)}")
        else:
            st.warning("Vui lòng tải file PDF lên hệ thống trước.")

# ==============================================================================
# --- TAB 2: PDF SANG WORD & AI TÓM TẮT ---
# ==============================================================================
with tab2:
    st.subheader("📝 Chuyển đổi PDF sang Word kết hợp Trí tuệ nhân tạo")
    f_w = st.file_uploader("Tải file PDF cần chuyển đổi & tóm tắt:", type="pdf", key="w_ai")
    
    if st.button("Bắt đầu chuyển đổi & Phân tích AI", type="primary"):
        if f_w:
            with st.spinner("⚡ Bước 1: Đang dựng lại cấu hình Layout chuyển đổi sang Word (.docx)..."):
                try:
                    with tempfile.TemporaryDirectory() as tmp_dir:
                        in_path = os.path.join(tmp_dir, "in.pdf")
                        out_path = os.path.join(tmp_dir, "out.docx")
                        with open(in_path, "wb") as f: 
                            f.write(f_w.getbuffer())
                        
                        cv = Converter(in_path)
                        cv.convert(out_path, start=0, end=None, layout=True)
                        cv.close()
                        
                        with open(out_path, "rb") as f_word:
                            word_bytes = f_word.read()
                        st.success("🎉 Chuyển đổi file sang định dạng Word hoàn tất thành công!")
                        st.download_button("📥 Tải về file Word (.docx)", word_bytes, f"{f_w.name.rsplit('.', 1)[0]}.docx")
                        
                        st.markdown("---")
                        st.subheader("🤖 Bộ não Trí tuệ nhân tạo (Gemini AI) phân tích sâu:")
                        
                        doc_text = ""
                        with fitz.open(in_path) as doc:
                            for page in doc: 
                                doc_text += " " + page.get_text()
                        
                        if len(doc_text.strip()) < 15:
                            st.warning("⚠️ Cảnh báo: Tài liệu này không chứa văn bản kỹ thuật số.")
                        else:
                            if st.session_state.model is None:
                                st.error("❌ Chưa cấu hình GOOGLE_API_KEY trong hệ thống st.secrets.")
                            else:
                                with st.spinner("AI đang đọc toàn văn và cô đọng kiến thức..."):
                                    prompt = f"Bạn là một chuyên gia phân tích tài liệu cao cấp. Hãy đọc toàn bộ văn bản dưới đây và tóm tắt thành các luận điểm, ý chính cốt lõi một cách khoa học, chuyên nghiệp bằng Tiếng Việt:\n\n{doc_text[:100000]}"
                                    res = st.session_state.model.generate_content(prompt)
                                    st.info(f"💡 **BẢN TÓM TẮT CHẤT LƯỢNG CAO TỪ AI:**\n\n{res.text}")
                except Exception as e:
                    st.error(f"❌ Lỗi hệ thống: {str(e)}")
        else:
            st.warning("Vui lòng nạp file PDF nguồn.")

# ==============================================================================
# --- TAB 3: AI PDF SANG EXCEL ---
# ==============================================================================
with tab3:
    st.subheader("📊 Trích xuất bảng biểu dữ liệu từ PDF sang Excel")
    f_e = st.file_uploader("Tải file PDF chứa bảng dữ liệu:", type="pdf", key="e1")
    
    if st.button("Kích hoạt bốc tách dữ liệu Excel", type="primary"):
        if f_e:
            with st.spinner("Đang quét cấu trúc ô và ma trận dòng/cột trên toàn bộ tài liệu..."):
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
                            
                            st.success(f"🎉 Thành công! Đã bốc tách được dữ liệu dạng bảng từ tất cả các trang.")
                            st.dataframe(df.head(20))
                            st.download_button("📥 Tải về file Excel (.xlsx)", out.getvalue(), "extracted_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                        else:
                            st.error("❌ Không tìm thấy bảng biểu nào.")
                        
                        os.remove(tmp.name)
                except Exception as e:
                    st.error(f"⚠️ Lỗi trích xuất bảng Excel: {str(e)}")
        else:
            st.warning("Vui lòng cung cấp file PDF chứa bảng tính.")

# ==============================================================================
# --- TAB 4: GỘP NHIỀU FILE PDF ---
# ==============================================================================
with tab4:
    st.subheader("🗜️ Hợp nhất (Merge) nhiều file PDF riêng lẻ")
    uploaded_merge_files = st.file_uploader("Chọn danh sách các file PDF cần gộp:", type="pdf", accept_multiple_files=True, key="merge_files")
    
    if st.button("Bắt đầu tiến trình gộp file", type="primary", disabled=(not uploaded_merge_files)):
        with st.spinner("Hệ thống đang đồng bộ cấu trúc hình ảnh và font chữ..."):
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
                    st.success(f"🎉 Xuất sắc! Đã nối thành công {count_files} file thành 1 tập tin duy nhất dài {total_pages_merged} trang.")
                    st.download_button("📥 Tải về file PDF Tổng Hợp", out_merge.getvalue(), "merged_document.pdf", mime="application/pdf")
                merged_pdf.close()
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")

# ==============================================================================
# --- TAB 5: CHUYỂN ĐỔI ĐA NĂNG SANG PDF ---
# ==============================================================================
with tab5:
    st.subheader("🔄 Bộ chuyển đổi định dạng đa năng sang File PDF")
    f_convert = st.file_uploader("Tải lên file nguồn cần chuyển đổi sang PDF:", type=["docx", "xlsx", "png", "jpg", "jpeg"], key="conv_source")
    
    if st.button("Thực hiện chuyển đổi mã hóa", type="primary", disabled=(not f_convert)):
        with st.spinner("Đang phân tích định dạng và kết xuất đồ họa sang PDF..."):
            try:
                f_name = f_convert.name
                ext = f_name.split('.')[-1].lower()
                pdf_out = io.BytesIO()
                
                if ext in ["png", "jpg", "jpeg"]:
                    image = Image.open(f_convert)
                    if image.mode in ("RGBA", "P"): image = image.convert("RGB")
                    image.save(pdf_out, format="PDF")
                    st.success("🎉 Đã chuyển đổi bức ảnh sang file PDF thành công!")
                    st.download_button("📥 Tải về file ảnh dạng PDF", pdf_out.getvalue(), f"{f_name.rsplit('.', 1)[0]}.pdf", mime="application/pdf")
                
                elif ext == "xlsx":
                    df_excel = pd.read_excel(f_convert)
                    doc = fitz.open()
                    page = doc.new_page()
                    string_data = df_excel.to_string()
                    page.insert_text((40, 40), f"TÀI LIỆU KẾT XUẤT TỪ FILE EXCEL: {f_name}\n\n" + string_data, fontsize=10)
                    doc.save(pdf_out)
                    doc.close()
                    st.success("🎉 Đã trích xuất dữ liệu Excel sang dạng trang văn bản PDF!")
                    st.download_button("📥 Tải về file Excel dạng PDF", pdf_out.getvalue(), f"{f_name.rsplit('.', 1)[0]}.pdf", mime="application/pdf")
                
                elif ext == "docx":
                    import docx
                    doc_word = docx.Document(f_convert)
                    doc_pdf = fitz.open()
                    page = doc_pdf.new_page()
                    text_lines = [f"TÀI LIỆU KẾT XUẤT TỪ VĂN BẢN WORD: {f_name}\n"]
                    for p in doc_word.paragraphs:
                        if p.text.strip(): text_lines.append(p.text)
                    page.insert_text((50, 50), "\n".join(text_lines), fontsize=12)
                    doc_pdf.save(pdf_out)
                    doc_pdf.close()
                    st.success("🎉 Đã biên dịch toàn bộ văn bản tài liệu Word sang file PDF!")
                    st.download_button("📥 Tải về file Word dạng PDF", pdf_out.getvalue(), f"{f_name.rsplit('.', 1)[0]}.pdf", mime="application/pdf")
                    
            except Exception as e:
                st.error(f"❌ Có lỗi phát sinh: {str(e)}")


# ==============================================================================
# --- TAB 6: AI XÓA NỀN ẢNH SIÊU TỐC QUA API (TỐC ĐỘ < 1 GIÂY) ---
# ==============================================================================
with tab6:
    st.subheader("✨ AI Tách & Đổi Nền Ảnh Studio (Remove BG API)")
    st.caption("⚡ Sử dụng API chuyên dụng cho tốc độ xử lý tức thì, không làm nặng máy chủ.")
    
    col_config, col_display = St.columns([1, 2])
    
    with col_config:
        st.markdown("##### 🛠️ Cài đặt bộ lọc AI")
        uploaded_bg_img = st.file_uploader("Tải ảnh nguồn lên:", type=["png", "jpg", "jpeg", "webp"], key="bg_remover_api")
        
        bg_mode = st.selectbox(
            "🎨 Chọn kiểu nền mới:",
            ["Trong suốt (Transparent)", "Nền màu đơn sắc (Solid Color)"]
        )
        
        bg_color = "#FFFFFF"
        if bg_mode == "Nền màu đơn sắc (Solid Color)":
            bg_color = st.color_picker("Chọn màu nền mong muốn:", "#FFFFFF")
            
    with col_display:
        if uploaded_bg_img is not None:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("🔹 **Ảnh gốc:**")
                original_image = Image.open(uploaded_bg_img)
                st.image(original_image, use_container_width=True)
                
            with c2:
                st.markdown("✨ **Kết quả từ API:**")
                
                if st.button("🪄 TIẾN HÀNH XỬ LÝ ẢNH", type="primary", use_container_width=True):
                    # Kiểm tra xem đã cấu hình API Key chưa
                    if "REMOVE_BG_API_KEY" not in st.secrets:
                        st.error("❌ Chưa cấu hình REMOVE_BG_API_KEY trong Advanced Settings của Streamlit Cloud!")
                    else:
                        with st.spinner("Đang gửi dữ liệu lên Cloud AI xử lý siêu tốc..."):
                            try:
                                # Gọi API của remove.bg
                                response = requests.post(
                                    'https://api.remove.bg/v1.0/removebg',
                                    files={'image_file': uploaded_bg_img.getvalue()},
                                    data={'size': 'auto'},
                                    headers={'X-Api-Key': st.secrets["PybugvXzq8CQjm4tUUVxVPH1"]},
                                )
                                
                                if response.status_code == 200:
                                    output_bytes = response.content
                                    result_image = Image.open(io.BytesIO(output_bytes))
                                    
                                    # Xử lý đổ màu nền nếu chọn màu đơn sắc
                                    if bg_mode == "Nền màu đơn sắc (Solid Color)":
                                        hex_str = bg_color.lstrip('#')
                                        rgb_tuple = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
                                        background = Image.new("RGBA", result_image.size, rgb_tuple + (255,))
                                        background.paste(result_image, (0, 0), result_image)
                                        result_image = background
                                        
                                        buffer = io.BytesIO()
                                        result_image.save(buffer, format="PNG")
                                        final_bytes = buffer.getvalue()
                                    else:
                                        final_bytes = output_bytes
                                    
                                    st.image(result_image, use_container_width=True)
                                    st.success("🎉 AI đã xóa nền hoàn hảo trong 0.5 giây!")
                                    
                                    st.download_button(
                                        label="📥 Tải ảnh kết quả về máy (.PNG)",
                                        data=final_bytes,
                                        file_name=f"{uploaded_bg_img.name.rsplit('.', 1)[0]}_api_bg.png",
                                        mime="image/png",
                                        use_container_width=True
                                    )
                                else:
                                    st.error(f"❌ API trả về lỗi (Mã {response.status_code}): {response.text}")
                            except Exception as e:
                                st.error(f"❌ Lỗi kết nối API: {str(e)}")
        else:
            st.info("📌 Vui lòng tải một bức ảnh lên để bắt đầu.")
