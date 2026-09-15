from agents.coding_agent import CodingAgent
from agents.debug_agent import DebugAgent
from agents.memory_agent import MemoryAgent
from agents.planning_agent import PlanningAgent
from agents.research_agent import ResearchAgent
from agents.testing_agent import TestingAgent as AgentTesting


def test_debug_and_testing_compile_checks():
    assert DebugAgent(timeout=10).run_compile_check().passed is True
    assert AgentTesting(timeout=10).run_compile_check().passed is True


def test_planning_agent_creates_debug_plan():
    plan = PlanningAgent().create_plan("debug the memory system")
    assert [step.agent for step in plan] == [
        "Planning Agent", "Debugging Agent", "Coding Agent", "Testing Agent"
    ]


def test_memory_agent_recall_is_read_only():
    assert isinstance(MemoryAgent().recall("What project am I building?"), list)


def test_research_agent_formats_empty_results():
    assert ResearchAgent().format_sources([]) == "No research sources found."


def test_coding_agent_inspects_python_files():
    assert "main.py" in CodingAgent().list_source_files()
