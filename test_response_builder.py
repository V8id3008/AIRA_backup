from orchestrator.response_builder import ResponseBuilder

builder = ResponseBuilder()

prompt = builder.build(
    user_input="Explain AI agents.",
    context="User prefers concise answers.",
    research="AI agents are autonomous systems..."
)

print(prompt)