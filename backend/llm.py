import json
import requests
from semantic_memory.retriever import get_relevant_memories
from memory.profile_manager import load_profile

def ask_aira(user_prompt):
    # Retrieve user profile
    profile = load_profile()
    profile_lines = []
    
    if profile.get("name"):
        profile_lines.append(f"- Name: {profile['name']}")
    if profile.get("projects"):
        profile_lines.append(f"- Projects: {', '.join(profile['projects'])}")
    if profile.get("goals"):
        profile_lines.append(f"- Goals: {', '.join(profile['goals'])}")
    if profile.get("preferences"):
        profile_lines.append(f"- Preferences: {', '.join(profile['preferences'])}")
    if profile.get("skills"):
        profile_lines.append(f"- Skills: {', '.join(profile['skills'])}")
    
    if profile.get("hardware") and isinstance(profile["hardware"], dict):
        hw = [f"{k.upper()}: {v}" for k, v in profile["hardware"].items() if v]
        if hw:
            profile_lines.append(f"- Hardware: {', '.join(hw)}")
            
    profile_context = "\n".join(profile_lines) if profile_lines else "No structured profile details available."

    # Retrieve relevant memories using priority-based ranking
    memories = get_relevant_memories(user_prompt)
    memory_context = "\n".join(f"- {m}" for m in memories) if memories else "No relevant memories found."

    final_prompt = f"""
[USER PROFILE]
{profile_context}

[RELEVANT MEMORIES]
{memory_context}

[USER REQUEST]
{user_prompt}
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "aira",
                "prompt": final_prompt,
                "stream": False
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: Ollama returned status code {response.status_code}"
    except Exception as e:
        return f"Error communicating with Ollama: {e}"