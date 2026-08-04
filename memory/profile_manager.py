import json
import requests
from semantic_memory.memory_db import COLLECTIONS

PROFILE_FILE = "data/profile.json"

def load_profile():
    try:
        with open(PROFILE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {
            "name": "",
            "projects": [],
            "goals": [],
            "preferences": [],
            "skills": [],
            "hardware": {}
        }

def save_profile(profile):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=4)

def sync_profile_from_db():
    """
    Retrieves all documents from profile_memory, project_memory, and preference_memory,
    and updates data/profile.json using the LLM to structure them.
    """
    all_facts = []
    
    for cat in ["profile_memory", "project_memory", "preference_memory"]:
        coll = COLLECTIONS[cat]
        try:
            results = coll.get()
            if results and results.get("documents"):
                for doc in results["documents"]:
                    all_facts.append(f"- {doc} (Category: {cat})")
        except Exception as e:
            print(f"Error fetching from {cat}: {e}")
            
    if not all_facts:
        return load_profile()
        
    current_profile = load_profile()
    facts_str = "\n".join(all_facts)
    
    prompt = f"""
You are the Profile Synthesizer for A.I.R.A.
Your job is to rebuild the user's structured profile using the raw memory facts collected from their conversations.

Existing Profile:
{json.dumps(current_profile, indent=2)}

Extracted Memory Facts:
{facts_str}

You must return a updated, cleaned, and merged JSON object adhering exactly to this structure:
{{
  "name": "User's name (string, or empty if unknown)",
  "projects": ["list of user's active/past projects"],
  "goals": ["list of user's active long-term goals"],
  "preferences": ["list of user's development or formatting preferences"],
  "skills": ["list of user's technical skills or languages"],
  "hardware": {{
    "gpu": "GPU name (or empty)",
    "ram": "RAM size (or empty)",
    "cpu": "CPU details (or empty)",
    "os": "Operating system (or empty)"
  }}
}}

Merge the new facts into the appropriate fields, resolve contradictions by prioritizing newer facts, and delete outdated projects/goals. Do not add details not mentioned.
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "aira",
                "prompt": prompt,
                "format": "json",
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            res_json = response.json()
            raw_text = res_json.get("response", "").strip()
            updated_profile = json.loads(raw_text)
            
            # Verify and sanitize hardware fields
            if "hardware" not in updated_profile or not isinstance(updated_profile["hardware"], dict):
                updated_profile["hardware"] = current_profile.get("hardware", {})
                
            # Ensure required keys exist
            required_keys = ["name", "projects", "goals", "preferences", "skills", "hardware"]
            for key in required_keys:
                if key not in updated_profile:
                    updated_profile[key] = current_profile.get(key, [] if key not in ["name", "hardware"] else ("" if key == "name" else {}))
            
            save_profile(updated_profile)
            return updated_profile
    except Exception as e:
        print(f"Error syncing profile from database: {e}")
        
    return current_profile