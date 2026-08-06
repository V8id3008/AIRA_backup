from memory.profile_manager import load_profile
from semantic_memory.retriever import get_relevant_memories


class ContextBuilder:
    """
    Builds structured context for the LLM.
    """

    def build(self, user_input: str) -> str:

        profile = load_profile()
        memories = get_relevant_memories(user_input, limit=5)

        sections = []

        # ---------------- Profile ---------------- #

        sections.append("===== USER PROFILE =====")

        sections.append(f"Name: {profile.get('name', 'Unknown')}")

        projects = profile.get("projects", [])
        if projects:
            sections.append(
                "Projects: " + ", ".join(projects)
            )

        goals = profile.get("goals", [])
        if goals:
            sections.append(
                "Goals: " + ", ".join(goals)
            )

        preferences = profile.get("preferences", [])
        if preferences:
            sections.append(
                "Preferences: " + ", ".join(preferences)
            )

        hardware = profile.get("hardware", {})
        if hardware:
            for key, value in hardware.items():
                sections.append(f"{key.upper()}: {value}")

        # ---------------- Memories ---------------- #

        sections.append("\n===== RELEVANT MEMORIES =====")

        if memories:
            for memory in memories:
                sections.append(f"- {memory}")
        else:
            sections.append("None")

        sections.append("============================")

        return "\n".join(sections)