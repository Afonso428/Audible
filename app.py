import os
from flask import Flask, request, render_template, send_file, url_for
from PyPDF2 import PdfReader
from gtts import gTTS
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def convert_pdf_to_mp3(pdf_path, output_path, language='en'):
    """Convert PDF to MP3 with audio."""
    text = extract_text_from_pdf(pdf_path)
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(output_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'pdf_file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['pdf_file']
    if file.filename == '':
        return 'No file selected', 400
    
    if not file.filename.endswith('.pdf'):
        return 'Please upload a PDF file', 400
    
    # Get language from form
    language = request.form.get('language', 'en')
    
    # Save uploaded PDF
    pdf_filename = secure_filename(file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    file.save(pdf_path)
    
    # Convert to MP3
    mp3_filename = os.path.splitext(pdf_filename)[0] + '.mp3'
    mp3_path = os.path.join(app.config['UPLOAD_FOLDER'], mp3_filename)
    convert_pdf_to_mp3(pdf_path, mp3_path, language)
    
    # Clean up PDF file
    os.remove(pdf_path)
    
    # Return MP3 file
    return send_file(mp3_path, as_attachment=True, download_name=mp3_filename)

if __name__ == '__main__':
    app.run(debug=True, port=5001) 