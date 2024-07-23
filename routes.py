from flask import render_template, request, redirect, url_for, send_file
from app import app
from app.utils import generate_pdf, generate_questions_with_dolly
import io

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files.get('pdf_file')
        if uploaded_file and uploaded_file.filename.endswith('.pdf'):
            # Extract text from PDF
            from PyPDF2 import PdfReader
            pdf_reader = PdfReader(uploaded_file)
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() or ""

            # Generate questions and answers
            api_key = request.form.get('api_key')
            num_questions = int(request.form.get('num_questions', 30))
            qa_pairs = generate_questions_with_dolly(api_key, extracted_text, num_questions)

            # Render the result page
            return render_template('result.html', qa_pairs=qa_pairs)

    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    uploaded_file = request.files.get('pdf_file')
    if uploaded_file and uploaded_file.filename.endswith('.pdf'):
        # Extract text from PDF
        from PyPDF2 import PdfReader
        pdf_reader = PdfReader(uploaded_file)
        extracted_text = ""
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() or ""

        # Generate questions and answers
        api_key = request.form.get('api_key')
        num_questions = int(request.form.get('num_questions', 30))
        qa_pairs = generate_questions_with_dolly(api_key, extracted_text, num_questions)

        # Generate PDF
        pdf_buffer = generate_pdf(qa_pairs)
        return send_file(
            io.BytesIO(pdf_buffer),
            as_attachment=True,
            download_name="questions_and_answers.pdf",
            mimetype="application/pdf"
        )

    return redirect(url_for('index'))
