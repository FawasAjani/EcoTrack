
import os
import re
import html

from dotenv import load_dotenv
from google import genai

load_dotenv()


def get_gemini_client():
    """Create a Gemini client using the backend API key."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Gemini API key is not configured.")

    return genai.Client(api_key=api_key)


def generate_ai_response(user_message, recommendations):
    """Generate an AI response using EcoTrack recommendations."""

    client = get_gemini_client()

    recommendation_context = "\n".join(
        [
            (
                f"Category: {item['category']}\n"
                f"Title: {item['title']}\n"
                f"Message: {item['message']}\n"
                f"Impact measurement: {item['impact_type']}\n"
                f"Priority: {item['priority']}"
            )
            for item in recommendations
        ]
    )

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=(
            "You are EcoTrack's sustainability assistant. "
            "Help users understand their environmental impact "
            "and make practical sustainable choices.\n\n"
            "Use the supplied EcoTrack recommendations as factual data. "
            "Never invent emissions figures or claim access to data "
            "that has not been supplied. Keep CO2 and CO2e distinct. "
            "Give clear, friendly and practical answers.\n\n"
            "IMPORTANT FORMATTING RULES:\n"
            "- Respond using plain text only.\n"
            "- Do not use Markdown formatting.\n"
            "- Do not use asterisks for bold or italic text.\n"
            "- Do not include HTML tags or HTML entities.\n"
            "- Use normal paragraphs and line breaks.\n\n"
            f"User's EcoTrack recommendations:\n"
            f"{recommendation_context}\n\n"
            f"User's question:\n{user_message}"
        )
    )

    text = response.text or ""

    # Decode HTML entities.
    text = html.unescape(text)

    # Remove escaped and unescaped Markdown formatting markers.
    text = text.replace(r"\*\*", "")
    text = text.replace(r"\*", "")
    text = text.replace("**", "")
    text = text.replace("*", "")

    # Remove any remaining HTML tags.
    text = re.sub(r"<[^>]*>", "", text)

    return text.strip()
