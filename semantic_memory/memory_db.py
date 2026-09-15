import math
import chromadb
import uuid
from datetime import datetime, timezone

'''


# =====================================================
# CHROMADB CONFIGURATION
# =====================================================

DB_PATH = "./semantic_memory/db"

client = chromadb.PersistentClient(
    path=DB_PATH
)


# =====================================================
# MEMORY COLLECTIONS
# =====================================================

COLLECTION_NAMES = (
    "profile_memory",
    "project_memory",
    "preference_memory",
    "research_memory"
)

COLLECTIONS = {
    category: client.get_or_create_collection(
        name=category
    )
    for category in COLLECTION_NAMES
}


# =====================================================
# MEMORY CONFIGURATION
# =====================================================

CONFIDENCE_THRESHOLD = 0.80

DUPLICATE_DISTANCE_THRESHOLD = 0.35

DELETE_DISTANCE_THRESHOLD = 0.45

# =====================================================
# COLLECTION ACCESS
# =====================================================

def get_collection(category: str):
    """
    Retrieve the ChromaDB collection for a memory category.

    Raises:
        ValueError: If the category is not supported.
    """

    if category not in COLLECTIONS:
        raise ValueError(
            f"Invalid memory category: {category}"
        )

    return COLLECTIONS[category]
# =====================================================
# MEMORY STORAGE
# =====================================================

def add_memory(
    text: str,
    category: str,
    importance: int = 5,
    confidence: float = 1.0,
    timestamp: str | None = None,
    distance_threshold: float | None = None,
    source: str = "conversation"
):
    """
    Adds a validated memory to the appropriate ChromaDB collection.

    Performs:
        - Confidence filtering
        - Category validation
        - Metadata normalization
        - Near-duplicate detection
        - Existing memory update
        - Persistent storage

    Returns:
        (memory_id, is_update)

        Returns (None, False) if the memory is rejected.
    """

    # =====================================================
    # INPUT VALIDATION
    # =====================================================

    if not isinstance(text, str) or not text.strip():
        print("[MEMORY DB] Memory text is empty.")
        return None, False

    text = text.strip()

    if category not in COLLECTIONS:
        print(f"[MEMORY DB] Invalid memory category: {category}")
        return None, False

# =====================================================
# CONFIDENCE VALIDATION
# =====================================================

try:

    confidence = float(confidence)

if not math.isfinite(confidence):

    print(
        f"[MEMORY DB] Confidence is not finite: "
        f"{confidence}"
    )

    return None, False

except (TypeError, ValueError):

    print(
        "[MEMORY DB] Invalid confidence value."
    )

    return None, False

if not (0.0 <= confidence <= 1.0):

    print(
        f"[MEMORY DB] Confidence out of range: "
        f"{confidence}"
    )

    return None, False

if confidence < CONFIDENCE_THRESHOLD:

    print(
        f"Memory rejected "
        f"(Confidence {confidence:.2f} < "
        f"threshold {CONFIDENCE_THRESHOLD:.2f}): "
        f"'{text}'"
    )

    return None, False

# =====================================================
# IMPORTANCE VALIDATION
# =====================================================

try:

    importance = int(importance)

except (TypeError, ValueError):

    print(
        "[MEMORY DB] Invalid importance value."
    )

    return None, False

if not (1 <= importance <= 10):

    print(
        f"[MEMORY DB] Importance out of range: "
        f"{importance}"
    )

    return None, False

   # =====================================================
   # SOURCE VALIDATION
   # =====================================================

 if not isinstance(source, str):

    print(
        "[MEMORY DB] Invalid source value."
    )

    return None, False

 source = source.strip()

 if not source:

    print(
        "[MEMORY DB] Memory source is empty."
    )

    return None, False

    # =====================================================
# TIMESTAMP VALIDATION
# =====================================================

if timestamp is None:

    timestamp = (
        datetime.now(timezone.utc)
        .replace(tzinfo=None)
        .isoformat()
    )

else:

    if not isinstance(timestamp, str):

        print(
            "[MEMORY DB] Invalid timestamp value."
        )

        return None, False

    timestamp = timestamp.strip()

    if not timestamp:

        print(
            "[MEMORY DB] Timestamp is empty."
        )

        return None, False

    try:

        datetime.fromisoformat(timestamp)

    except ValueError:

        print(
            "[MEMORY DB] Invalid timestamp format."
        )

        return None, False

    # =====================================================
    # COLLECTION
    # =====================================================

    collection = get_collection(category)
    

# =====================================================
# EMPTY COLLECTION CHECK
# =====================================================

if collection.count() == 0:

    memory_id = str(uuid.uuid4())

    metadata = {
        "category": category,
        "importance": importance,
        "confidence": confidence,
        "timestamp": timestamp,
        "source": source
    }

    try:

        collection.add(
            documents=[text],
            ids=[memory_id],
            metadatas=[metadata]
        )

    except Exception as e:

        print(
            f"[MEMORY DB] Failed to store memory: {e}"
        )

        return None, False

    return memory_id, False
	



	

    # =====================================================
    # DUPLICATE DETECTION
    # =====================================================

    if distance_threshold is None:
        distance_threshold = DUPLICATE_DISTANCE_THRESHOLD

    try:
        results = collection.query(
            query_texts=[text],
            n_results=1
        )
    except Exception as e:
        print(
            f"[MEMORY DB] Duplicate check failed: {e}"
        )
        return None, False

    is_update = False
    existing_id = None

    if (
        results
        and results.get("distances")
        and results.get("ids")
        and len(results["distances"]) > 0
        and len(results["distances"][0]) > 0
        and len(results["ids"]) > 0
        and len(results["ids"][0]) > 0
    ):

# =====================================================
# EXISTING MEMORY QUALITY CHECK
# =====================================================

if distance < distance_threshold:

    existing_id = matched_id

    existing_metadata = {}

    if results.get("metadatas"):

        if (
            len(results["metadatas"]) > 0
            and len(results["metadatas"][0]) > 0
            and results["metadatas"][0][0]
        ):
            existing_metadata = (
                results["metadatas"][0][0]
            )

    try:

        existing_confidence = float(
            existing_metadata.get(
                "confidence",
                0.0
            )
        )

    except (TypeError, ValueError):

        existing_confidence = 0.0

    try:

        existing_importance = int(
            existing_metadata.get(
                "importance",
                0
            )
        )

    except (TypeError, ValueError):

        existing_importance = 0

    # =================================================
    # PREVENT MEMORY QUALITY DEGRADATION
    # =================================================

    if (
        confidence >= existing_confidence
        and importance >= existing_importance
    ):

        is_update = True

    else:

        # Keep the stronger existing memory.
        return existing_id, False

    # =====================================================
    # MEMORY METADATA
    # =====================================================

    metadata = {
        "category": category,
        "importance": importance,
        "confidence": confidence,
        "timestamp": timestamp,
        "source": source
    }

    # =====================================================
    # UPDATE / INSERT
    # =====================================================
     
     try:

    if is_update:

        memory_id = existing_id

        collection.update(
            ids=[memory_id],
            documents=[text],
            metadatas=[metadata]
        )

    else:

        memory_id = str(uuid.uuid4())

        collection.add(
            documents=[text],
            ids=[memory_id],
            metadatas=[metadata]
        )

except Exception as e:

    print(
        f"[MEMORY DB] Failed to store memory: {e}"
    )

    return None, False
    

    # =====================================================
    # RESULT
    # =====================================================

    return memory_id, is_update
# =====================================================
# MEMORY SEARCH
# =====================================================

def search_collection(
    category: str,
    query: str,
    n_results: int = 5
):
    """
    Searches a specific memory collection using semantic similarity.

    Returns:
        ChromaDB query results.

    Returns None if the query cannot be executed.
    """

    # =====================================================
    # INPUT VALIDATION
    # =====================================================

    if not isinstance(query, str) or not query.strip():
        return None

    query = query.strip()

    # =====================================================
    # RESULT LIMIT
    # =====================================================

    try:
        n_results = int(n_results)
    except (TypeError, ValueError):
        n_results = 5

    if n_results < 1:
        n_results = 1

    # =====================================================
    # COLLECTION
    # =====================================================

    try:
        collection = get_collection(category)
    except ValueError as e:
        print(f"[MEMORY DB] {e}")
        return None

    # =====================================================
    # SEARCH
    # =====================================================

  try:

    collection_size = collection.count()

    if collection_size == 0:
        return None

    n_results = min(
        n_results,
        collection_size
    )

    result = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return result

except Exception as e:

    print(
        f"[MEMORY DB] Search failed "
        f"in '{category}': {e}"
    )

    return None
# =====================================================
# DELETE MEMORY BY ID
# =====================================================

def delete_memory_by_id(
    mem_id: str
):
    """
    Deletes a memory by its ID across all collections.

    Returns:
        (True, category, text) if deleted successfully.
        (False, None, None) if the memory was not found.
    """

    # =====================================================
    # INPUT VALIDATION
    # =====================================================

    if not isinstance(mem_id, str) or not mem_id.strip():
        return False, None, None

    mem_id = mem_id.strip()

    # =====================================================
    # SEARCH ALL COLLECTIONS
    # =====================================================

    for category, collection in COLLECTIONS.items():

        try:

            results = collection.get(
                ids=[mem_id]
            )

            ids = results.get("ids", [])

            if not ids:
                continue

            documents = results.get(
                "documents",
                []
            )

            text = (
                documents[0]
                if documents
                else ""
            )

            # =================================================
            # DELETE
            # =================================================

            collection.delete(
                ids=[mem_id]
            )

            return True, category, text

        except Exception as e:

            print(
                f"[MEMORY DB] Error checking "
                f"collection '{category}' "
                f"for ID '{mem_id}': {e}"
            )

            # Continue checking other collections.
            continue

    # =====================================================
    # NOT FOUND
    # =====================================================

    return False, None, None

# =====================================================
# DELETE MEMORY BY SEMANTIC QUERY
# =====================================================

def delete_memory_by_query(
    query: str,
    distance_threshold: float | None = None
):
    """
    Deletes the closest semantic memory matching a query
    across all memory collections.

    Returns:
        (True, category, text, distance)
        if a sufficiently close memory is deleted.

        (False, None, None, None)
        if no suitable memory is found.
    """

    # =====================================================
    # INPUT VALIDATION
    # =====================================================

    if not isinstance(query, str) or not query.strip():
        return False, None, None, None

    query = query.strip()
    # =====================================================
    # DELETE DISTANCE THRESHOLD
    # =====================================================

    if distance_threshold is None:

        distance_threshold = (
            DELETE_DISTANCE_THRESHOLD
        )

    try:

        distance_threshold = float(
            distance_threshold
        )

    except (TypeError, ValueError):

        print(
            "[MEMORY DB] Invalid delete "
            "distance threshold."
        )

        return False, None, None, None

    if not math.isfinite(
        distance_threshold
    ):

        print(
            "[MEMORY DB] Delete distance "
            "threshold is not finite."
        )

        return False, None, None, None

    if distance_threshold < 0:

        print(
            "[MEMORY DB] Delete distance "
            "threshold cannot be negative."
        )

        return False, None, None, None
    # =====================================================
    # FIND CLOSEST MEMORY
    # =====================================================

    best_match = None
    best_distance = float("inf")

    for category, collection in COLLECTIONS.items():

        try:

            results = collection.query(
                query_texts=[query],
                n_results=1
            )

            if not results:
                continue

            ids = results.get("ids", [])
            documents = results.get("documents", [])
            distances = results.get("distances", [])

            if (
                not ids
                or not ids[0]
                or not documents
                or not documents[0]
                or not distances
                or not distances[0]
            ):
                continue

            mem_id = ids[0][0]
            text = documents[0][0]
            distance = float(distances[0][0])
            
 	if not math.isfinite(distance):
    	continue


         if distance < best_distance:

	best_distance = distance

	best_match = (
         category,
         mem_id,
          text
                )

        except Exception as e:

            print(
                f"[MEMORY DB] Error querying "
                f"'{category}' for deletion: {e}"
            )

            continue

    # =====================================================
    # SAFETY CHECK
    # =====================================================

    if (
        best_match is None
        or best_distance >= distance_threshold
    ):
        return False, None, None, None

    # =====================================================
    # DELETE MATCH
    # =====================================================

    category, mem_id, text = best_match

    try:

        collection = COLLECTIONS[category]

        collection.delete(
            ids=[mem_id]
        )

    except Exception as e:

        print(
            f"[MEMORY DB] Failed to delete "
            f"memory '{mem_id}': {e}"
        )

        return False, None, None, None

    # =====================================================
    # SUCCESS
    # =====================================================

    return (
        True,
        category,
        text,
        best_distance
    )

# =====================================================
# GET ALL MEMORIES
# =====================================================

def get_all_memories():
    """
    Retrieves all memories across all collections.

    Returns:
        {
            "profile_memory": [...],
            "project_memory": [...],
            "preference_memory": [...],
            "research_memory": [...]
        }

    Each memory contains:
        - id
        - text
        - importance
        - confidence
        - source
        - timestamp
    """

    all_memories = {}

    # =====================================================
    # COLLECTION TRAVERSAL
    # =====================================================

    for category, collection in COLLECTIONS.items():

        try:

            result = collection.get()

            memory_list = []

            ids = result.get("ids", [])
            documents = result.get("documents", [])
            metadatas = result.get("metadatas", [])

            # =================================================
            # MEMORY EXTRACTION
            # =================================================

            for index, memory_id in enumerate(ids):

                text = (
                    documents[index]
                    if index < len(documents)
                    else ""
                )

                metadata = (
                    metadatas[index]
                    if index < len(metadatas)
                    and metadatas[index]
                    else {}
                )

                memory_list.append({
                    "id": memory_id,
                    "text": text,
                    "importance": metadata.get(
                        "importance",
                        5
                    ),
                    "confidence": metadata.get(
                        "confidence",
                        1.0
                    ),
                    "source": metadata.get(
                        "source",
                        "conversation"
                    ),
                    "timestamp": metadata.get(
                        "timestamp",
                        ""
                    )
                })

            all_memories[category] = memory_list

        except Exception as e:

            print(
                f"[MEMORY DB] Error reading "
                f"collection '{category}': {e}"
            )

            # Keep the category present even if
            # one collection cannot be read.
            all_memories[category] = []

    # =====================================================
    # RESULT
    # =====================================================

    return all_memories

# =====================================================
# DUPLICATE MEMORY HEALTH CHECK
# =====================================================

def get_duplicate_candidates_count():
    """
    Counts near-duplicate memory pairs across all collections.

    A pair is considered a duplicate candidate when its
    semantic distance is below DUPLICATE_DISTANCE_THRESHOLD.

    Returns:
        Integer count of unique duplicate candidates.
    """

    duplicate_count = 0
    seen_pairs = set()

    # =====================================================
    # COLLECTION TRAVERSAL
    # =====================================================

    for category, collection in COLLECTIONS.items():

        try:

            result = collection.get()

            ids = result.get("ids", [])
            documents = result.get("documents", [])

            if len(ids) < 2:
                continue

            # =================================================
            # MEMORY COMPARISON
            # =================================================

            for index, document in enumerate(documents):

                if not document:
                    continue

                if index >= len(ids):
                    continue

                current_id = ids[index]

                try:

                    query_result = collection.query(
                        query_texts=[document],
                        n_results=2
                    )

                except Exception as e:

                    print(
                        f"[MEMORY DB] Duplicate query failed "
                        f"in '{category}': {e}"
                    )

                    continue

                distances = query_result.get(
                    "distances",
                    []
                )

                result_ids = query_result.get(
                    "ids",
                    []
                )

# ================================================		                             # RESULT VALIDATION
# =================================================

                if (
                    not distances
                    or not distances[0]
                    or len(distances[0]) < 2
                    or not result_ids
                    or not result_ids[0]
                    or len(result_ids[0]) < 2
                ):
                    continue

                distance = float(
                    distances[0][1]
                )

                neighbor_id = result_ids[0][1]

                # =================================================
                # DUPLICATE CHECK
                # =================================================

                if (
                    distance
                    < DUPLICATE_DISTANCE_THRESHOLD
                ):

                    pair = tuple(
                        sorted(
                            [current_id, neighbor_id]
                        )
                    )

                    if pair not in seen_pairs:

                        seen_pairs.add(pair)
                        duplicate_count += 1

        except Exception as e:

            print(
                f"[MEMORY DB] Error checking "
                f"duplicates in '{category}': {e}"
            )

            continue

    # =====================================================
    # RESULT
    # =====================================================

    return duplicate_count

# =====================================================
# LOW-CONFIDENCE MEMORY HEALTH CHECK
# =====================================================

def get_low_confidence_memories_count():
    """
    Counts memories whose stored confidence is below
    CONFIDENCE_THRESHOLD.

    Returns:
        Integer count of low-confidence memories.
    """

    low_confidence_count = 0

    # =====================================================
    # COLLECTION TRAVERSAL
    # =====================================================

    for category, collection in COLLECTIONS.items():

        try:

            result = collection.get()

            metadatas = result.get(
                "metadatas",
                []
            )

            # =================================================
            # CONFIDENCE CHECK
            # =================================================

            for metadata in metadatas:

                if not metadata:
                    continue

                raw_confidence = metadata.get(
                    "confidence",
                    1.0
                )

                try:

                    confidence = float(
                        raw_confidence
                    )

                except (TypeError, ValueError):

                    # Malformed confidence metadata
                    # is treated as low confidence.
                    low_confidence_count += 1
                    continue

                if (
                    confidence
                    < CONFIDENCE_THRESHOLD
                ):
                    low_confidence_count += 1

        except Exception as e:

            print(
                f"[MEMORY DB] Error checking "
                f"confidence in '{category}': {e}"
            )

            continue

    # =====================================================
    # RESULT
    # =====================================================

    return low_confidence_count
'''

