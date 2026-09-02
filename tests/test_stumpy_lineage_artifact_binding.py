import importlib

contracts = importlib.import_module("05_runtime.governance.contracts")
vault_module = importlib.import_module("05_runtime.vault")


def _chain():
    operator = contracts.ValidatedOperatorContext(
        operator_id="probe-operator",
        credential_id="probe-credential",
        authenticated_at=contracts.iso_now(),
        session_id="probe-session",
        signature="probe-signature",
    )
    intent = contracts.ValidatedIntent(
        kind="commit",
        scope=("vault",),
        nonce="probe-nonce",
        issued_at=contracts.iso_now(),
    )
    request = contracts.GovernedRequest(
        request_id="probe-request",
        operator=operator,
        intent=intent,
        input_payload={"content": "artifact-bound"},
        source_refs=(),
        requested_action="commit",
    )
    decision = contracts.GovernanceDecision.create("ALLOW", {}, (), (), {})
    transition = contracts.StateTransition(
        transition_id="probe-transition",
        prior_refs=(),
        operation="commit",
        payload_hash=request.payload_hash,
        decision_hash=decision.decision_hash,
        lineage_event_id="probe-lineage",
        request_id=request.request_id,
        intent_id=request.intent.intent_id,
        artifact_hash=request.artifact_hash,
    )
    lineage = contracts.LineageEvent(
        event_id="probe-lineage",
        timestamp=contracts.iso_now(),
        operator_id=operator.operator_id,
        transition_id=transition.transition_id,
        decision_hash=decision.decision_hash,
        input_hash=request.payload_hash,
        payload_hash=request.payload_hash,
        evaluator_versions={},
        request_id=request.request_id,
        intent_id=request.intent.intent_id,
        artifact_hash=request.artifact_hash,
    )
    return request, decision, transition, lineage


def test_constitutional_lineage_resolves_to_committed_artifact():
    request, decision, transition, lineage = _chain()
    vault = vault_module.CanonicalVault()
    receipt = vault.commit_transition(transition, decision, lineage, request.input_payload, request=request)
    node = vault.nodes[0]

    assert lineage.artifact_hash == request.artifact_hash == node["content_hash"]
    assert receipt.node_id == node["node_id"]


def test_tampered_artifact_identity_is_rejected():
    request, decision, transition, lineage = _chain()
    tampered = contracts.LineageEvent(
        event_id=lineage.event_id,
        timestamp=lineage.timestamp,
        operator_id=lineage.operator_id,
        transition_id=lineage.transition_id,
        decision_hash=lineage.decision_hash,
        input_hash=lineage.input_hash,
        payload_hash=lineage.payload_hash,
        evaluator_versions=lineage.evaluator_versions,
        request_id=lineage.request_id,
        intent_id=lineage.intent_id,
        artifact_hash=contracts.sha256_digest("tampered"),
    )

    assert not tampered.is_constitutionally_bound_to(transition, request, decision)
