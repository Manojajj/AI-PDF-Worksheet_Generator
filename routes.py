from flask import Flask, render_template, request, redirect, url_for, send_file
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import io
from PyPDF2 import PdfReader
from app import app
from app.utils import generate_pdf

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("databricks/dolly-v2-3b")
model = AutoModelForCausalLM.from_pretrained("databricks/dolly-v2-3b")

def generate_questions_with_dolly(text, num_questions=30):
    # Prepare the prompt
    prompt = f"Generate {num_questions} random questions and answers from the following text:\n{text}"
    
    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    
    # Generate responses
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=1500, num_return_sequences=1)
    
    # Decode generated text
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    lines = generated_text.strip().split('\n')
    
    # Extract questions and answers
    qa_pairs = []
    for i in range(0, len(lines), 2):
        question = lines[i].strip()
        answer = lines[i + 1].strip() if (i + 1) < len(lines) else "No answer generated"
        qa_pairs.append((question, answer))
    
    return qa_pairs

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files.get('pdf_file')
        if uploaded_file and uploaded_file.filename.endswith('.pdf'):
            # Extract text from PDF
            pdf_reader = PdfReader(uploaded_file)
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() or ""

            # Generate questions and answers
            num_questions = int(request.form.get('num_questions', 30))
            qa_pairs = generate_questions_with_dolly(extracted_text, num_questions)

            # Render the result page
            return render_template('result.html', qa_pairs=qa_pairs, pdf_file=uploaded_file.read())

    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    # Handle file and form data from results page
    pdf_file = request.form.get('pdf_file')
    num_questions = int(request.form.get('num_questions', 30))
    
    if pdf_file:
        # Decode the file content
        pdf_file_content = io.BytesIO(base64.b64decode(pdf_file))

        # Generate questions and answers
        extracted_text = ""  # You would need to re-extract text from the PDF here
        qa_pairs = generate_questions_with_dolly(extracted_text, num_questions)

        # Generate PDF
        pdf_buffer = generate_pdf(qa_pairs)
        return send_file(
            io.BytesIO(pdf_buffer),
            as_attachment=True,
            download_name="questions_and_answers.pdf",
            mimetype="application/pdf"
        )

    return redirect(url_for('index'))
