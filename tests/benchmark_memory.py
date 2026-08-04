import time
import os
import json
from datetime import datetime, timezone

# Ensure we import our local modules
from semantic_memory.memory_db import add_memory, delete_memory_by_id, COLLECTIONS
from semantic_memory.retriever import get_relevant_memories
from memory.profile_manager import sync_profile_from_db, load_profile

def run_benchmarks():
    print("====================================================")
    print("      A.I.R.A. Semantic Memory System Benchmark     ")
    print("====================================================")
    
    test_ids = []
    
    # 1. Benchmark: Memory Insertion Time
    print("\n[1/4] Benchmarking Insertion Latency...")
    insert_times = []
    for i in range(10):
        text = f"Benchmark memory item #{i}: The user is running a latency and performance test."
        start = time.perf_counter()
        mem_id, _ = add_memory(
            text=text,
            category="project_memory",
            importance=5,
            confidence=0.90,
            source="benchmark"
        )
        elapsed = time.perf_counter() - start
        insert_times.append(elapsed)
        if mem_id:
            test_ids.append(mem_id)
            
    avg_insert = sum(insert_times) / len(insert_times)
    min_insert = min(insert_times)
    max_insert = max(insert_times)
    print(f"  Insertions executed: {len(insert_times)}")
    print(f"  Average Insertion Time: {avg_insert:.4f} sec")
    print(f"  Min/Max Insertion Time: {min_insert:.4f} / {max_insert:.4f} sec")

    # 2. Benchmark: Retrieval Latency
    print("\n[2/4] Benchmarking Retrieval Latency...")
    retrieval_times = []
    test_queries = [
        "What project am I building?",
        "What kind of tests are running?",
        "Benchmark details",
        "semantic memory latency",
        "performance stats",
        "system benchmarks",
        "relevance search",
        "importance score search",
        "recency decay check",
        "latencies of query"
    ]
    for q in test_queries:
        start = time.perf_counter()
        results = get_relevant_memories(q, limit=5)
        elapsed = time.perf_counter() - start
        retrieval_times.append(elapsed)
        
    avg_retrieve = sum(retrieval_times) / len(retrieval_times)
    min_retrieve = min(retrieval_times)
    max_retrieve = max(retrieval_times)
    print(f"  Retrievals executed: {len(retrieval_times)}")
    print(f"  Average Retrieval Time: {avg_retrieve:.4f} sec")
    print(f"  Min/Max Retrieval Time: {min_retrieve:.4f} / {max_retrieve:.4f} sec")

    # 3. Benchmark: Profile Sync Time (LLM execution)
    print("\n[3/4] Benchmarking Profile Sync (LLM synthesis)...")
    start = time.perf_counter()
    sync_profile_from_db()
    sync_time = time.perf_counter() - start
    print(f"  Sync Profile Time (1 run): {sync_time:.4f} sec (involves local LLM JSON output)")

    # 4. Benchmark: Context Build Time
    print("\n[4/4] Benchmarking Context Build Latency...")
    context_times = []
    for q in test_queries[:5]:
        start = time.perf_counter()
        
        # Load profile context
        profile = load_profile()
        profile_lines = []
        if profile.get("name"):
            profile_lines.append(f"- Name: {profile['name']}")
        if profile.get("projects"):
            profile_lines.append(f"- Projects: {', '.join(profile['projects'])}")
        if profile.get("goals"):
            profile_lines.append(f"- Goals: {', '.join(profile['goals'])}")
        if profile.get("preferences"):
            profile_lines.append(f"- Preferences: {', '.join(profile['preferences'])}")
        
        # Retrieve ranked memories
        memories = get_relevant_memories(q, limit=5)
        memory_context = "\n".join(f"- {m}" for m in memories) if memories else "No memories"
        
        final_prompt = f"""
Profile:
{"\n".join(profile_lines)}

Memories:
{memory_context}

Query:
{q}
"""
        elapsed = time.perf_counter() - start
        context_times.append(elapsed)
        
    avg_context = sum(context_times) / len(context_times)
    print(f"  Average Context Build Time: {avg_context:.4f} sec")
    
    # TearDown cleanups
    print("\nCleaning up benchmark database entries...")
    for mem_id in test_ids:
        delete_memory_by_id(mem_id)
    print("Cleanup completed successfully.")
    print("====================================================")

if __name__ == "__main__":
    run_benchmarks()
