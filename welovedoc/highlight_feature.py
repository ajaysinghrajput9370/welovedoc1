import fitz  # PyMuPDF
import pandas as pd
import os
from openpyxl import Workbook

def highlight_pdf(input_pdf_path, excel_path, output_folder):
    # Read Excel column (assuming first column contains UAN/ESIC numbers)
    excel_df = pd.read_excel(excel_path, header=None)
    keywords = set(str(x).strip() for x in excel_df.iloc[:, 0].dropna())

    not_found = set(keywords)

    pdf_document = fitz.open(input_pdf_path)
    output_pdf = fitz.open()

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text_instances = []

        for word in page.get_text("words"):
            word_text = word[4].strip()
            if word_text in keywords:
                not_found.discard(word_text)
                text_instances.append(word)

        if text_instances:
            for inst in text_instances:
                keyword = inst[4].strip()
                rect = fitz.Rect(inst[0], inst[1], inst[2], inst[3])

                # Check if ESIC or PF page based on header text
                page_text = page.get_text().lower()

                if "state insurance" in page_text or "esic" in page_text:
                    # Highlight entire row for ESIC
                    y0 = inst[1]
                    y1 = inst[3]
                    row_rect = fitz.Rect(0, y0 - 1, page.rect.width, y1 + 1)
                    highlight = page.add_highlight_annot(row_rect)
                else:
                    # Highlight only UAN cell (PF type)
                    highlight = page.add_highlight_annot(rect)

                highlight.set_colors(stroke=(1, 1, 0))  # Yellow
                highlight.update()

            output_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)

    if len(output_pdf) > 0:
        base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]
        for i in range(1, 1000):
            result_filename = f"{base_name}_highlighted_{i}.pdf"
            result_path = os.path.join(output_folder, result_filename)
            if not os.path.exists(result_path):
                output_pdf.save(result_path)
                break

    # Save unmatched entries
    if not_found:
        df_not_found = pd.DataFrame(list(not_found))
        df_not_found.to_excel(os.path.join(output_folder, "Data_Not_Found.xlsx"), index=False, header=False)

    pdf_document.close()
    output_pdf.close()

# Example usage:
# highlight_pdf("example.pdf", "input.xlsx", "output_folder")
