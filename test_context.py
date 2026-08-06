from orchestrator.context_builder import ContextBuilder

builder = ContextBuilder()

context = builder.build(
    "What project am I building?"
)

print(context)
