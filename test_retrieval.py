from semantic_memory.retriever import get_relevant_memories

memories = get_relevant_memories(
    "What project is the user working on?"
)

print(memories)