import math
import uuid
from datetime import datetime, timezone
import chromadb

DB_PATH = "./semantic_memory/db"
COLLECTION_NAMES = ("profile_memory", "project_memory", "preference_memory", "research_memory")
CONFIDENCE_THRESHOLD = 0.80
DUPLICATE_DISTANCE_THRESHOLD = 0.35
DELETE_DISTANCE_THRESHOLD = 0.45
client = chromadb.PersistentClient(path=DB_PATH)
COLLECTIONS = {name: client.get_or_create_collection(name=name) for name in COLLECTION_NAMES}


def get_collection(category: str):
    if category not in COLLECTIONS:
        raise ValueError(f"Invalid memory category: {category}")
    return COLLECTIONS[category]


def add_memory(text, category, importance=5, confidence=1.0, timestamp=None,
               distance_threshold=None, source="conversation"):
    if not isinstance(text, str) or not text.strip() or category not in COLLECTIONS:
        return None, False
    try:
        confidence = float(confidence)
        importance = int(importance)
    except (TypeError, ValueError):
        return None, False
    if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0 or confidence < CONFIDENCE_THRESHOLD:
        return None, False
    if not 1 <= importance <= 10 or not isinstance(source, str) or not source.strip():
        return None, False
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    try:
        datetime.fromisoformat(timestamp)
    except (TypeError, ValueError):
        return None, False
    collection = COLLECTIONS[category]
    threshold = DUPLICATE_DISTANCE_THRESHOLD if distance_threshold is None else float(distance_threshold)
    existing_id = None
    if collection.count():
        try:
            result = collection.query(query_texts=[text.strip()], n_results=1)
            if result.get("ids") and result["ids"][0] and result.get("distances"):
                if result["distances"][0][0] < threshold:
                    existing_id = result["ids"][0][0]
        except Exception:
            return None, False
    memory_id = existing_id or str(uuid.uuid4())
    metadata = {"category": category, "importance": importance, "confidence": confidence, "timestamp": timestamp, "source": source.strip()}
    try:
        if existing_id:
            collection.update(ids=[memory_id], documents=[text.strip()], metadatas=[metadata])
        else:
            collection.add(ids=[memory_id], documents=[text.strip()], metadatas=[metadata])
    except Exception:
        return None, False
    return memory_id, bool(existing_id)


