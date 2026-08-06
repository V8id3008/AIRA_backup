from orchestrator.router import classify_intent, Intent
from orchestrator.profiler import Profiler
from orchestrator.context_builder import ContextBuilder
from orchestrator.response_builder import ResponseBuilder

from backend.llm import ask_aira
from search.research_engine import gather_research
from semantic_memory.retriever import get_relevant_memories


class Orchestrator:

    def __init__(self):
        self.profiler = Profiler()
        self.context_builder = ContextBuilder()
        self.response_builder = ResponseBuilder()

    def process(self, user_input: str):

        self.profiler.reset()

        self.profiler.start("Intent Routing")
        intent = classify_intent(user_input)
        self.profiler.stop("Intent Routing")

        print(f"\n[ORCHESTRATOR] Intent: {intent.value}")

        handlers = {
            Intent.CHAT: self.handle_chat,
            Intent.MEMORY: self.handle_memory,
            Intent.RESEARCH: self.handle_research,
            Intent.CODING: self.handle_coding,
            Intent.SYSTEM: self.handle_system,
        }

        handler = handlers.get(intent)

        if handler is None:
            return "Unable to determine intent."

        response = handler(user_input)

        self.profiler.report()

        return response

    def handle_chat(self, text):

        context = self.context_builder.build(text)

        prompt = self.response_builder.build(
            user_input=text,
            context=context
        )

        self.profiler.start("LLM")
        response = ask_aira(prompt)
        self.profiler.stop("LLM")

        return response

    def handle_memory(self, text):

        self.profiler.start("Memory Retrieval")
        memories = get_relevant_memories(text)
        self.profiler.stop("Memory Retrieval")

        if memories:
            print("\nRelevant Memories:")
            for memory in memories:
                print(f"• {memory}")

        context = self.context_builder.build(text)

        prompt = self.response_builder.build(
            user_input=text,
            context=context
        )

        self.profiler.start("LLM")
        response = ask_aira(prompt)
        self.profiler.stop("LLM")

        return response

    def handle_research(self, text):

        self.profiler.start("Research")
        research = gather_research(text)
        self.profiler.stop("Research")

        context = self.context_builder.build(text)

        prompt = self.response_builder.build(
            user_input=text,
            context=context,
            research=research
        )

        self.profiler.start("LLM")
        response = ask_aira(prompt)
        self.profiler.stop("LLM")

        return response

    def handle_coding(self, text):
        return "[Qwen Coding Agent - Coming in Phase 7]"

    def handle_system(self, text):
        return "[System Agent - Coming in Phase 9]"