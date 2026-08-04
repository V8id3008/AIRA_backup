from orchestrator.orchestrator import Orchestrator

ai = Orchestrator()

tests = [
    "Hello!",
    "Research AI agents",
    "Remember my name",
    "Write a Python function",
    "Open downloads folder"
]

for test in tests:
    print()
    print("User:", test)
    print("AIRA:", ai.process(test))