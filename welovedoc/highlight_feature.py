import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import os
from config import Config

def process_files(pdf_path, excel_path):
    # Read Excel
    df = pd.read_excel(excel_path)
    uan_numbers = df.iloc[:, 0].astype(str).tolist()  # First column = UAN/ESIC
    
    # Process PDF
    pdf_reader = PdfReader(pdf_path)
    pdf_writer = PdfWriter()
    
    for page in pdf_reader.pages:
        text = page.extract_text()
        for uan in uan_numbers:
            if uan in text:
                pdf_writer.add_page(page)
                break
    
    # Save output PDF
    output_pdf = os.path.join(Config.OUTPUT_FOLDER, 'highlighted.pdf')
    with open(output_pdf, 'wb') as out_pdf:
        pdf_writer.write(out_pdf)
    
    # Save not found entries
    not_found = [uan for uan in uan_numbers if uan not in text]
    not_found_df = df[df.iloc[:, 0].astype(str).isin(not_found)]
    not_found_path = os.path.join(Config.OUTPUT_FOLDER, 'not_found.xlsx')
    not_found_df.to_excel(not_found_path, index=False)
    
    return output_pdf, not_found_path