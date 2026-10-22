from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
import os
import re
import json

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

try:
    from docx import Document
except Exception:
    Document = None

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path='')

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/styles.css')
def styles():
    return send_from_directory(BASE_DIR, 'styles.css')

@app.route('/script.js')
def script():
    return send_from_directory(BASE_DIR, 'script.js')


def extract_pdf_text(file_storage):
    if fitz is None:
        return ''
    text = ''
    try:
        file_storage.seek(0)
        pdf = fitz.open(stream=file_storage.read(), filetype='pdf')
        for page in pdf:
            text += page.get_text()
        pdf.close()
    except Exception:
        text = ''
    return text


def extract_docx_text(file_storage):
    if Document is None:
        return ''
    text = ''
    try:
        file_storage.seek(0)
        document = Document(file_storage)
        for paragraph in document.paragraphs:
            text += paragraph.text + '\n'
    except Exception:
        text = ''
    return text


def normalize_text(text):
    return re.sub(r'[^a-zA-Z0-9+\-\s]', ' ', text.lower())


def tokenize(text):
    return set(re.findall(r'[a-z0-9+\-]{2,}', normalize_text(text)))


def score_resume(resume_text, job_description):
    resume_words = tokenize(resume_text)
    jd_words = tokenize(job_description)

    jd_unique = [w for w in jd_words if len(w) >= 2]
    jd_unique = [w for w in jd_unique if w not in {'with', 'the', 'and', 'for', 'that', 'are', 'your', 'job', 'description', 'experience', 'developer', 'team'}]

    overlap = sorted([w for w in jd_unique if w in resume_words])
    overlap_count = len(overlap)
    total = len(jd_unique)

    ats_score = 70
    if resume_text.strip():
        ats_score += 20
    if len(resume_text.split()) >= 80:
        ats_score += 5
    if any(k in resume_words for k in jd_unique):
        ats_score += 5

    ats_score = max(50, min(97, ats_score))

    overlap_ratio = overlap_count / max(total, 1)
    job_match_score = int(overlap_ratio * 100)
    if job_match_score < 30:
        job_match_score = max(30, job_match_score)

    overall_score = int((ats_score * 0.55) + (job_match_score * 0.45))

    missing_skills = [w for w in jd_unique if w not in resume_words][:6]

    if not missing_skills:
        missing_skills = ['No major skill gaps detected']

    keywords = [w for w in jd_unique[:8]]

    return {
        'ats_score': ats_score,
        'job_match_score': job_match_score,
        'overall_score': overall_score,
        'matching_skills': overlap[:10],
        'missing_skills': missing_skills,
        'recommended_keywords': keywords,
    }


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resumeFile' not in request.files:
        return jsonify({"ok": False, "error": "No resume file uploaded."}), 400

    uploaded_file = request.files['resumeFile']
    job_description = request.form.get('jobDescription', '').strip()

    if uploaded_file.filename == '':
        return jsonify({"ok": False, "error": "Please choose a PDF or DOCX resume file."}), 400

    if not job_description:
        return jsonify({"ok": False, "error": "Please enter a job description."}), 400

    ext = Path(uploaded_file.filename).suffix.lower()
    if ext not in {'.pdf', '.docx'}:
        return jsonify({"ok": False, "error": "Unsupported file type. Upload a PDF or DOCX file."}), 400

    file_type = 'PDF' if ext == '.pdf' else 'DOCX'
    file_text = ''
    if ext == '.pdf':
        file_text = extract_pdf_text(uploaded_file)
    else:
        file_text = extract_docx_text(uploaded_file)

    if not file_text.strip():
        return jsonify({"ok": False, "error": "Unable to read text from the uploaded file."}), 400

    safe_filename = f"resume_{Path(uploaded_file.filename).stem}_{os.urandom(6).hex()}{ext}"
    saved_path = UPLOAD_DIR / safe_filename
    uploaded_file.save(saved_path)

    analysis = score_resume(file_text, job_description)

    return jsonify({
        "ok": True,
        "status": "Complete",
        "file": uploaded_file.filename,
        "fileType": file_type,
        "atsScore": analysis['ats_score'],
        "overallScore": analysis['overall_score'],
        "jobMatchScore": analysis['job_match_score'],
        "matchingSkills": analysis['matching_skills'],
        "missingSkills": analysis['missing_skills'],
        "recommendedKeywords": analysis['recommended_keywords'],
        "message": "Resume received and analyzed successfully."
    })


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
