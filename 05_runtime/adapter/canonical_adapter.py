# runtime/adapter/canonical_adapter.py

class LatticeRuntimeAdapter:
    def __init__(self, model_client, governance_engine):
        self.model = model_client
        self.gov = governance_engine

    def run(self, request_envelope: dict) -> dict:
        # 1. Governance context
        gco = self.gov.resolve_context(request_envelope)

        # 2. Governed prompt envelope
        gpe = self._build_gpe(request_envelope, gco)

        # 3. Model invocation
        mia = self.model.invoke(gpe)

        # 4. Output interpretation
        ioo = self._interpret_output(mia)

        # 5. Evals
        er = self.gov.run_evals(ioo, gco)

        # 6. Lineage block
        lb = self.gov.capture_lineage(
            request_envelope, gpe, mia, ioo, er, gco
        )

        # 7. Policy decision
        pdo = self.gov.decide_policy(er, gco)

        # 8. Governed response envelope
        return self._emit_response(ioo, er, lb, pdo)

    def _build_gpe(self, req: dict, gco: dict) -> dict:
        # TODO: compose system + modules + user prompt
        raise NotImplementedError

    def _interpret_output(self, mia: dict) -> dict:
        # TODO: split answer / reasoning / tool calls
        raise NotImplementedError

    def _emit_response(self, ioo: dict, er: dict, lb: dict, pdo: dict) -> dict:
        # TODO: construct governed response envelope
        raise NotImplementedError
