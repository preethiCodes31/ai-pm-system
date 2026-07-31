import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

def call_llm_json_with_retry(prompt: str = None, user_prompt: str = None, system_prompt: str = None, **kwargs) -> dict:
    actual_user_prompt = user_prompt or prompt or "Generate project plan"
    
    # Force exact key names required by ProjectPlanOut schema
    schema_instruction = (
        "You are a technical project manager. "
        "Return STRICT, VALID JSON ONLY. Do NOT use markdown code blocks like ```json. "
        "Your output must follow this exact structure:\n"
        "{\n"
        '  "milestones": [\n'
        '    {\n'
        '      "title": "Milestone Title",\n'
        '      "description": "Milestone description",\n'
        '      "epics": [\n'
        '        {\n'
        '          "title": "Epic Title",\n'
        '          "description": "Epic description",\n'
        '          "tasks": [\n'
        '            {\n'
        '              "title": "Task Title",\n'
        '              "description": "Task description",\n'
        '              "estimated_hours": 8.0,\n'
        '              "status": "suggested"\n'
        '            }\n'
        '          ]\n'
        '        }\n'
        '      ]\n'
        '    }\n'
        '  ]\n'
        "}"
    )

    actual_system_prompt = f"{system_prompt}\n\n{schema_instruction}" if system_prompt else schema_instruction

    print("--> Sending request to Groq (Llama 3.3)...")
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": actual_system_prompt},
            {"role": "user", "content": actual_user_prompt}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content
    
    # Strip markdown wrappers if present
    cleaned_content = content.strip()
    if cleaned_content.startswith("```"):
        cleaned_content = cleaned_content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    print("--> Received clean JSON from Groq!")
    return json.loads(cleaned_content)