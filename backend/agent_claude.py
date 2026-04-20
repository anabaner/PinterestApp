import os
import json
import base64
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # loads ANTHROPIC_API_KEY from .env file

client = Anthropic()  # automatically picks up the key from environment

SYSTEM_PROMPT = """You are a helpful assistant for a Pinterest-like app.
When given an image, you analyze it and return metadata in JSON format only.
Never return anything outside the JSON object."""

def encode_image(image_path: str) -> tuple[str, str]:
    """Read image from disk and encode it to base64 for the Claude API."""
    ext = os.path.splitext(image_path)[-1].lower()
    media_type_map = {
        ".jpg":  "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png":  "image/png",
        ".webp": "image/webp",
        ".gif":  "image/gif",
    }
    media_type = media_type_map.get(ext, "image/jpeg")

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    return image_data, media_type


def auto_tag_image(image_path: str) -> dict:
    """
    Send an image to Claude and get back a title, description, and tags.
    Returns a dict like:
    {
        "title": "Sunset over mountains",
        "description": "A beautiful golden sunset...",
        "tags": "nature,sunset,mountains,landscape"
    }
    """
    image_data, media_type = encode_image(image_path)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # fastest + cheapest model, perfect for tagging
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": """Analyze this image and return ONLY a JSON object with these fields:
{
  "title": "short catchy title (max 6 words)",
  "description": "2 sentence description of what you see",
  "tags": "5 to 8 comma-separated lowercase tags"
}
No explanation, no markdown, just the raw JSON."""
                    }
                ],
            }
        ],
    )

    # Parse Claude's response
    raw_text = response.content[0].text.strip()

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        # Fallback if Claude returns something unexpected
        result = {
            "title": "Untitled Pin",
            "description": "An interesting image.",
            "tags": "photo,image"
        }

    return result