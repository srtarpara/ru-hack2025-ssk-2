import os
import json
from google import genai


def generate_recipe(dish: str, servings: int, model: str = "gemini-2.5-flash") -> dict:
    api_key = os.environ.get("GENAI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GENAI_API_KEY (or GOOGLE_API_KEY) environment variable is not set")

    client = genai.Client(api_key=api_key)

    prompt = f"Dish: '{dish}' for {servings} people. Return JSON only with fields title, servings, timeMinutes, steps, ingredients."

    # The SDK may return text on response.text or nested candidates; handle both.
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "servings": {"type": "number"},
                    "timeMinutes": {"type": "number"},
                    "steps": {"type": "array", "items": {"type": "string"}},
                    "ingredients": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "qty": {"type": "number"},
                                "unit": {"type": "string"}
                            },
                            "required": ["name", "qty", "unit"]
                        }
                    }
                },
                "required": ["title", "servings", "timeMinutes", "steps", "ingredients"]
            }
        }
    )

    text = None
    # prefer response.text if provided
    if hasattr(response, 'text') and response.text:
        text = response.text
    else:
        # try to extract from candidates content path
        try:
            text = response.candidates[0].content.parts[0].text
        except Exception:
            text = None

    if not text:
        raise RuntimeError("AI did not return a valid JSON text response")

    return json.loads(text)