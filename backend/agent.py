import os
import json
import base64
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")  # free tier model


def auto_tag_image(image_path: str) -> dict:
    image = Image.open(image_path)

    prompt = """Analyze this image and return ONLY a JSON object with these fields:
{
  "title": "short catchy title (max 6 words)",
  "description": "2 sentence description of what you see",
  "tags": "5 to 8 comma-separated lowercase tags"
}
No explanation, no markdown, just the raw JSON."""

    response = model.generate_content([prompt, image])
    raw_text = response.text.strip()

    # Strip markdown code fences if Gemini wraps in ```json ... ```
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "title": "Untitled Pin",
            "description": "An interesting image.",
            "tags": "photo,image"
        }