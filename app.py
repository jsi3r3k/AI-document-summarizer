from openai import OpenAI
from flask import Flask, request, render_template, flash, session, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
from docx import Document
import PyPDF2
import markdown
from langdetect import detect, LangDetectException
import zipfile
import pandas as pd
import io
from io import BytesIO

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024 
CORS(app)
load_dotenv()
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SUPPORTED_EXTENSIONS = ['.txt', '.docx', '.pdf', '.csv', '.xlsx']

def extract_text_from_file(file_storage, filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.txt':
        return file_storage.read().decode("utf-8")
    elif ext == '.docx':
        doc = Document(file_storage)
        return "\n".join([para.text for para in doc.paragraphs])
    elif ext == '.pdf':
        pdf_reader = PyPDF2.PdfReader(file_storage)
        return "\n".join([page.extract_text() or '' for page in pdf_reader.pages])
    elif ext == '.csv':
        file_storage.seek(0)
        df = pd.read_csv(file_storage)
        return df.to_string(index=False)
    elif ext == '.xlsx':
        file_storage.seek(0)
        df = pd.read_excel(file_storage)
        return df.to_string(index=False)
    else:
        return None

def extract_text_from_zip(file_storage):
    file_storage.seek(0)
    text_content = []
    with zipfile.ZipFile(file_storage) as z:
        for name in z.namelist():
            ext = os.path.splitext(name)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                with z.open(name) as f:
                    # For docx, pdf, xlsx, csv, need to wrap in BytesIO
                    if ext in ['.docx', '.pdf', '.xlsx', '.csv']:
                        content = extract_text_from_file(io.BytesIO(f.read()), name)
                    else:
                        content = extract_text_from_file(f, name)
                    if content:
                        text_content.append(f"--- {name} ---\n{content}")
    return "\n\n".join(text_content)

@app.route("/", methods=["GET", "POST"])
def index():
    response = None
    notification = None
    if request.method == "POST":
        user_input = request.form.get("user_input")
        file_input = request.files.get("file_input")
        if file_input and file_input.filename:
            filename = file_input.filename
            ext = os.path.splitext(filename)[1].lower()
            allowed_mime_types = {
                '.txt': ['text/plain'],
                '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
                '.pdf': ['application/pdf'],
                '.csv': ['text/csv', 'application/vnd.ms-excel'],
                '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
                '.zip': ['application/zip', 'application/x-zip-compressed', 'multipart/x-zip']
            }
            mime_type = file_input.mimetype
            if ext in allowed_mime_types and mime_type not in allowed_mime_types[ext]:
                notification = f"Niedozwolony typ MIME: {mime_type} dla pliku {filename}."
                return render_template("index.html", response=None, notification=notification)
            if ext == '.zip':
                user_input = extract_text_from_zip(file_input)
                notification = f"ZIP file '{filename}' uploaded and extracted successfully."
            elif ext in SUPPORTED_EXTENSIONS:
                user_input = extract_text_from_file(file_input, filename)
                notification = f"File '{filename}' uploaded successfully."
            else:
                notification = "Only .txt, .docx, .pdf, .csv, .xlsx, and .zip files are supported."
        if not user_input:
            return render_template("index.html", response="Please provide some text or upload a file.", notification=notification)
        try:
            detected_lang = detect(user_input)
        except LangDetectException:
            detected_lang = "en"
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=1000,
            temperature=0,
            messages=[
                {"role": "user", "content": f"Summarize the following text in {detected_lang}:\n{user_input}. Format the summary using markdown for headings, lists, and bold important points. Make sure that the information you provide is accurate and concise."},
            ]
        )
        session['plain_summary'] = response.choices[0].message.content
    html_response = markdown.markdown(response.choices[0].message.content) if response else None
    return render_template("index.html", response=html_response, notification=notification)

@app.route("/download-txt")
def download_txt():
    summary = session.get('plain_summary')
    if not summary:
        return "No summary to export.", 400
    buffer = BytesIO()
    buffer.write(summary.encode('utf-8'))
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="summary.txt", mimetype="text/plain")

@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template("index.html", response=None, notification="File is too big. Maximum size is 20MB."), 413

if __name__ == "__main__":
    app.run(debug=True)
