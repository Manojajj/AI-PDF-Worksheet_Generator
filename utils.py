from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import io

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
