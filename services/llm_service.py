import os
import logging
import google.generativeai as genai
from PIL import Image
import base64
import io
import json
import re

logger = logging.getLogger(__name__)

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)


def analyze_waste_image(image_bytes):
    """Analyzes a waste image using Gemini."""
    try:
        # Validate API key
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is not set")
            return "Unknown", "Unknown"

        logger.debug("Using configured Gemini API key")

        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))

        # Convert RGBA to RGB if needed
        if image.mode == "RGBA":
            logger.debug("Converting RGBA image to RGB")
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background

        # Convert image to base64 JPEG
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        image_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Prepare Gemini model
        model = genai.GenerativeModel("gemma-3-27b-it")

        prompt = (
            "Analyze this image of waste.\n"
            "Identify:\n"
            "1. Waste type (Paper, Plastic, E-waste, Food waste, Mixed waste, Hazardous)\n"
            "2. Severity (Critical, High, Medium, Low)\n\n"
            'Return ONLY valid JSON in this format:\n'
            '{"waste_type": "...", "severity": "..."}'
        )

        logger.debug("Sending request to Gemini API")

        response = model.generate_content(
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"mime_type": "image/jpeg", "data": image_b64},
                        {"text": prompt},
                    ],
                }
            ],
            generation_config={"temperature": 0.1},
        )

        if not response or not response.text:
            logger.error("Empty response from Gemini")
            return "Unknown", "Unknown"

        logger.debug(f"Gemini response: {response.text[:200]}")

        # Attempt JSON parsing
        json_match = re.search(r"\{[^}]*\}", response.text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(0))
                waste_type = result.get("waste_type", "Unknown")
                severity = result.get("severity", "Unknown")
                logger.debug(
                    f"Parsed JSON: waste_type={waste_type}, severity={severity}"
                )
                return waste_type, severity
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")

        # Fallback: text parsing
        logger.debug("Falling back to text parsing")
        text = response.text.lower()

        if "paper" in text:
            waste_type = "Paper"
        elif "plastic" in text:
            waste_type = "Plastic"
        elif "e-waste" in text or "electronic" in text:
            waste_type = "E-waste"
        elif "food" in text:
            waste_type = "Food waste"
        elif "hazard" in text:
            waste_type = "Hazardous"
        else:
            waste_type = "Mixed waste"

        if "critical" in text:
            severity = "Critical"
        elif "high" in text:
            severity = "High"
        elif "medium" in text:
            severity = "Medium"
        elif "low" in text:
            severity = "Low"
        else:
            severity = "Unknown"

        logger.debug(
            f"Fallback result: waste_type={waste_type}, severity={severity}"
        )
        return waste_type, severity

    except Exception as e:
        logger.exception(f"Error during Gemini analysis: {e}")
        return "Unknown", "Unknown"
