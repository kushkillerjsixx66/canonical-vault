from ..vault_chain import VaultChain


def test_vault_chain_append_and_load(tmp_path):
    chain = VaultChain(root=tmp_path)

    entry = {
        "seq": 1,
        "operator_id": "op",
        "role": "root",
        "altitude": "runtime",
    }

    chain.append(entry)
    loaded = chain.load(1)

    assert loaded["seq"] == 1
    assert chain.verify_entry(loaded)
    assert chain.verify_continuity()
