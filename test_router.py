from orchestrator.router import classify_intent

tests = [
    "Hello!",
    "Research quantum computing",
    "Write a Python function",
    "Remember my favorite color",
    "Open my downloads folder"
]

for test in tests:
    print(f"{test} --> {classify_intent(test).value}")
