from orchestrator.router import classify_intent, Intent

from backend.llm import ask_aira
from search.research_engine import gather_research
from semantic_memory.retriever import get_relevant_memories


class Orchestrator:

    def process(self, user_input: str):

        intent = classify_intent(user_input)

        print(f"\n[ORCHESTRATOR] Intent: {intent.value}")

        handlers = {
            Intent.CHAT: self.handle_chat,
            Intent.MEMORY: self.handle_memory,
            Intent.RESEARCH: self.handle_research,
            Intent.CODING: self.handle_coding,
            Intent.SYSTEM: self.handle_system,
        }

        handler = handlers.get(intent)

        if handler:
            return handler(user_input)

        return "Unable to determine intent."

    def handle_chat(self, text):
        return ask_aira(text)

    def handle_memory(self, text):

        memories = get_relevant_memories(text)

        if memories:

            print("\nRelevant Memories:")

            for memory in memories:
                print(f"• {memory}")

        return ask_aira(text)

    def handle_research(self, text):

        research = gather_research(text)

        prompt = f"""
Use the following research to answer the question.

Research:

{research}

Question:

{text}
"""

        return ask_aira(prompt)

    def handle_coding(self, text):

        return "[Qwen Coding Agent - Coming in Phase 7]"

    def handle_system(self, text):

        return "[System Agent - Coming in Phase 9]"