def search_collection(category, query, n_results=5):
    if not isinstance(query, str) or not query.strip():
        return None
    try:
        collection = get_collection(category)
        count = collection.count()
        return None if not count else collection.query(query_texts=[query.strip()], n_results=min(max(1, int(n_results)), count))
    except (TypeError, ValueError, Exception):
        return None


def delete_memory_by_id(mem_id):
    if not isinstance(mem_id, str) or not mem_id.strip():
        return False, None, None
    for category, collection in COLLECTIONS.items():
        try:
            result = collection.get(ids=[mem_id.strip()])
            if result.get("ids"):
                text = result.get("documents", [""])[0]
                collection.delete(ids=[mem_id.strip()])
                return True, category, text
        except Exception:
            continue
    return False, None, None


def delete_memory_by_query(query, distance_threshold=DELETE_DISTANCE_THRESHOLD):
    if not isinstance(query, str) or not query.strip():
        return False, None, None, None
    try:
        threshold = float(distance_threshold)
    except (TypeError, ValueError):
        return False, None, None, None
    best = None
    for category, collection in COLLECTIONS.items():
        try:
            result = collection.query(query_texts=[query.strip()], n_results=1)
            if result.get("ids") and result["ids"][0] and result.get("distances"):
                distance = float(result["distances"][0][0])
                if math.isfinite(distance) and (best is None or distance < best[3]):
                    best = (category, result["ids"][0][0], result["documents"][0][0], distance)
        except Exception:
            continue
    if best is None or best[3] >= threshold:
        return False, None, None, None
    category, memory_id, text, distance = best
    try:
        COLLECTIONS[category].delete(ids=[memory_id])
    except Exception:
        return False, None, None, None
    return True, category, text, distance


