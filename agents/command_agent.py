"""Interactive command center for launching individual A.I.R.A. agents."""

from __future__ import annotations

from dataclasses import dataclass

from agents.coding_agent import CodingAgent
from agents.debug_agent import DebugAgent
from agents.memory_agent import MemoryAgent
from agents.planning_agent import PlanningAgent
from agents.research_agent import ResearchAgent
from agents.self_building_agent import SelfBuildingAgent
from agents.testing_agent import TestingAgent


@dataclass(frozen=True)
class AgentSpec:
    name: str
    description: str
    factory: object | None


class AgentCommandCenter:
    """List agents and launch each selected agent as an independent instance."""

    def __init__(self):
        self.agents = [
            AgentSpec("Debugging Agent", "Diagnose compilation and test failures.", DebugAgent),
            AgentSpec("Planning Agent", "Create a dependency-aware execution plan.", PlanningAgent),
            AgentSpec("Memory Agent", "Recall, extract, validate, and store memories.", MemoryAgent),
            AgentSpec("Research Agent", "Collect and format web research sources.", ResearchAgent),
            AgentSpec("Coding Agent", "Inspect the repository and propose coding work.", CodingAgent),
            AgentSpec("Testing Agent", "Run bounded compilation and agent-test checks.", TestingAgent),
            AgentSpec("Self-Building Agent", "Inspect A.I.R.A. and plan the next build step.", SelfBuildingAgent),
            AgentSpec("Code Review Agent", "Review diffs for correctness and regressions.", None),
            AgentSpec("Documentation Agent", "Create and maintain project documentation.", None),
            AgentSpec("System Agent", "Perform approved operating-system actions.", None),
            AgentSpec("Security Agent", "Audit code, permissions, and trust boundaries.", None),
            AgentSpec("Multi-Agent Coordinator", "Coordinate multiple specialist agents.", None),
        ]

    def show_agents(self) -> None:
        print("\nA.I.R.A. AGENT COMMAND CENTER\n")
        for number, spec in enumerate(self.agents, 1):
            status = "READY" if spec.factory is not None else "PLANNED"
            print(f"{number:>2}. {spec.name:<24} [{status}] - {spec.description}")
        print("\nCommands: number to launch, 'list' to refresh, or 'exit' to quit.\n")

    def launch(self, number: int, request: str) -> str:
        if number < 1 or number > len(self.agents):
            return "Invalid agent number."
        spec = self.agents[number - 1]
        if spec.factory is None:
            return f"{spec.name} is planned but not built yet."

        agent = spec.factory()
        if isinstance(agent, DebugAgent):
            return agent.diagnose(request)
        if isinstance(agent, PlanningAgent):
            return agent.format_plan(request)
        if isinstance(agent, MemoryAgent):
            return agent.recall_report(request)
        if isinstance(agent, ResearchAgent):
            return agent.research(request)
        if isinstance(agent, CodingAgent):
            return agent.propose(request)
        if isinstance(agent, TestingAgent):
            return agent.report()
        if isinstance(agent, SelfBuildingAgent):
            return agent.run_build_cycle()
        return "This agent has no command handler yet."

    def run(self) -> None:
        self.show_agents()
        while True:
            choice = input("Select agent: ").strip()
            if choice.lower() in {"exit", "q", "quit"}:
                print("Agent command center closed.")
                return
            if choice.lower() == "list":
                self.show_agents()
                continue
            try:
                number = int(choice)
            except ValueError:
                print("Enter an agent number, 'list', or 'exit'.")
                continue
            if number < 1 or number > len(self.agents):
                print("Invalid agent number.")
                continue
            if self.agents[number - 1].factory is None:
                print(self.launch(number, ""))
                continue
            request = input("Request for this agent: ").strip()
            print(f"\n--- {self.agents[number - 1].name} instance ---")
            print(self.launch(number, request))
            print("--- instance complete ---\n")


def main() -> None:
    AgentCommandCenter().run()


if __name__ == "__main__":
    main()
