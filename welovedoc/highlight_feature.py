import fitz  # PyMuPDF
import pandas as pd
import os
from openpyxl import Workbook
from tkinter import filedialog
from datetime import datetime


def highlight_and_extract(pdf_path, excel_path, output_folder, match_keywords):
    df = pd.read_excel(excel_path)
    match_values = df.iloc[:, 0].astype(str).tolist()

    pdf = fitz.open(pdf_path)
    matched_pages = []
    not_found = []

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_pdf_path = os.path.join(output_folder, f"{base_name}_highlighted_{now}.pdf")

    output_pdf = fitz.open()

    for page_num, page in enumerate(pdf):
        page_matched = False
        for val in match_values:
            found = False
            text_instances = page.search_for(val)
            for inst in text_instances:
                nearby_text = page.get_textbox(inst).lower()

                # Check for any keyword around the match
                if any(keyword.lower() in nearby_text for keyword in match_keywords):
                    found = True
                    if "esic" in pdf_path.lower():
                        # Full row highlight
                        words = page.get_text("words")
                        for w in words:
                            if val in w[4]:
                                y0 = w[1]
                                y1 = w[3]
                                row_words = [word for word in words if abs(word[1] - y0) < 1.5]
                                for rw in row_words:
                                    rect = fitz.Rect(rw[0], rw[1], rw[2], rw[3])
                                    highlight = page.add_highlight_annot(rect)
                        break

                    else:
                        # UAN or PF ECR case — only highlight number
                        for inst in text_instances:
                            highlight = page.add_highlight_annot(inst)
                        break

            if found:
                matched_pages.append(page_num)
                page_matched = True
                break

        if page_matched:
            output_pdf.insert_pdf(pdf, from_page=page_num, to_page=page_num)

        else:
            not_found.append(val)

    if matched_pages:
        output_pdf.save(output_pdf_path)

    # Save unmatched values
    if not_found:
        wb = Workbook()
        ws = wb.active
        ws.append(["Data Not Found"])
        for item in not_found:
            ws.append([item])
        excel_save_path = os.path.join(output_folder, "Data_Not_Found.xlsx")
        wb.save(excel_save_path)

    pdf.close()
    output_pdf.close()
    return output_pdf_path if matched_pages else None
