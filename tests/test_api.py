import uuid

from fastapi.testclient import TestClient

import compgraph.main

client = TestClient(compgraph.main.app)


def test():
    payload = {
        "$Template": {
            "name": "foo",
            "parameters": ["a"],
            "entries": [
                {"name": "step1", "inputs": ["a"], "command": {"kind": "identity",}}
            ],
        },
        "a": "10",
    }
    res = client.post("/triggerProcess", json=payload)
    assert res.json() == {
        "a": "10",
        "step1": {
            "args": ["10"],
            "command": {"kind": "identity"},
            "name": "step1",
            "params": {},
        },
    }
