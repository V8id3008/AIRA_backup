"""
A.I.R.A. Duplicate Detector
---------------------------

Checks whether a memory already exists.
"""


class DuplicateDetector:

    def is_duplicate(self, candidate, existing_memories):

        if not existing_memories:
            return False

        candidate_text = candidate["text"].strip().lower()

        for memory in existing_memories:

            if candidate_text == memory.strip().lower():
                return True

        return False