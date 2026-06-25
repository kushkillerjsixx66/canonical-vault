#!/usr/bin/env python3

VAULT_OP_ID = "@liminaljermo."

VALID_INTENTS = ["Commit", "Retrieve", "Review", "Canonize"]


def perimeter_state():
    print("VAULT PERIMETER")
    print("Awaiting acknowledgment.\n")
    user = input("> ").strip()
    if user == "I am at the perimeter.":
        return "INTENT"
    else:
        print("Unrecognized. The perimeter holds.\n")
        return "PERIMETER"


def intent_state(context):
    print("PERIMETER RECOGNIZED")
    print("State your intent.")
    print("Accepted intents: Commit · Retrieve · Review · Canonize\n")
    user = input("> ").strip()
    if user.startswith("Intent: "):
        intent = user[len("Intent: "):].strip(".").strip()
        if intent in VALID_INTENTS:
            context["intent"] = intent
            return "IDENTITY"
        else:
            print("Invalid intent.\n")
            return "INTENT"
    else:
        print("Intent required.\n")
        return "INTENT"


def identity_state():
    print("INTENT LOGGED")
    print("Identify yourself.")
    print("opID required for threshold access.\n")
    user = input("> ").strip()
    if user == f"opID: {VAULT_OP_ID}":
        return "THRESHOLD"
    else:
        print("Identity mismatch.\n")
        return "IDENTITY"


def threshold_state():
    print("IDENTITY VERIFIED")
    print("Approach the threshold.")
    print("Clarity is required for entry.\n")
    user = input("> ").strip()
    if user == "I cross with clarity.":
        return "INTERIOR"
    else:
        print("Clarity phrase required.\n")
        return "THRESHOLD"


def interior_state(context):
    print("\nTHE VAULT IS OPEN")
    print("State your first action.")
    print("Commit · Retrieve · Review · Canonize")
    print("All actions are logged to lineage.\n")

    # Simple action loop (stubbed for now)
    while True:
        action = input("> ").strip()
        if action.lower() in ["exit", "quit"]:
            print("\nPREPARING TO SEAL THE VAULT")
            print("State your closing phrase.\n")
            closing = input("> ").strip()
            if closing == "I leave with integrity.":
                print("\nVAULT SEALED")
                print("Perimeter restored.\n")
            else:
                print("\nClosing phrase not recognized. Vault remains in liminal state.\n")
            break
        else:
            print(f"[VAULT LOG] Action received: {action}")
            print(f"[VAULT LOG] Intent context: {context.get('intent', 'None')}\n")


def main():
    state = "PERIMETER"
    context = {}

    while True:
        if state == "PERIMETER":
            state = perimeter_state()
        elif state == "INTENT":
            state = intent_state(context)
        elif state == "IDENTITY":
            state = identity_state()
        elif state == "THRESHOLD":
            state = threshold_state()
        elif state == "INTERIOR":
            interior_state(context)
            break
        else:
            print("Invalid state. Exiting.")
            break


if __name__ == "__main__":
    main()
