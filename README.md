# Document AI Summarizer

A modern web application for summarizing documents and text using OpenAI's GPT models. The app features a clean, dark-themed interface with purple accents and smooth transitions. Users can paste text or upload a `.txt` file, and receive a concise summary in a single, focused view.

## Features
- Summarize pasted text or uploaded `.txt` files
- Minimalist, responsive dark mode UI
- Animated transitions for a smooth user experience
- One-click reset to summarize another document

## Requirements
- Python 3.8+
- OpenAI API key

## Installation
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd AI-document-summarizer
   ```
2. **Create a virtual environment and activate it:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment variables:**
   - Copy `.env.example` to `.env` and add your OpenAI API key:
     ```env
     OPENAI_API_KEY=sk-...
     FLASK_SECRET_KEY=your_secret_key
     ```

## Usage
1. **Run the app:**
   ```bash
   python app.py
   ```
2. **Open your browser and go to:**
   [http://localhost:5000](http://localhost:5000)
3. **Paste text or upload a `.txt` file, then click Summarize.**
4. **View the summary and click "📄 Summarize next notes" to start over.**

## License
MIT
