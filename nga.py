

import fitz  # PyMuPDF
import pandas as pd
from pdf2docx import Converter # Cần cài thêm: pip install pdf2docx

# --- CHỨC NĂNG BĂM PDF TÙY BIẾN ---
def split_pdf_custom(input_pdf, mode, custom_pages=None):
    """
    mode: 'chan', 'le', 'tuy_chon'
    custom_pages: list hoặc string (VD: "1,3,5" hoặc [1, 2, 5])
    """
    doc = fitz.open(stream=input_pdf.read(), filetype="pdf")
    new_doc = fitz.open()
    
    if mode == 'chan':
        for i in range(1, len(doc), 2): new_doc.insert_pdf(doc, from_page=i, to_page=i)
    elif mode == 'le':
        for i in range(0, len(doc), 2): new_doc.insert_pdf(doc, from_page=i, to_page=i)
    elif mode == 'tuy_chon':
        for p in custom_pages: new_doc.insert_pdf(doc, from_page=p-1, to_page=p-1)
        
    return new_doc

# --- CHỨC NĂNG CHUYỂN ĐỔI ---
def pdf_to_word(pdf_file, docx_path):
    cv = Converter(pdf_file)
    cv.convert(docx_path)
    cv.close()

def pdf_to_excel(pdf_file):
    # Dùng tabula-py hoặc pandas để trích xuất bảng
    import tabula
    df_list = tabula.read_pdf(pdf_file, pages='all')
    return df_list # Danh sách các bảng (DataFrame)
