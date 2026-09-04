# runtime/run_lattice.py

from runtime.adapter.canonical_adapter import LatticeRuntimeAdapter

if __name__ == "__main__":
    adapter = LatticeRuntimeAdapter()

    request = {
        "session_id": "test-session",
        "operator_posture": "OPERATOR",
        "intent": "analysis",
        "prompt": "Explain the purpose of the Lattice runtime.",
        "lattice": {
            "modules": ["IDE", "CCE", "CFC"],
            "constraints": ["NO_HARM", "NO_LEAKAGE"],
            "lineage": {"mode": "FULL", "visibility": "OPERATOR"},
            "eval_profile": ["DRIFT", "COHERENCE", "SAFETY"]
        }
    }

    response = adapter.run(request)
    print(response)
