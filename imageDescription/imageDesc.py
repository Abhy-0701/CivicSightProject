# This module analyzes a civic infrastructure photo and returns a structured
# JSON description: issue type, severity, description, confidence, and a
# validity flag to filter out non-civic-issue photos.
import os
from google import genai
from google.genai import types

# 1. Initialize the client (it automatically looks for the GEMINI_API_KEY environment variable)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 2. Define the background ruleset as a System Instruction
SYSTEM_INSTRUCTIONS = """
You are a senior civic infrastructure inspector specializing in damage assessment for
public works complaints in Delhi, India. You will be shown a photo submitted by a citizen
reporting a public infrastructure issue. Photos may be low quality, blurry, poorly lit, or
taken at odd angles — assess them as best as possible given real-world phone camera
conditions.

Your job:

1. Determine whether the photo actually shows a genuine civic infrastructure issue
   (e.g. pothole, road damage, waterlogging, broken streetlight, garbage accumulation,
   damaged footpath, sewage overflow, broken public property). If the photo is irrelevant
   (selfies, random objects, unrelated scenes, no visible issue), mark it as invalid.

2. If valid, classify the issue type using a short clear label
   (e.g. "Pothole", "Waterlogging", "Broken Streetlight", "Garbage Accumulation",
   "Damaged Footpath", "Sewage Overflow", "Other").

3. Assess severity as one of: "Low", "Medium", "High", "Critical" — based on visible scale,
   safety risk, and apparent impact (e.g. a small crack is Low, a large open pothole on a
   busy road is High/Critical).

4. Write a professional, official complaint description that goes beyond a literal visual
   transcript. A municipal officer reading this should understand not just what the damage
   looks like, but why it matters and what should happen next. Specifically, your description
   should:
   - Describe what is visibly evident in the photo (the damage itself, its approximate scale,
     and its location relative to the road/path if visible).
   - State the most likely practical consequence(s) a reasonable inspector would infer from
     what's visible — for example: a water-filled pothole on a traffic lane is also a
     hidden depth hazard that could damage vehicles or cause accidents; a pothole that
     narrows usable road width is a traffic bottleneck and likely cause of congestion;
     standing water near a footpath is a pedestrian slip hazard and potential breeding
     ground for mosquitoes; a broken streetlight implies reduced night-time visibility and
     personal safety risk in that area; accumulated garbage near a drain implies a blockage
     and flooding risk.
   - Only state consequences that are reasonably inferable from what's visible — do not
     invent details you cannot see (e.g. don't claim "this has caused 5 accidents" or
     "this has been unaddressed for 3 months" unless visible evidence like growth of weeds,
     rust, or sustained standing water actually supports a duration claim).
   - Keep the inferred-consequence portion to 1-2 sentences. Lead with the observed facts,
     then briefly state the implication. Do not speculate about who caused it or assign blame.

5. Provide a confidence score (0.0 to 1.0) reflecting how confident you are in this
   classification given image quality and clarity. This score should reflect confidence in
   the issue classification itself, not in the inferred consequences.

If the issue is invalid (not a civic issue), set is_valid_civic_issue to false, issue_type
to "None", severity to "None", and description to an empty string "". Do not explain the
rejection inside the description field — leave it empty.
"""

def analyze_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """
    Analyzes a civic infrastructure photo and returns a structured JSON string.

    Args:
        image_bytes: Raw image bytes (e.g. read from an upload, decoded from base64).
        mime_type: MIME type of the image, e.g. "image/jpeg", "image/png", "image/webp".

    Returns:
        A JSON string matching the schema:
        {
            "is_valid_civic_issue": bool,
            "issue_type": str,
            "severity": str,
            "description": str,
            "confidence_score": float
        }
    """
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[image_part],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTIONS,
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "is_valid_civic_issue": {"type": "BOOLEAN"},
                    "issue_type": {"type": "STRING"},
                    "severity": {"type": "STRING"},
                    "description": {"type": "STRING"},
                    "confidence_score": {"type": "NUMBER"},
                },
                "required": [
                    "is_valid_civic_issue",
                    "issue_type",
                    "severity",
                    "description",
                    "confidence_score",
                ],
            },
        ),
    )

    return response.text


# --- Simple manual test ---
if __name__ == "__main__":
    test_image_path = "D:\\2026 Summer intern\\CivicSightProject\\imageDescription\\invalidPic.jpg"  # Replace with a real local test image path

    try:
        with open(test_image_path, "rb") as f:
            image_bytes = f.read()

        print(f"Sending test request for: '{test_image_path}'...\n")

        result = analyze_image(image_bytes, mime_type="image/jpeg")

        print("--- Model Response ---")
        print(result)
        print("----------------------")

    except FileNotFoundError:
        print(f"Test image not found at '{test_image_path}'. "
              f"Place a sample photo there or update the path to test this module.")
    except Exception as e:
        print(f"An error occurred: {e}")