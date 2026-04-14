from groq import Groq
from app.config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

def call_llm_json(prompt: str):
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{
            "role": "user",
            "content": prompt + "\n\nRespond in valid JSON format."
        }],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content

def call_llm_text(prompt: str):
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content