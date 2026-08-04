import json
import requests
from datetime import datetime

def extract_memories(user_message, assistant_response, existing_memories=None, source="conversation"):
    """
    Extracts structured memories from a single conversation exchange using Ollama.
    Uses contextual deduplication by comparing against existing memories.
    Returns a list of extracted memory dicts with fields: text, category, importance, confidence, source.
    """
    existing_context = ""
    if existing_memories:
        existing_context = "\nExisting User Memories (do NOT extract duplicates or near-duplicates of these):\n" + "\n".join(f"- {m}" for m in existing_memories)

    prompt = f"""
Analyze this exchange between the User and the AI Assistant (A.I.R.A.).
Extract only important, long-term facts, goals, projects, preferences, hardware details, or skills about the user.

Categories to use:
- 'profile_memory': User's identity, name, skills, hardware specs, location, long-term plans.
- 'project_memory': Details about user's active/future development projects.
- 'preference_memory': User's style preferences, coding conventions, response constraints, or likes/dislikes.
- 'research_memory': High-value facts or research topics discussed (e.g. key technical definitions, statistics, or URLs to remember).

Discard:
- Casual conversation, small talk, pleasantries.
- Temporary questions or short-lived troubleshooting actions.
- Model's own internal instructions or generic statements.
{existing_context}

Duplicate Prevention:
Do NOT extract any facts that are already represented, similar, or redundant to the "Existing User Memories" list. Only extract new facts or updates to existing facts.

Each memory must contain:
1. "text": a concise, self-contained statement of the fact in third person (e.g., "User prefers python for AI scripts").
2. "category": one of the 4 categories above.
3. "importance": an integer scale from 1 (lowest) to 10 (highest).
4. "confidence": float value from 0.0 to 1.0.

Return the result strictly as a JSON object conforming to this schema:
{{
  "memories": [
    {{
      "text": "statement",
      "category": "category_name",
      "importance": 8,
      "confidence": 0.9
    }}
  ]
}}

User Message:
{user_message}

Assistant Response:
{assistant_response}
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
            timeout=60  # Increased timeout to prevent Ollama load timeouts
        )
        
        if response.status_code == 200:
            res_json = response.json()
            raw_text = res_json.get("response", "").strip()
            
            # Parse the structured response
            data = json.loads(raw_text)
            memories = data.get("memories", [])
            
            # Validate output categories and structure
            valid_categories = {"profile_memory", "project_memory", "preference_memory", "research_memory"}
            validated_memories = []
            
            for m in memories:
                text = m.get("text", "").strip()
                cat = m.get("category", "").strip().lower()
                imp = m.get("importance", 5)
                conf = m.get("confidence", 1.0)
                
                if text and cat in valid_categories:
                    try:
                        imp = max(1, min(10, int(imp)))
                    except Exception:
                        imp = 5
                    try:
                        conf = max(0.0, min(1.0, float(conf)))
                    except Exception:
                        conf = 1.0
                    
                    validated_memories.append({
                        "text": text,
                        "category": cat,
                        "importance": imp,
                        "confidence": conf,
                        "source": source
                    })
            return validated_memories
    except Exception as e:
        print(f"Error extracting memory: {e}")
        
    return []

def extract_memory(user_message):
    """Legacy wrapper function for backwards compatibility."""
    res = extract_memories(user_message, "", existing_memories=None)
    if res:
        first = res[0]
        category_map = {
            "profile_memory": "likes",
            "project_memory": "project",
            "preference_memory": "likes",
            "research_memory": "working_on"
        }
        key = category_map.get(first["category"], "working_on")
        return {key: first["text"]}
    return {}