def get_all_memories():
    output = {}
    for category, collection in COLLECTIONS.items():
        try:
            result = collection.get()
            ids = result.get("ids", [])
            docs = result.get("documents", [])
            metas = result.get("metadatas", []) or []
            output[category] = [{"id": memory_id, "text": docs[i] if i < len(docs) else "", **(metas[i] if i < len(metas) and metas[i] else {})} for i, memory_id in enumerate(ids)]
        except Exception:
            output[category] = []
    return output


def get_duplicate_candidates_count():
    count = 0
    seen = set()
    for category, collection in COLLECTIONS.items():
        try:
            result = collection.get()
            ids = result.get("ids", [])
            docs = result.get("documents", [])
            for i, doc in enumerate(docs):
                query = collection.query(query_texts=[doc], n_results=2)
                if len(query.get("ids", [[]])[0]) < 2:
                    continue
                if query["distances"][0][1] < DUPLICATE_DISTANCE_THRESHOLD:
                    pair = tuple(sorted((ids[i], query["ids"][0][1])))
                    if pair not in seen:
                        seen.add(pair)
                        count += 1
        except Exception:
            continue
    return count


def get_low_confidence_memories_count():
    count = 0
    for memory in get_all_memories().values():
        for item in memory:
            try:
                if float(item.get("confidence", 1.0)) < CONFIDENCE_THRESHOLD:
                    count += 1
            except (TypeError, ValueError):
                count += 1
    return count
