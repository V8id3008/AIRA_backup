from orchestrator.router import classify_intent, Intent
from orchestrator.profiler import Profiler
from orchestrator.context_builder import ContextBuilder
from orchestrator.response_builder import ResponseBuilder

from backend.llm import ask_aira
from search.research_engine import gather_research
from semantic_memory.retriever import get_relevant_memories
from agents.debug_agent import DebugAgent
from agents.planning_agent import PlanningAgent
from agents.memory_agent import MemoryAgent
from agents.research_agent import ResearchAgent
from agents.coding_agent import CodingAgent
from agents.testing_agent import TestingAgent


class Orchestrator:

    def __init__(self):
        self.profiler = Profiler()
        self.context_builder = ContextBuilder()
        self.response_builder = ResponseBuilder()
        self.debug_agent = DebugAgent()
        self.planning_agent = PlanningAgent()
        self.memory_agent = MemoryAgent()
        self.research_agent = ResearchAgent()
        self.coding_agent = CodingAgent()
        self.testing_agent = TestingAgent()

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
            Intent.DEBUG: self.handle_debug,
            Intent.PLAN: self.handle_plan,
            Intent.TEST: self.handle_test,
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
        self.profiler.start("Memory Agent")
        response = self.memory_agent.recall_report(text)
        self.profiler.stop("Memory Agent")
        return response

    def handle_research(self, text):

        self.profiler.start("Research")
        research = self.research_agent.research(text)
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
        return self.coding_agent.propose(text)

    def handle_debug(self, text):
        self.profiler.start("Debug Agent")
        report = self.debug_agent.diagnose(text)
        self.profiler.stop("Debug Agent")
        return report

    def handle_plan(self, text):
        self.profiler.start("Planning Agent")
        plan = self.planning_agent.format_plan(text)
        self.profiler.stop("Planning Agent")
        return plan

    def handle_test(self, text):
        self.profiler.start("Testing Agent")
        report = self.testing_agent.report()
        self.profiler.stop("Testing Agent")
        return report

    def handle_system(self, text):
        return "[System Agent - Coming in Phase 9]"
