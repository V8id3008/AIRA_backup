from semantic_memory.memory_db import (
    delete_memory_by_id, delete_memory_by_query,
    get_all_memories, get_duplicate_candidates_count, get_low_confidence_memories_count
)
from memory.profile_manager import sync_profile_from_db, load_profile
import time
from semantic_memory.retriever import get_relevant_memories

def print_memory_list():
    try:
        profile = load_profile()
        print("\n================ USER PROFILE ================")
        print(f"Name: {profile.get('name', 'Unknown') or 'Unknown'}")
        
        print("Projects:")
        projects = profile.get("projects", [])
        if projects:
            for p in projects:
                print(f"* {p}")
        else:
            print("* None")
            
        print("Goals:")
        goals = profile.get("goals", [])
        if goals:
            for g in goals:
                print(f"* {g}")
        else:
            print("* None")
            
        print("Preferences:")
        prefs = profile.get("preferences", [])
        if prefs:
            for pr in prefs:
                print(f"* {pr}")
        else:
            print("* None")
            
        print("Skills:")
        skills = profile.get("skills", [])
        if skills:
            for s in skills:
                print(f"* {s}")
        else:
            print("* None")
            
        print("Hardware:")
        hw = profile.get("hardware", {})
        if hw and isinstance(hw, dict):
            for k, v in hw.items():
                if v:
                    print(f"* {k.upper()}: {v}")
        else:
            print("* None")
        print("==============================================")
        
        # Print raw memories
        print("\n============== RAW SEMANTIC MEMORIES ==============")
        mems = get_all_memories()
        for category, items in mems.items():
            nice_cat = category.replace("_", " ").title()
            print(f"\n[{nice_cat}]")
            if not items:
                print("  (Empty)")
            for item in items:
                print(f"  - ID: {item['id'][:8]}... | '{item['text']}'")
                print(f"    [Importance: {item['importance']}/10, Confidence: {item['confidence']:.2f}, Source: {item['source']}]")
        print("====================================================")
    except Exception as e:
        print(f"Error listing memories: {e}")

def print_memory_health():
    try:
        print("\n================ MEMORY HEALTH REPORT ================")
        mems = get_all_memories()
        total = 0
        breakdown_lines = []
        for cat, items in mems.items():
            count = len(items)
            total += count
            nice_name = cat.replace("_", " ").title()
            breakdown_lines.append(f"{nice_name}s: {count}")
            
        print(f"Total Memories: {total}")
        for line in breakdown_lines:
            print(line)
            
        dup_candidates = get_duplicate_candidates_count()
        print(f"Duplicate Candidates: {dup_candidates}")
        
        low_conf = get_low_confidence_memories_count()
        print(f"Low Confidence Memories: {low_conf}")
        
        # Measure average retrieval time over 5 query runs
        start = time.perf_counter()
        test_queries = [
            "What is the user name?", 
            "What project am I building?", 
            "What are user style preferences?",
            "What GPU model?", 
            "research topics"
        ]
        for q in test_queries:
            get_relevant_memories(q, limit=5)
        avg_time = (time.perf_counter() - start) / len(test_queries)
        print(f"Average Retrieval Time: {avg_time:.4f} sec")
        print("======================================================")
    except Exception as e:
        print(f"Error generating memory health report: {e}")

print("====================================================")
print("  A.I.R.A. - Artificial Intelligence for Research   ")
print("====================================================")
print("Initializing semantic memory systems...")
try:
    # Perform an initial sync of profile from DB on startup
    sync_profile_from_db()
except Exception as e:
    print(f"Warning during startup profile sync: {e}")
print("System Ready. Type 'exit' to quit.\n")
print("Available Memory Commands:")
print("  memory:list            - Show structured profile and all raw memories")
print("  memory:health          - Print a detailed health and latency report")
print("  memory:delete <query>  - Semantically delete the closest matching memory")
print("  memory:delete-id <id>  - Delete a memory by its ID (accepts prefix/short ID)\n")

from orchestrator.orchestrator import Orchestrator
orchestrator = Orchestrator()

while True:
    try:
        user = input("You: ")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")
        break

    if user.lower() == "exit":
        break

    if not user.strip():
        continue

    # CLI Command parsing
    if user.strip() == "memory:list":
        print_memory_list()
        continue

    if user.strip() == "memory:health":
        print_memory_health()
        continue

    if user.startswith("memory:delete "):
        query = user.replace("memory:delete ", "").strip()
        print(f"Searching for memory matching '{query}' to delete...")
        success, category, text, dist = delete_memory_by_query(query)
        if success:
            print(f"\n[Success] Deleted memory from collection '{category}':")
            print(f"  '{text}' (Distance: {dist:.4f})")
            # Sync the profile
            sync_profile_from_db()
            print("Structured profile successfully updated/rebuilt.")
        else:
            print(f"\n[Error] No memory matching '{query}' found within the similarity threshold.")
        continue

    if user.startswith("memory:delete-id "):
        mem_id = user.replace("memory:delete-id ", "").strip()
        success, category, text = delete_memory_by_id(mem_id)
        
        if not success:
            # Try to search for partial match on ID
            all_mems = get_all_memories()
            found = False
            for cat, items in all_mems.items():
                for item in items:
                    if item["id"].startswith(mem_id):
                        success, category, text = delete_memory_by_id(item["id"])
                        if success:
                            found = True
                            break
                if found:
                    break
                    
        if success:
            print(f"\n[Success] Deleted memory from '{category}':")
            print(f"  '{text}'")
            sync_profile_from_db()
            print("Structured profile successfully updated/rebuilt.")
        else:
            print(f"\n[Error] Memory ID '{mem_id}' not found.")
        continue

    # Execute assistant generation via Orchestrator
    response = orchestrator.process(user)

    print("\nA.I.R.A.\n")
    print(response)
    print()