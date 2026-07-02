#This is to get the name of the road authority by giving the road name.
import os
import json
from google import genai
from google.genai import types

# 1. Initialize the client (it automatically looks for the GEMINI_API_KEY environment variable)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 2. Define the background ruleset as a System Instruction
SYSTEM_INSTRUCTIONS = """
You are a geospatial data assistant specializing in Delhi civic infrastructure. 
Your task is to identify the specific government authority responsible for a given road or street name in Delhi, India.

Rules for Classification:
1. MCD: Standard residential streets, colony roads, local commercial lanes.
2. NDMC: Streets explicitly in Lutyens' Delhi / New Delhi zone (e.g., Connaught Place).
3. PWD: Major arterial roads, ring roads, and sub-arterials spanning greater than 60-feet in width.
4. NHAI: National Highways passing through Delhi (e.g., NH-44, NH-48).
5. Delhi Cantt: Roads explicitly within the military cantonment area.
6. DEFAULT RULE: If the input is a residential colony/locality name, is vague, generic,
   or does not clearly match rules 2-5 above, always classify it as MCD. Never return
   "unknown", "none", or leave responsible_authority empty - MCD is the correct default
   for all standard residential and local areas in Delhi.
"""

# 3. Choose a test street name
def resolve_authority(street_name: str) -> str:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=street_name,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTIONS,
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "street_name": {"type": "STRING"},
                    "responsible_authority": {"type": "STRING"},
                    "confidence_score": {"type": "STRING"},
                    "reasoning": {"type": "STRING"}
                },
                "required": ["street_name", "responsible_authority", "confidence_score", "reasoning"]
            }
        ),
    )

    result = json.loads(response.text)

    # Safety net: if Gemini still returns nothing usable, default to MCD
    authority = result.get("responsible_authority", "").strip().lower()
    if authority in ("", "none", "unknown", "n/a", "null"):
        result["responsible_authority"] = "MCD"
        result["reasoning"] = (result.get("reasoning") or "") + \
            " [Fallback applied: defaulted to MCD due to missing/ambiguous authority.]"

    return json.dumps(result)


if __name__ == "__main__":
    test_street = "Delhi - Dehradun Expy"
    print(resolve_authority(test_street))