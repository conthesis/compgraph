import uuid

from fastapi.testclient import TestClient

from compgraph import main
from compgraph import dag

client = TestClient(main.app)


def test():
    payload = {
        "$Template": {
            "name": "foo",
            "entries": [
                {"name": "step1", "inputs": ["a"], "command": {"kind": "identity"}}
            ],
        },
        "a": "10",
    }
    res = client.post("/triggerProcess", json=payload)
    assert res.json() == {"a": "10", "step1": {"a": "10"}}


def test_url_command():
    data = {
        "name": "foo",
        "entries": [
            {"name": "step1",
             "inputs": ["a,b"],
             "command":
                {
                 "kind": "http",
                 "properties": {"url": "http://127.0.0.1:8000/add"}
                }
             }
        ],
    }
    data_parsed = dag.DagTemplate.parse_obj(data)
    assert type(data_parsed.entries[0].command.properties) == dag.HttpCommand
    assert data_parsed.entries[0].command.properties.url == "http://127.0.0.1:8000/add"


def test_add():
    payload = {
        "$Template": {
            "name": "foo",
            "entries": [
                {"name": "step1",
                 "inputs": ["a", "b"],
                 "command":
                    {
                     "kind": "http",
                     "properties": {"url": "http://127.0.0.1:8000/add"}
                    }
                }
            ],
        },
        "a": 10,
        "b": 20
    }
    res = client.post("/triggerProcess", json=payload)
    assert res.json() == {"a": 10, "b": 20, "step1": 30}
