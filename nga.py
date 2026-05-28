with tab3:
    st.subheader("📊 PDF sang Excel (Sử dụng PDFPlumber)")
    excel_file = st.file_uploader("Tải PDF bảng biểu:", type="pdf", key="excel")
    if st.button("Convert sang Excel"):
        if excel_file:
            try:
                import pdfplumber
                # Mở PDF bằng pdfplumber
                with pdfplumber.open(excel_file) as pdf:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        for i, page in enumerate(pdf.pages):
                            table = page.extract_table()
                            if table:
                                df = pd.DataFrame(table[1:], columns=table[0])
                                df.to_excel(writer, sheet_name=f'Page_{i+1}', index=False)
                    
                    st.download_button(
                        label="📥 Tải về Excel",
                        data=output.getvalue(),
                        file_name="data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                st.success("✅ Chuyển đổi thành công!")
            except Exception as e:
                st.error(f"Lỗi chuyển đổi: {e}")
