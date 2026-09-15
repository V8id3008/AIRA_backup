from memory.duplicate_detector import DuplicateDetector

detector = DuplicateDetector()

existing = [
    "User prefers Python.",
    "User owns RTX 4050 GPU.",
    "User is building A.I.R.A."
]

tests = [
    "User prefers Python.",
    "User likes Python.",
    "User owns RTX 4050 GPU.",
    "User uses Docker."
]

for t in tests:

    duplicate = detector.is_duplicate(
        {"text": t},
        existing
    )

    print(t)
    print("Duplicate:", duplicate)
    print("-" * 40)