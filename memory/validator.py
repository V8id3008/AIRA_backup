"""
Responsible for deciding whether an extracted memory
should be stored in long-term semantic memory.
"""

import re

# =====================================================
# MEMORY VALIDATOR
# =====================================================

class MemoryValidator:

    # =====================================================
    # CONFIGURATION
    # =====================================================

    CONFIDENCE_THRESHOLD = 0.80

    VALID_CATEGORIES = {
        "profile_memory",
        "project_memory",
        "preference_memory",
        "research_memory"
    }

    BAD_VALUES = {
        "",
        "none",
        "unknown",
        "n a",
        "na",
        "..."
    }

    ASSISTANT_PATTERNS = [

        "my name is aira",
        "i am aira",
        "assistant name is aira",
        "the assistant is aira",
        "the users name is aira",
        "user name is aira"

    ]

    ASSISTANT_SUBJECTS = [

    "assistant",
    "chatgpt",
    "aira",
    "ai assistant"

    ]
    

    TEMPORARY_KEYWORDS = [

        "installing",
        "requirements txt",
        "pip install",
        "python m",
        "running",
        "executing",
        "creating file",
        "downloading",
        "traceback",
        "module not found",
        "error",
        "compiling",
        "building wheel",
        "collecting",
        "loading model"

    ]

    WEAK_PATTERNS = [

        "user asked",
        "user said",
        "user replied",
        "user mentioned",
        "user is talking",
        "user is speaking",
        "user asked a question",
        "user responded",
        "user answered"

    ]


'''
# =====================================================
# Legacy malformed validation block retained as reference
# =====================================================

    def validate(self, memory: dict):
    """
    Validates whether a memory should be stored.

    Returns:
        (True, "Accepted")
        (False, "Reason")
    """

    # =====================================================
    # OBJECT VALIDATION
    # =====================================================

    if not isinstance(memory, dict):
        return False, "Invalid object"

    # =====================================================
    # REQUIRED FIELDS
    # =====================================================

    text = str(memory.get("text", "")).strip()
    category = memory.get("category")
    importance = memory.get("importance")
    confidence = memory.get("confidence", 0)
    source = memory.get("source")

    # =====================================================
    # EMPTY MEMORY
    # =====================================================

    if not text:
        return False, "Empty memory"

    # =====================================================
    # CATEGORY VALIDATION
    # =====================================================

    if category not in self.VALID_CATEGORIES:
        return False, "Invalid category"

    # =====================================================
    # IMPORTANCE VALIDATION
    # =====================================================

    try:
        importance = int(importance)
    except (TypeError, ValueError):
        return False, "Invalid importance"

    if not (1 <= importance <= 10):
        return False, "Importance out of range"

    # =====================================================
    # CONFIDENCE VALIDATION
    # =====================================================

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        return False, "Invalid confidence"

    if confidence < self.CONFIDENCE_THRESHOLD:
        return False, "Low confidence"

    # =====================================================
    # SOURCE VALIDATION
    # =====================================================

        if not isinstance(source, str):
            return False, "Invalid source"

        if not source.strip():
            return False, "Missing source"

    # =====================================================
    # LENGTH VALIDATION
    # =====================================================

    if len(text) < 10:
        return False, "Memory too short"

# ==================================================
# Normalize text
# ==================================================


    # =====================================================
    # TEXT NORMALIZATION
    # =====================================================

    normalized = text.lower()

    # Remove punctuation
    normalized = re.sub(r"[^a-z0-9\s]", "", normalized)

    # Collapse multiple spaces
    normalized = " ".join(normalized.split())

    # =====================================================
    # PLACEHOLDER MEMORY VALIDATION
    # =====================================================

    if normalized in self.BAD_VALUES:
        return False, "Invalid memory"

    # =====================================================
    # ASSISTANT IDENTITY CONTAMINATION
    # =====================================================

    for pattern in self.ASSISTANT_PATTERNS:

        if pattern in normalized:
            return False, "Assistant identity contamination"

    # =====================================================
    # OWNERSHIP VALIDATION
    # =====================================================

    for subject in self.ASSISTANT_SUBJECTS:   

        if normalized.startswith(subject):
            return False, "Assistant memory"

        if f" {subject} " in f" {normalized} ":
            return False, "Assistant memory"

    # =====================================================
    # TEMPORARY INFORMATION
    # =====================================================

    for keyword in self.TEMPORARY_KEYWORDS:

        if keyword in normalized:
            return False, "Temporary information"

    # =====================================================
    # WEAK MEMORY DETECTION
    # =====================================================

        for pattern in self.WEAK_PATTERNS:

            if normalized.startswith(pattern):
                return False, "Weak memory"

    # =====================================================
    # MEMORY QUALITY CHECK
    # =====================================================

        return True, "Accepted"
'''


class MemoryValidator:
    CONFIDENCE_THRESHOLD = 0.80
    VALID_CATEGORIES = {"profile_memory", "project_memory", "preference_memory", "research_memory"}
    BAD_VALUES = {"", "none", "unknown", "n a", "na", "..."}
    ASSISTANT_PATTERNS = ("my name is aira", "i am aira", "assistant name is aira", "the assistant is aira", "the users name is aira", "user name is aira")
    ASSISTANT_SUBJECTS = ("assistant", "chatgpt", "aira", "ai assistant")
    TEMPORARY_KEYWORDS = ("installing", "requirements txt", "pip install", "python m", "running", "executing", "creating file", "downloading", "traceback", "module not found", "error", "compiling", "building wheel", "collecting", "loading model")
    WEAK_PATTERNS = ("user asked", "user said", "user replied", "user mentioned", "user is talking", "user is speaking", "user asked a question", "user responded", "user answered")

    def validate(self, memory: dict):
        if not isinstance(memory, dict):
            return False, "Invalid object"
        text = str(memory.get("text", "")).strip()
        category = memory.get("category")
        source = memory.get("source")
        if not text:
            return False, "Empty memory"
        if category not in self.VALID_CATEGORIES:
            return False, "Invalid category"
        try:
            importance = int(memory.get("importance"))
        except (TypeError, ValueError):
            return False, "Invalid importance"
        if not 1 <= importance <= 10:
            return False, "Importance out of range"
        try:
            confidence = float(memory.get("confidence", 0))
        except (TypeError, ValueError):
            return False, "Invalid confidence"
        if not 0.0 <= confidence <= 1.0:
            return False, "Confidence out of range"
        if confidence < self.CONFIDENCE_THRESHOLD:
            return False, "Low confidence"
        if not isinstance(source, str):
            return False, "Invalid source"
        if not source.strip():
            return False, "Missing source"
        if len(text) < 10:
            return False, "Memory too short"
        normalized = re.sub(r"[^a-z0-9\s]", "", text.lower())
        normalized = " ".join(normalized.split())
        if normalized in self.BAD_VALUES:
            return False, "Invalid memory"
        if any(pattern in normalized for pattern in self.ASSISTANT_PATTERNS):
            return False, "Assistant identity contamination"
        if any(normalized.startswith(subject) or f" {subject} " in f" {normalized} " for subject in self.ASSISTANT_SUBJECTS):
            return False, "Assistant memory"
        if any(keyword in normalized for keyword in self.TEMPORARY_KEYWORDS):
            return False, "Temporary information"
        if any(normalized.startswith(pattern) for pattern in self.WEAK_PATTERNS):
            return False, "Weak memory"
        return True, "Accepted"
