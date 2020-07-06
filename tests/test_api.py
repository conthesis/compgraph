# from fastapi.testclient import TestClient
from compgraph.dag import dag
import pytest
import asyncio
import logging


def test_build_dag_error():
    payload = {
            "name": "foo",
            "entries": [
                {
                    "name": "step1",
                    "inputs": ["a", "b"],
                    "action": "eataduck"
                },
                {
                    "name": "step2",
                    "inputs": ["step2", "b"],
                    "action": "eataduck",
                    "dependencies": ["step1, step3"]
                }
            ],
        }
    from nats.aio.client import Client as NATS
    nc = NATS()
    with pytest.raises(RuntimeError):
        dag.Dag(payload, nc)


def test_compute_dag():
    payload = {
            "name": "foo",
            "entries": [
                {
                    "name": "step1",
                    "inputs": ["a", "b"],
                    "action": "na"
                },
                {
                    "name": "step2",
                    "inputs": ["step1"],
                    "action": "na",
                    "dependencies": ["step1"]
                },
                {
                    "name": "step3",
                    "inputs": ["step1", "b"],
                    "action": "na",
                    "dependencies": ["step1"]
                },
                {
                    "name": "step4",
                    "inputs": ["step3"],
                    "action": "na",
                    "dependencies": ["step2"]
                }
            ],
        }
    inputs = {"a": "na", "b":"na"}


    from nats.aio.client import Client as NATS
    nc = NATS()
    my_dag = dag.Dag(payload, nc)
    results = asyncio.run(my_dag.compute(inputs))

    print(results)

    assert my_dag.levels[1][0].name == "step2"
    assert my_dag.levels[1][1].name == "step3"
    assert my_dag.levels[2][0].name == "step4"

    assert results['step1'] is not None
    assert results['step2'] is not None
    assert results['step3'] is not None
    assert results['step4'] is not None



