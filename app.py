from openai import OpenAI
from flask import Flask, request, render_template, flash
from flask_cors import CORS
from dotenv import load_dotenv
import os
from docx import Document
import PyPDF2
import markdown
from langdetect import detect, LangDetectException

app = Flask(__name__)
CORS(app)
load_dotenv()
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def index():
    response = None
    notification = None
    if request.method == "POST":
        user_input = request.form.get("user_input")
        file_input = request.files.get("file_input")
        if file_input and file_input.filename:
            filename = file_input.filename
            if filename.endswith('.txt'):
                user_input = file_input.read().decode("utf-8")
                notification = f"File '{filename}' uploaded successfully."
            elif filename.endswith('.docx'):
                doc = Document(file_input)
                user_input = "\n".join([para.text for para in doc.paragraphs])
                notification = f"File '{filename}' (.docx) uploaded successfully."
            elif filename.endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(file_input)
                user_input = "\n".join([page.extract_text() or '' for page in pdf_reader.pages])
                notification = f"File '{filename}' (.pdf) uploaded successfully."
            else:
                notification = "Only .txt, .docx, and .pdf files are supported."
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
    html_response = markdown.markdown(response.choices[0].message.content) if response else None
    return render_template("index.html", response=html_response, notification=notification)

if __name__ == "__main__":
    app.run(debug=True)
