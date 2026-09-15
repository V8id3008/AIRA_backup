from memory.validator import MemoryValidator

validator = MemoryValidator()

tests = [

    {
        "text": "User prefers Python for AI development.",
        "confidence": 0.95
    },

    {
        "text": "The user's name is A.I.R.A.",
        "confidence": 0.99
    },

    {
        "text": "My name is A.I.R.A.",
        "confidence": 0.99
    },

    {
        "text": "Installing requirements.txt",
        "confidence": 0.95
    },

    {
        "text": "",
        "confidence": 0.95
    },

    {
        "text": "Python",
        "confidence": 0.95
    },

    {
        "text": "User is building A.I.R.A.",
        "confidence": 0.99
    },

    {
        "text": "Project A.I.R.A. uses ChromaDB.",
        "confidence": 0.99
    },

    {
        "text": "User owns an RTX 4050 GPU.",
        "confidence": 0.96
    }

]

for memory in tests:

    accepted, reason = validator.validate(memory)

    print("=" * 60)
    print(memory["text"])
    print("Accepted :", accepted)
    print("Reason   :", reason)