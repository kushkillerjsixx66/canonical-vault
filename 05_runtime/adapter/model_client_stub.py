# runtime/adapter/model_client_stub.py

class StubModelClient:
    def invoke(self, governed_prompt_envelope: dict) -> dict:
        # For now, just echo the user prompt as answer
        user_prompt = governed_prompt_envelope.get("user", "")
        return {
            "raw_output": f"[GOVERNED ANSWER] {user_prompt}",
            "reasoning": "stub-reasoning",
            "tools_used": []
        }
