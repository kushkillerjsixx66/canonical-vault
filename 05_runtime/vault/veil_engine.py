# veil_engine.py

def apply_veil(path, level="partial"):
    with open(path, "r") as f:
        content = f.read()

    if level == "partial":
        return content[:50] + "\n...[VEILED]..."

    if level == "full":
        return "[REDACTED BY VEIL]"

    return content
