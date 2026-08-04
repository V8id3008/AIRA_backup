import unittest
import os
import json
from datetime import datetime, timezone, timedelta
import chromadb

# Ensure we import our local modules
from semantic_memory.memory_db import (
    add_memory, search_collection, get_collection, COLLECTIONS,
    delete_memory_by_id, delete_memory_by_query, get_all_memories,
    CONFIDENCE_THRESHOLD
)
from semantic_memory.retriever import get_relevant_memories, parse_timestamp
from memory.extractor import extract_memories
from memory.profile_manager import sync_profile_from_db, load_profile, save_profile

class TestSemanticSystem(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # We will use the live collections but write specific test records
        cls.test_ids = []
        cls.original_profile = load_profile()
        
    @classmethod
    def tearDownClass(cls):
        # Restore the original user profile
        save_profile(cls.original_profile)
        
    def tearDown(self):
        # Clean up any test IDs we generated in ChromaDB during execution
        for cat, coll in COLLECTIONS.items():
            try:
                existing = coll.get()
                to_delete = [id_ for id_ in existing["ids"] if id_ in self.test_ids]
                if to_delete:
                    coll.delete(ids=to_delete)
            except Exception as e:
                print(f"Error during tearDown cleanup: {e}")
        self.test_ids.clear()
        
    def test_01_memory_extraction(self):
        print("\n--- Testing Structured Memory Extraction ---")
        user_msg = "I am building a web app using Next.js. I have an RTX 4050 GPU."
        assistant_res = "That sounds like an interesting project. An RTX 4050 with 6GB VRAM is good for lightweight local testing."
        
        memories = extract_memories(user_msg, assistant_res, source="conversation")
        
        print(f"Extracted {len(memories)} memories:")
        for m in memories:
            print(f" - Text: '{m['text']}' | Category: {m['category']} | Importance: {m['importance']} | Source: {m['source']}")
            
        self.assertGreaterEqual(len(memories), 1, "Should extract at least one memory.")
        for m in memories:
            self.assertIn("text", m)
            self.assertIn("category", m)
            self.assertIn("importance", m)
            self.assertIn("confidence", m)
            self.assertIn("source", m)
            self.assertEqual(m["source"], "conversation")
            self.assertIn(m["category"], ["profile_memory", "project_memory", "preference_memory", "research_memory"])
            
    def test_02_confidence_filtering(self):
        print("\n--- Testing Confidence Filtering ---")
        # 1. Test rejection (Confidence 0.62 < 0.80)
        id_rejected, is_update1 = add_memory(
            text="Reject me: User likes COBOL.",
            category="preference_memory",
            confidence=0.62
        )
        self.assertIsNone(id_rejected, "Memory below threshold should return None.")
        self.assertFalse(is_update1)
        
        # 2. Test acceptance (Confidence 0.95 >= 0.80)
        id_accepted, is_update2 = add_memory(
            text="Store me: User likes Python.",
            category="preference_memory",
            confidence=0.95
        )
        self.assertIsNotNone(id_accepted, "Memory at/above threshold should return a valid ID.")
        self.test_ids.append(id_accepted)
        
        # Verify it was written
        mems = get_all_memories()
        found = any(item["id"] == id_accepted for item in mems["preference_memory"])
        self.assertTrue(found, "Accepted memory should be present in ChromaDB.")

    def test_03_top_k_retrieval_and_bounds(self):
        print("\n--- Testing Top-K Retrieval & Prompt Bounds ---")
        query = "What kind of projects does the user build?"
        
        # 1. Insert 7 distinct project memories to verify Top-K = 5 limit (preventing vector deduplication)
        projects_list = [
            "User builds microservices in Go.",
            "User develops Android apps with Kotlin.",
            "User designs databases using PostgreSQL.",
            "User implements frontend pages in React.",
            "User deploys Kubernetes clusters on AWS.",
            "User writes AI agents using Python.",
            "User creates CI pipelines with GitHub Actions."
        ]
        for p in projects_list:
            mem_id, _ = add_memory(p, "project_memory", importance=5, confidence=0.90)
            self.test_ids.append(mem_id)
            
        retrieved = get_relevant_memories(query, limit=5)
        print(f"Retrieved {len(retrieved)} memories for query (limit=5).")
        self.assertEqual(len(retrieved), 5, "Retrieved memory count should be strictly limited to 5.")
        
        # 2. Test bounding of excessively long memories
        long_text = "User has a complex project goal: " + ("x" * 600)
        long_id, _ = add_memory(long_text, "project_memory", importance=10, confidence=0.95)
        self.test_ids.append(long_id)
        
        retrieved_long = get_relevant_memories("complex project goal", limit=1)
        self.assertEqual(len(retrieved_long), 1)
        retrieved_item = retrieved_long[0]
        
        print(f"Excessively long memory length: {len(retrieved_item)} characters.")
        self.assertLessEqual(len(retrieved_item), 500, "Retrieved memory string should be truncated/bounded to 500 chars.")
        self.assertTrue(retrieved_item.endswith("..."), "Truncated memory should end with ellipsis.")

    def test_04_deletion_system(self):
        print("\n--- Testing Deletion System (ID and Query) ---")
        # 1. Test delete by ID
        text_id = "Delete me: User is testing deletion by ID."
        mem_id, _ = add_memory(text_id, "profile_memory", confidence=0.95)
        self.test_ids.append(mem_id)
        
        success, cat, txt = delete_memory_by_id(mem_id)
        self.assertTrue(success, "Deletion by ID should return True.")
        self.assertEqual(cat, "profile_memory")
        self.assertEqual(txt, text_id)
        
        # Verify gone
        mems = get_all_memories()
        found = any(item["id"] == mem_id for item in mems["profile_memory"])
        self.assertFalse(found, "Memory deleted by ID should no longer exist in ChromaDB.")
        
        # 2. Test delete by query
        text_q = "Delete me: User prefers spacing over tabs."
        mem_id_q, _ = add_memory(text_q, "preference_memory", confidence=0.95)
        self.test_ids.append(mem_id_q)
        
        success_q, cat_q, txt_q, dist = delete_memory_by_query("User prefers spacing over tabs")
        self.assertTrue(success_q, "Deletion by query should return True.")
        self.assertEqual(cat_q, "preference_memory")
        self.assertEqual(txt_q, text_q)
        self.assertLess(dist, 0.45, "Distance of match should be within deletion threshold.")

    def test_05_duplicate_prevention_stress(self):
        print("\n--- Testing Duplicate Prevention Stress Test ---")
        category = "preference_memory"
        
        # Insert variation 1
        id1, is_update1 = add_memory("I prefer concise answers.", category, importance=8, confidence=0.95)
        self.test_ids.append(id1)
        self.assertFalse(is_update1)
        
        # Insert variation 2 (Semantically very similar, minor wording change)
        id2, is_update2 = add_memory("I like concise answers.", category, importance=9, confidence=0.95)
        self.test_ids.append(id2)
        self.assertTrue(is_update2, "Semantic duplicate should trigger update logic.")
        self.assertEqual(id1, id2, "ID should remain the same on duplicate overwrite.")
        
        # Insert variation 3 (Slightly rephrased, but similar meaning)
        # Vector L2 distance is ~0.75, which is above the default 0.35 database threshold.
        # This will be stored as a separate ID on raw insert, which is correct for vector safety.
        id3, is_update3 = add_memory("I prefer short responses.", category, importance=7, confidence=0.95)
        self.test_ids.append(id3)
        self.assertFalse(is_update3, "High distance variation should not overwrite on raw vector check.")
        
        # Test Stage 2: Contextual LLM deduplication
        # When we extract memories and pass existing facts, the LLM should filter out semantic duplicates
        extracted = extract_memories(
            user_message="I prefer short responses.",
            assistant_response="Understood, I will keep responses brief.",
            existing_memories=["I prefer concise answers."]
        )
        print(f"Contextual duplicate extraction test output: {extracted}")
        self.assertEqual(len(extracted), 0, "Semantic duplicate should be filtered out by contextual deduplication.")
        
    def test_06_profile_syncing(self):
        print("\n--- Testing Profile Syncing ---")
        # Add test memories specifically for profile
        id_name, _ = add_memory("User's name is Alex.", "profile_memory", confidence=0.95)
        id_skill, _ = add_memory("User knows Rust and Python.", "profile_memory", confidence=0.95)
        id_pref, _ = add_memory("User prefers highly detailed code documentation.", "preference_memory", confidence=0.95)
        self.test_ids.extend([id_name, id_skill, id_pref])
        
        # Trigger profile sync
        updated_profile = sync_profile_from_db()
        print("Updated Profile JSON:")
        print(json.dumps(updated_profile, indent=2))
        
        self.assertEqual(updated_profile["name"], "Alex", "Name should be parsed and updated in profile.")
        self.assertIn("Python", updated_profile["skills"])
        self.assertIn("highly detailed code documentation", updated_profile["preferences"][0].lower())

if __name__ == "__main__":
    unittest.main()
