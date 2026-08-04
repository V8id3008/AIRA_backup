from datetime import datetime, timezone
import math
from semantic_memory.memory_db import COLLECTIONS

def parse_timestamp(ts_str):
    """Parses an ISO format timestamp string, falling back to naive UTC now."""
    if not ts_str:
        return datetime.now(timezone.utc).replace(tzinfo=None)
    try:
        dt = datetime.fromisoformat(ts_str)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except Exception:
        # Handle cases with 'Z' suffix or other variations
        try:
            return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=None)
        except Exception:
            try:
                return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=None)
            except Exception:
                return datetime.now(timezone.utc).replace(tzinfo=None)

def get_relevant_memories(query, limit=5, relevance_weight=0.5, importance_weight=0.3, recency_weight=0.2):
    """
    Retrieves and ranks relevant memories across all categories (collections).
    Calculates a composite score combining relevance, importance, and recency.
    """
    candidates = []
    seen_texts = set()
    current_time = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # Query each collection for top-3 matching memories to ensure high recall and speed
    for category, collection in COLLECTIONS.items():
        try:
            results = collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            if not results or not results.get("ids") or len(results["ids"]) == 0:
                continue
                
            ids = results["ids"][0]
            documents = results["documents"][0]
            metadatas = results["metadatas"][0] if results.get("metadatas") else [None] * len(ids)
            distances = results["distances"][0] if results.get("distances") else [1.0] * len(ids)
            
            for i in range(len(ids)):
                doc_text = documents[i]
                
                # Deduplicate exact text matches across different collections (if any)
                if doc_text in seen_texts:
                    continue
                seen_texts.add(doc_text)
                
                meta = metadatas[i] or {}
                dist = distances[i]
                
                # 1. Relevance: ChromaDB cosine/L2 distance metric (lower distance -> higher relevance)
                relevance = max(0.0, 1.0 - dist)
                
                # 2. Importance: integer from 1 to 10
                importance = int(meta.get("importance", 5))
                importance_score = importance / 10.0
                
                # 3. Recency: time decay based on age in days
                ts_str = meta.get("timestamp")
                ts = parse_timestamp(ts_str)
                days_elapsed = max(0.0, (current_time - ts).total_seconds() / 86400.0)
                recency = math.exp(-0.01 * days_elapsed)  # Exponential decay over time
                
                # Composite Score calculation
                score = (relevance_weight * relevance) + (importance_weight * importance_score) + (recency_weight * recency)
                
                candidates.append({
                    "text": doc_text,
                    "score": score,
                    "category": category,
                    "importance": importance
                })
        except Exception as e:
            # Handle collection query errors gracefully
            print(f"Error querying collection {category}: {e}")
            
    # Sort candidates by composite score descending
    candidates.sort(key=lambda x: x["score"], reverse=True)
    
    # Select top candidates, enforcing the top-K limit and character length bounds
    top_candidates = []
    current_char_count = 0
    MAX_CUMULATIVE_CHARS = 2000  # Keep prompt size strictly bounded
    
    for c in candidates:
        if len(top_candidates) >= limit:
            break
            
        text_to_add = c["text"]
        # Safeguard: if a memory is excessively long, truncate it
        if len(text_to_add) > 500:
            text_to_add = text_to_add[:497] + "..."
            
        if current_char_count + len(text_to_add) > MAX_CUMULATIVE_CHARS:
            # Bounded size limit reached, skip remaining memories
            break
            
        top_candidates.append(text_to_add)
        current_char_count += len(text_to_add)
        
    return top_candidates