import openai

def generate_questions_with_dolly(text, num_questions=30):
    # Replace with your model call logic
    # For demonstration, a placeholder function:
    openai.api_key = 'YOUR_OPENAI_API_KEY'  # Set this directly or use environment variables
    
    response = openai.Completion.create(
        model="databricks/dolly-v2-3b",
        prompt=f"Generate {num_questions} random questions and answers from the following text:\n{text}",
        max_tokens=1500
    )
    
    generated_text = response.choices[0].text.strip().split('\n')
    qa_pairs = []
    for i in range(0, len(generated_text), 2):
        question = generated_text[i].strip()
        answer = generated_text[i+1].strip() if (i+1) < len(generated_text) else "No answer generated"
        qa_pairs.append((question, answer))
    
    return qa_pairs
