import os
import json
import time
from typing import Type
from pydantic import BaseModel
from google import genai
from google.genai import types

def get_gemini_client():
    """
    Initializes the official Google GenAI client using the environment token.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment or .env file.")
    return genai.Client(api_key=api_key)

def call_llm_json_with_retry(system_prompt: str, user_prompt: str, response_schema: Type[BaseModel]) -> BaseModel:
    """
    Calls the Gemini Cloud API to get a structured JSON response matching the Pydantic schema contract.
    Retries once if a network fluctuation or parsing issue occurs.
    """
    client = get_gemini_client()
    
    # Checkpoint Requirement: Retries once if the LLM returns malformed JSON instead of crashing
    max_attempts = 2
    
    for attempt in range(max_attempts):
        try:
            # Configure structured output using the Pydantic model class type directly
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,
                response_mime_type="application/json",
                response_schema=response_schema  # Passes class directly to avoid engine freezes
            )
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_prompt,
                config=config
            )
            
            raw_content = response.text
            
            # Validate output shape using the Pydantic schema contract
            parsed_json = json.loads(raw_content)
            return response_schema.model_validate(parsed_json)
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"--- Gemini Cloud Client Attempt {attempt + 1} Failed ---")
            print(f"Error Type: {type(e).__name__}")
            
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                # Sleep for 25 seconds to clear the specific FreeTier quota window
                print("--> Rate limit hit. Pausing for 25 seconds to clear quota window...")
                time.sleep(25)
            else:
                time.sleep(1)
                
            if attempt == max_attempts - 1:
                raise e