import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, DictionaryObject, ArrayObject, NumberObject
import os
from config import Config

def add_highlight(page, keyword, full_row=False):
    text = page.extract_text()
    if not text:
        return

    if keyword not in text:
        return

    matches = []
    lines = text.split('\n')
    for line in lines:
        if keyword in line:
            matches.append(line)

    if not matches:
        return

    for line in matches:
        if full_row:
            highlight_text = line
        else:
            highlight_text = keyword

        if "/Annots" not in page:
            page[NameObject("/Annots")] = ArrayObject()

        annotation = DictionaryObject()
        annotation.update({
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Highlight"),
            NameObject("/Rect"): ArrayObject([NumberObject(0), NumberObject(0), NumberObject(0), NumberObject(0)]),
            NameObject("/C"): ArrayObject([NumberObject(1), NumberObject(1), NumberObject(0)]),  # Yellow color
            NameObject("/F"): NumberObject(4),
            # No visible content/text — silent highlight
        })

        page["/Annots"].append(annotation)

def process_files(pdf_path, excel_path, mode='uan'):
    df = pd.read_excel(excel_path)
    values = df.iloc[:, 0].astype(str).tolist()
    
    pdf_reader = PdfReader(pdf_path)
    pdf_writer = PdfWriter()

    found_values = []
    keywords_to_always_highlight = [
        "EMPLOYEE'S PROVIDENT FUND ORGANISATION",
        "Employees' State Insurance Corporation"
    ]

    for page in pdf_reader.pages:
        text = page.extract_text()
        matched = False

        # Always highlight these lines if present
        for kw in keywords_to_always_highlight:
            if kw in text:
                add_highlight(page, kw, full_row=False)
                matched = True

        for val in values:
            if val in text:
                matched = True
                if mode == 'uan':
                    add_highlight(page, val, full_row=False)  # only highlight text
                elif mode == 'esic':
                    add_highlight(page, val, full_row=True)   # full row highlight
                found_values.append(val)

        if matched:
            pdf_writer.add_page(page)

    # Save matched pages to output PDF
    output_pdf_path = os.path.join(Config.OUTPUT_FOLDER, 'highlighted.pdf')
    with open(output_pdf_path, 'wb') as f:
        pdf_writer.write(f)

    # Save unmatched entries to Excel
    not_found = list(set(values) - set(found_values))
    not_found_df = df[df.iloc[:, 0].astype(str).isin(not_found)]
    not_found_excel = os.path.join(Config.OUTPUT_FOLDER, 'Data_Not_Found.xlsx')
    not_found_df.to_excel(not_found_excel, index=False)

    return output_pdf_path, not_found_excel
