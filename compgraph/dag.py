from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from pydantic import BaseModel
from graphkit import compose, operation

from compgraph.commands import identity

import httpx

http_client = httpx.AsyncClient()


class DummyCommand(BaseModel):
    dummy: str
    dummy_2: int


class HttpCommand(BaseModel):
    url: str


class DagCommand(BaseModel):
    kind: str
    properties: Optional[Union[DummyCommand, HttpCommand]]


class DagTemplateEntry(BaseModel):
    name: str
    inputs: List[str]
    command: DagCommand


class DagTemplate(BaseModel):
    name: str
    entries: List[DagTemplateEntry]


def trigger_dag_node(*args, entry):
    infused_inputs = dict(zip(entry.inputs, args))

    if entry.command.kind == "identity":
        return identity(infused_inputs)

    if entry.command.kind == "http":
        body = {"data": infused_inputs}
        resp = http_client.post(url=entry.command.properties.url, json=body)
        resp.raise_for_status()
        resp.json()
        return resp.json()


def template_to_computable(template: DagTemplate):
    ops = []
    for entry in template.entries:
        op = operation(
            name=entry.name,
            needs=entry.inputs,
            provides=[entry.name],
            params={"entry": entry},
        )(trigger_dag_node)
        ops.append(op)
    graph = compose(name=template.name)(*ops)
    return graph


def build_dag(x: Dict[str, Any]):

    template = DagTemplate.parse_obj(x)
    return template_to_computable(template)
