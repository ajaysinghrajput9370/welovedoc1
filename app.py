from flask import Flask, render_template_string, request, send_file
import pandas as pd
import fitz  # PyMuPDF
import os
from werkzeug.utils import secure_filename
from io import BytesIO
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>We ❤️ DOC</title>
  <style>
    body {
      margin: 0; font-family: Arial, sans-serif;
      background-color: #f5f5f5;
      padding-top: 60px; padding-bottom: 60px;
    }
    .top-strip, .bottom-strip {
      position: fixed; left: 0; right: 0;
      background-color: white; color: black;
      padding: 10px 20px; display: flex;
      align-items: center; justify-content: space-between;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
      z-index: 999;
    }
    .top-strip { top: 0; height: 60px; }
    .bottom-strip { bottom: 0; font-size: 12px; color: #666; }

    .logo { font-weight: bold; font-size: 20px; }
    .blue-heart { color: #007BFF; font-size: 24px; margin: 0 4px; }

    .main-content {
      max-width: 600px; margin: auto; margin-top: 30px;
      background: white; padding: 20px; border-radius: 8px;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    input[type="file"] { margin-bottom: 15px; }
    button {
      background-color: #007BFF; color: white;
      padding: 10px 20px; border: none;
      border-radius: 4px; font-weight: bold;
      cursor: pointer;
    }
  </style>
</head>
<body>

<div class="top-strip">
  <div class="logo">WE<span class="blue-heart">❤️</span>DOC</div>
  <div>
    <button onclick="alert('Login')">Login</button>
    <button onclick="alert('Sign Up')">Sign Up</button>
  </div>
</div>

<div class="main-content">
  <h3>Select PDF and Excel to Highlight</h3>
  <form action="/highlight" method="post" enctype="multipart/form-data">
    <label>Select PDF File:</label><br>
    <input type="file" name="pdf_file" accept="application/pdf" required><br>

    <label>Select Excel File (first column must have UAN/ESIC):</label><br>
    <input type="file" name="excel_file" accept=".xlsx" required><br>

    <label>Highlight Type:</label><br>
    <input type="radio" name="highlight_type" value="uan" checked> UAN Highlight<br>
    <input type="radio" name="highlight_type" value="esic"> ESIC Highlight<br><br>

    <button type="submit">Start Highlighting</button>
  </form>
</div>

<div class="bottom-strip">
  © WeLoveDOC 2025 ® - Highlight your life | A&S
</div>

</body>
</html>
"""

def highlight_pdf(pdf_path, ids_to_match, highlight_type):
    doc = fitz.open(pdf_path)
    matched_doc = fitz.open()
    matched_any = set()

    for page in doc:
        text_instances = []
        words = page.get_text("words")
        for w in words:
            if w[4].strip() in ids_to_match:
                matched_any.add(w[4].strip())
                y0 = w[1]
                y1 = w[3]
                row_words = [word for word in words if abs(word[1] - y0) < 1 and abs(word[3] - y1) < 1]
                for word in row_words:
                    text_instances.append(fitz.Rect(word[:4]))
        if text_instances:
            for inst in text_instances:
                highlight = page.add_highlight_annot(inst)
                highlight.update()
            matched_doc.insert_pdf(doc, from_page=page.number, to_page=page.number)

    # Save results
    output_pdf = os.path.join(UPLOAD_FOLDER, f"highlighted_{uuid.uuid4().hex[:6]}.pdf")
    matched_doc.save(output_pdf)
    return output_pdf, list(set(ids_to_match) - matched_any)

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/highlight', methods=['POST'])
def highlight():
    pdf = request.files['pdf_file']
    excel = request.files['excel_file']
    highlight_type = request.form['highlight_type']

    pdf_path = os.path.join(UPLOAD_FOLDER, secure_filename(pdf.filename))
    excel_path = os.path.join(UPLOAD_FOLDER, secure_filename(excel.filename))
    pdf.save(pdf_path)
    excel.save(excel_path)

    df = pd.read_excel(excel_path)
    ids = df.iloc[:, 0].dropna().astype(str).str.strip().tolist()

    output_pdf_path, not_found_ids = highlight_pdf(pdf_path, ids, highlight_type)

    not_found_excel = BytesIO()
    if not_found_ids:
        pd.DataFrame(not_found_ids, columns=["Not Found"]).to_excel(not_found_excel, index=False)
        not_found_excel.seek(0)

    # Serve ZIP if needed or just files:
    if not_found_ids:
        return f"""
        <h3>Highlighting Complete ✅</h3>
        <a href="/download_pdf?path={output_pdf_path}" target="_blank">📄 Download Highlighted PDF</a><br>
        <a href="/download_excel" target="_blank">📊 Download Data_Not_Found.xlsx</a>
        """
    else:
        return f"""
        <h3>Highlighting Complete ✅ (All IDs Matched)</h3>
        <a href="/download_pdf?path={output_pdf_path}" target="_blank">📄 Download Highlighted PDF</a>
        """

@app.route('/download_pdf')
def download_pdf():
    path = request.args.get('path')
    return send_file(path, as_attachment=True)

@app.route('/download_excel')
def download_excel():
    not_found_excel = BytesIO()
    # Dummy fallback; will only work in-session
    pd.DataFrame(["No matches"]).to_excel(not_found_excel, index=False)
    not_found_excel.seek(0)
    return send_file(not_found_excel, download_name="Data_Not_Found.xlsx", as_attachment=True)
@app.route("/privacy")
def privacy():
    return render_template("privacy_policy.html")

@app.route("/terms")
def terms():
    return render_template("terms_conditions.html")

@app.route("/refund")
def refund():
    return render_template("refund_policy.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == '__main__':
    app.run(debug=True)

