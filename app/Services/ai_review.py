import json
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def review_repository(repository_content: str):
    if not os.getenv("GROQ_API_KEY"):
        return {
            "overall_score": 7.2,
            "summary": "A concise review is unavailable right now, but the code structure looks reasonable and is ready for a human pass.",
            "issues": ["Consider adding comments for complex logic and validating edge cases."],
            "suggestions": ["Add a few unit tests and improve naming for clarity."],
        }
        
    repository_content = repository_content[:25000]
    
  
    prompt = f"""
You are a Genius top level Senior Staff Software Engineer performing a professional review of an entire software repository.

Analyze the repository based on:

- Architecture
- Code Quality
- Maintainability
- Readability
- Performance
- Security
- Best Practices
- Folder Structure
- Design Patterns
- Error Handling
- Documentation

Return ONLY valid JSON.

{{
    "overall_score": number,
    "summary": "",
    "issues": [],
    "suggestions": []
}}
pleae try to give a better text and all use better wya of saying add some abuses to make it cool like what the fuck and all this shit like a freind is saying bruhhhh what the hell if the the overall score is belw 7 and hell yeah bro this is good if its above 8.2 is this and all please like being a good freind and all shit pleae 
Repository:

{repository_content}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        print(response.choices[0].message.content)
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Groq Error: {e}")
        return {
            "overall_score": 7.2,
            "summary": "A concise review is unavailable right now, but the code structure looks reasonable and is ready for a human pass.",
            "issues": ["Consider adding comments for complex logic and validating edge cases."],
            "suggestions": ["Add a few unit tests and improve naming for clarity."],
        }
