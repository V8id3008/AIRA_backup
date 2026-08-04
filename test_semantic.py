from semantic_memory.memory_db import (
    add_memory,
    search_memory
)

add_memory(
    "I am building A.I.R.A."
)

results = search_memory(
    "What project am I building?"
)

print(results)