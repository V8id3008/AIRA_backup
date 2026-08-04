from enum import Enum
import re


class Intent(Enum):
    CHAT = "chat"
    MEMORY = "memory"
    RESEARCH = "research"
    CODING = "coding"
    SYSTEM = "system"


def classify_intent(user_input: str) -> Intent:
    """
    Classify the user's request into one of the core intents.
    """

    text = user_input.lower().strip()

    # Research
    research_keywords = [
        "research",
        "search",
        "latest",
        "news",
        "find",
        "look up",
        "lookup"
    ]

    if any(keyword in text for keyword in research_keywords):
        return Intent.RESEARCH

    # Memory
    memory_keywords = [
        "remember",
        "memory",
        "what do you know",
        "what project",
        "what do i like",
        "who am i"
    ]

    if any(keyword in text for keyword in memory_keywords):
        return Intent.MEMORY

    # Coding
    coding_keywords = [
        "python",
        "code",
        "program",
        "debug",
        "function",
        "class",
        "api",
        "sql",
        "java",
        "cpp",
        "c++"
    ]

    if any(keyword in text for keyword in coding_keywords):
        return Intent.CODING

    # System
    system_keywords = [
        "shutdown",
        "open",
        "launch",
        "system",
        "file",
        "folder"
    ]

    if any(keyword in text for keyword in system_keywords):
        return Intent.SYSTEM

    return Intent.CHAT