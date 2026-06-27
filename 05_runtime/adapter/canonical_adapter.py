from runtime.adapter.model_client_stub import StubModelClient
from runtime.governance.engine import GovernanceEngine


class LatticeRuntimeAdapter:
    def __init__(self, model_client=None, governance_engine=None):
        self.model = model_client or StubModelClient()
        self.gov = governance_engine or GovernanceEngine(config={})

    def run(self, request_envelope: dict) -> dict:
        gco = self.gov.resolve_context(request_envelope)
        gpe = self._build_gpe(request_envelope, gco)
        mia = self.model.invoke(gpe)
        ioo = self._interpret_output(mia)
        er = self.gov.run_evals(ioo, gco)
        lb = self.gov.capture_lineage(
            request_envelope, gpe, mia, ioo, er, gco
        )
        pdo = self.gov.decide_policy(er, gco)
        return self._emit_response(ioo, er, lb, pdo)

    def _build_gpe(self, req: dict, gco: dict) -> dict:
        return {
            "system": f"Posture: {gco['posture']}; Constraints: {gco['constraints']}",
            "modules": {m: f"Module {m} active" for m in gco["modules"]},
            "user": req.get("prompt", ""),
            "tools": []
        }

    def _interpret_output(self, mia: dict) -> dict:
        return {
            "answer": mia.get("raw_output", ""),
            "reasoning": mia.get("reasoning", ""),
            "tools_used": mia.get("tools_used", [])
        }

    def _emit_response(self, ioo: dict, er: dict, lb: dict, pdo: dict) -> dict:
        return {
            "answer": ioo["answer"],
            "lineage": {
                "block_hash": lb["block_hash"],
                "module_trace": lb["module_trace"],
                "visibility": lb["visibility"]
            },
            "evals": er,
            "policy": pdo,
            "meta": {
                "adapter_version": "0.1.0",
                "model": "stub-model"
            }
        }
