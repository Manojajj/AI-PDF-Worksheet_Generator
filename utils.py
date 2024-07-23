import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from transformers import AutoModelForCausalLM, AutoTokenizer

def generate_pdf(qa_pairs):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 12)
    c.drawString(30, height - 30, "Generated Questions and Answers")
    
    y = height - 50
    for i, (question, answer) in enumerate(qa_pairs):
        c.drawString(30, y, f"Question {i+1}: {question}")
        y -= 20
        c.drawString(30, y, f"Answer: {answer}")
        y -= 40
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - 30

    c.save()
    buffer.seek(0)
    return buffer

def generate_questions_with_dolly(api_key, text, num_questions=30):
    # Initialize Dolly model
    tokenizer = AutoTokenizer.from_pretrained("databricks/dolly-v2-3b")
    model = AutoModelForCausalLM.from_pretrained("databricks/dolly-v2-3b")

    # Generate questions and answers
    prompt = f"Generate {num_questions} random questions and answers from the following text:\n{text}"
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=1500)
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    generated_lines = generated_text.split('\n')
    
    qa_pairs = []
    for i in range(0, len(generated_lines), 2):
        question = generated_lines[i].strip()
        answer = generated_lines[i+1].strip() if (i+1) < len(generated_lines) else "No answer generated"
        qa_pairs.append((question, answer))
    
    return qa_pairs
