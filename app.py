from openai import OpenAI
from flask import Flask, request, render_template, flash
from flask_cors import CORS
from dotenv import load_dotenv
import os

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
            else:
                notification = "Only .txt files are supported for now."
        if not user_input:
            return render_template("index.html", response="Please provide some text or upload a file.", notification=notification)
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=1000,
            temperature=0,
            messages=[
                {"role": "user", "content": f"Summarize the following text:\n{user_input}"},
            ]
        )
    return render_template("index.html", response=response.choices[0].message.content if response else None, notification=notification)

if __name__ == "__main__":
    app.run(debug=True)