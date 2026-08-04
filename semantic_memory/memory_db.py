import chromadb
import uuid
from datetime import datetime, timezone

# Initialize ChromaDB persistent client
client = chromadb.PersistentClient(path="./semantic_memory/db")

COLLECTIONS = {
    "profile_memory": client.get_or_create_collection(name="profile_memory"),
    "project_memory": client.get_or_create_collection(name="project_memory"),
    "preference_memory": client.get_or_create_collection(name="preference_memory"),
    "research_memory": client.get_or_create_collection(name="research_memory"),
}

CONFIDENCE_THRESHOLD = 0.80

def get_collection(category):
    """Retrieve the collection corresponding to the category, default to profile_memory."""
    if category in COLLECTIONS:
        return COLLECTIONS[category]
    return COLLECTIONS["profile_memory"]

def add_memory(text, category, importance=5, confidence=1.0, timestamp=None, distance_threshold=0.35, source="conversation"):
    """
    Adds a memory to the appropriate collection.
    Performs confidence filtering, duplicate prevention, and update logic.
    """
    # 1. Enforce confidence filtering
    if confidence < CONFIDENCE_THRESHOLD:
        print(f"Memory rejected (Confidence {confidence:.2f} < threshold {CONFIDENCE_THRESHOLD:.2f}): '{text}'")
        return None, False

    if not timestamp:
        timestamp = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()

    collection = get_collection(category)
    
    # Query collection to check for near-duplicates
    results = collection.query(
        query_texts=[text],
        n_results=1
    )
    
    is_update = False
    existing_id = None
    
    if results and results.get("distances") and len(results["distances"]) > 0 and len(results["distances"][0]) > 0:
        distance = results["distances"][0][0]
        matched_id = results["ids"][0][0]
        
        if distance < distance_threshold:
            is_update = True
            existing_id = matched_id
            
    # Metadata for the memory
    metadata = {
        "category": category,
        "importance": int(importance),
        "confidence": float(confidence),
        "timestamp": timestamp,
        "source": source
    }
    
    if is_update:
        # Overwrite/update: delete old and insert new to refresh embeddings and metadata
        collection.delete(ids=[existing_id])
        new_id = existing_id
    else:
        new_id = str(uuid.uuid4())
        
    collection.add(
        documents=[text],
        ids=[new_id],
        metadatas=[metadata]
    )
    
    return new_id, is_update

def search_collection(category, query, n_results=5):
    """Searches a specific collection for matching memories."""
    collection = get_collection(category)
    return collection.query(
        query_texts=[query],
        n_results=n_results
    )

def delete_memory_by_id(mem_id):
    """Deletes a memory by its ID across all collections. Returns (Success, Category, Text)."""
    for category, collection in COLLECTIONS.items():
        try:
            results = collection.get(ids=[mem_id])
            if results and results.get("ids") and len(results["ids"]) > 0:
                text = results["documents"][0]
                collection.delete(ids=[mem_id])
                return True, category, text
        except Exception as e:
            print(f"Error checking collection {category} for ID {mem_id}: {e}")
    return False, None, None

def delete_memory_by_query(query, distance_threshold=0.45):
    """Deletes the single closest memory matching the query across all collections. Returns (Success, Category, Text, Distance)."""
    best_match = None
    best_dist = float('inf')
    
    for category, collection in COLLECTIONS.items():
        try:
            results = collection.query(query_texts=[query], n_results=1)
            if results and results.get("ids") and len(results["ids"]) > 0 and len(results["ids"][0]) > 0:
                dist = results["distances"][0][0]
                mem_id = results["ids"][0][0]
                text = results["documents"][0][0]
                if dist < best_dist:
                    best_dist = dist
                    best_match = (category, mem_id, text)
        except Exception as e:
            print(f"Error querying {category} for delete: {e}")
            
    if best_match and best_dist < distance_threshold:
        category, mem_id, text = best_match
        collection = COLLECTIONS[category]
        collection.delete(ids=[mem_id])
        return True, category, text, best_dist
        
    return False, None, None, None

def get_all_memories():
    """Retrieves all memories across all collections grouped by category."""
    all_memories = {}
    for category, collection in COLLECTIONS.items():
        try:
            res = collection.get()
            mem_list = []
            if res and res.get("ids"):
                ids = res["ids"]
                docs = res["documents"]
                metadatas = res["metadatas"] if res.get("metadatas") else [None] * len(ids)
                
                for i in range(len(ids)):
                    meta = metadatas[i] or {}
                    mem_list.append({
                        "id": ids[i],
                        "text": docs[i],
                        "importance": meta.get("importance", 5),
                        "confidence": meta.get("confidence", 1.0),
                        "source": meta.get("source", "conversation"),
                        "timestamp": meta.get("timestamp", "")
                    })
            all_memories[category] = mem_list
        except Exception as e:
            print(f"Error reading collection {category}: {e}")
            all_memories[category] = []
    return all_memories

def get_duplicate_candidates_count():
    """Finds pairwise near-duplicate memories (distance < 0.35) in each collection."""
    duplicate_count = 0
    seen_pairs = set()
    for category, collection in COLLECTIONS.items():
        try:
            res = collection.get()
            if not res or not res.get("ids"):
                continue
            ids = res["ids"]
            docs = res["documents"]
            if len(ids) < 2:
                continue
                
            for i, doc in enumerate(docs):
                query_res = collection.query(query_texts=[doc], n_results=2)
                if query_res and query_res.get("distances") and len(query_res["distances"][0]) > 1:
                    dist = query_res["distances"][0][1]
                    neighbor_id = query_res["ids"][0][1]
                    current_id = ids[i]
                    
                    if dist < 0.35:
                        pair = tuple(sorted([current_id, neighbor_id]))
                        if pair not in seen_pairs:
                            seen_pairs.add(pair)
                            duplicate_count += 1
        except Exception as e:
            print(f"Error checking duplicates in {category}: {e}")
    return duplicate_count

def get_low_confidence_memories_count():
    """Counts memories with confidence below the configured threshold (0.80)."""
    low_conf_count = 0
    for category, collection in COLLECTIONS.items():
        try:
            res = collection.get()
            if res and res.get("metadatas"):
                for meta in res["metadatas"]:
                    if meta and float(meta.get("confidence", 1.0)) < CONFIDENCE_THRESHOLD:
                        low_conf_count += 1
        except Exception as e:
            print(f"Error checking confidence in {category}: {e}")
    return low_conf_count