import json
import requests
import re

from memory.validator import MemoryValidator

# =====================================================
# VALIDATOR
# =====================================================

validator = MemoryValidator()

# =====================================================
# CONFIGURATION
# =====================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "aira"
OLLAMA_TIMEOUT = 60

VALID_CATEGORIES = {
    "profile_memory",
    "project_memory",
    "preference_memory",
    "research_memory"
}



# =====================================================
# HELPER FUNCTIONS
# =====================================================



# =====================================================
# HELPER FUNCTIONS
# =====================================================

def safe_json_parse(raw: str) -> dict | None:
    """
    Safely parses JSON returned by Ollama.
    Removes markdown code fences if present.
    Returns None if parsing fails.
    """

    try:

        raw = raw.strip()

        if raw.startswith("```json"):
            raw = raw.replace("```json", "", 1)

        if raw.endswith("```"):
            raw = raw[:-3]

        raw = raw.strip()

        return json.loads(raw)

    except json.JSONDecodeError:
        return None

    except Exception as e:
        return None


def build_memory(
    text,
    category,
    importance,
    confidence,
    source
) -> dict:
    """
    Creates a standardized memory object.
    """

    return {
        "text": text,
        "category": category,
        "importance": importance,
        "confidence": confidence,
        "source": source
    }


def _memory_signature(text: str) -> set[str]:
    """Build a small normalized token set for deterministic duplicate filtering."""
    stop_words = {"the", "user", "i", "am", "is", "are", "has", "have", "my", "a"}
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    normalized = set()
    for token in tokens:
        if token in stop_words:
            continue
        if token.endswith("s") and len(token) > 4:
            token = token[:-1]
        normalized.add(token)
    return normalized


def _is_existing_memory(text: str, existing_memories: list[str] | None) -> bool:
    candidate = _memory_signature(text)
    if not candidate:
        return False
    for existing in existing_memories or []:
        previous = _memory_signature(existing)
        if previous and len(candidate & previous) / max(len(candidate), len(previous)) >= 0.75:
            return True
    return False


# =====================================================
# MEMORY EXTRACTION
# =====================================================

def extract_memories(
    user_message: str,
    assistant_response: str,
    existing_memories: list[str] | None = None,
    source: str = "conversation"
) -> list[dict]:
    """
    Extract structured long-term memories from a conversation using Ollama.

    Returns:
        [
            {
                "text": "...",
                "category": "...",
                "importance": 8,
                "confidence": 0.95,
                "source": "conversation"
            }
        ]
    """

    existing_context = ""

    if existing_memories:

        existing_context = (
            "\nExisting User Memories "
            "(do NOT extract duplicates or near-duplicates of these):\n"
            + "\n".join(f"- {m}" for m in existing_memories)
        )

    prompt = f"""
Analyze this exchange between the User and the AI Assistant (A.I.R.A.).

Extract ONLY important long-term facts about the USER.

Categories:

- profile_memory
- project_memory
- preference_memory
- research_memory

Discard:

- Small talk
- Greetings
- Temporary troubleshooting
- Installation steps
- Assistant information
- Generic explanations

{existing_context}

Duplicate Prevention:

Do NOT extract memories already represented above.

Each memory MUST contain:

1. text
2. category
3. importance (1-10)
4. confidence (0.0-1.0)

Return STRICT JSON ONLY.

Schema:

{{
    "memories": [
        {{
            "text": "statement",
            "category": "profile_memory",
            "importance": 8,
            "confidence": 0.92
        }}
    ]
}}

User Message:
{user_message}

Assistant Response:
{assistant_response}
"""

    try:

        # =====================================================
        # OLLAMA REQUEST
        # =====================================================

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "format": "json",
                "stream": False
            },
            timeout=OLLAMA_TIMEOUT
        )

        if response.status_code != 200:
            return []

        # =====================================================
        # RESPONSE PARSING
        # =====================================================

        raw = response.json().get("response", "").strip()

        if not raw:
            return []

        data = safe_json_parse(raw)

        if data is None:
            return []

        memories = data.get("memories", [])

        validated_memories: list[dict] = []
        for item in memories:
            if not isinstance(item, dict):
                continue
            memory = build_memory(
                text=str(item.get("text", "")).strip(),
                category=str(item.get("category", "")).strip().lower(),
                importance=item.get("importance", 5),
                confidence=item.get("confidence", 0),
                source=source,
            )
            if _is_existing_memory(memory["text"], existing_memories):
                continue
            accepted, _ = validator.validate(memory)
            if accepted:
                validated_memories.append(memory)
        return validated_memories
    # =====================================================
    # NETWORK ERRORS
    # =====================================================

    except requests.exceptions.Timeout:

        print("[MEMORY] Ollama request timed out.")
        return []

    except requests.exceptions.ConnectionError:

        print("[MEMORY] Could not connect to Ollama.")
        return []

    # =====================================================
    # PARSING ERRORS
    # =====================================================

    except json.JSONDecodeError:

        print("[MEMORY] Invalid JSON returned by Ollama.")
        return []

    # =====================================================
    # UNKNOWN ERRORS
    # =====================================================

    except Exception as e:

        print(f"[MEMORY] Unexpected error: {e}")
        return []

# =====================================================
# LEGACY WRAPPER
# =====================================================

def extract_memory(user_message: str) -> dict:
    """
    Legacy wrapper maintained for backwards compatibility.

    Returns:
        {
            "likes": "...",
            "project": "...",
            "working_on": "..."
        }
    """

    memories = extract_memories(
        user_message=user_message,
        assistant_response="",
        existing_memories=None
    )

    if not memories:
        return {}

    first = memories[0]

    category_map = {
        "profile_memory": "likes",
        "project_memory": "project",
        "preference_memory": "likes",
        "research_memory": "working_on"
    }

    key = category_map.get(
        first["category"],
        "working_on"
    )

    return {
        key: first["text"]
    }


# =====================================================
# END OF FILE
# =====================================================
