from typing import List, Dict, Any
from dataclasses import dataclass
from pydantic import BaseModel
from graphkit import compose, operation


class DagCommand(BaseModel):
    kind: str
    url: str


class DagTemplateEntry(BaseModel):
    name: str
    inputs: List[str]
    command: DagCommand


class DagTemplate(BaseModel):
    name: str
    entries: List[DagTemplateEntry]


def trigger_dag_node(*args, entry):
    name = entry.name
    command = entry.command
    dict_args = dict(zip(entry.inputs, args))
    if command.kind == "identity":
        return dict_args

    return None


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
