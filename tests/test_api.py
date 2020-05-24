import uuid

from fastapi.testclient import TestClient

import compgraph.main

client = TestClient(compgraph.main.app)


def test():
    payload = {
        "$Template": {
            "name": "foo",
            "entries": [
                {"name": "step1", "inputs": ["a"], "command": {"kind": "identity",}}
            ],
        },
        "a": "10",
    }
    res = client.post("/triggerProcess", json=payload)
    assert res.json() == {"a": "10", "step1": {"a": "10"}}
