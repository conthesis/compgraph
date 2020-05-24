from typing import List, Dict, Any
from dataclasses import dataclass
from pydantic import BaseModel
from graphkit import compose, operation


class DagCommand(BaseModel):
    kind: str


class DagTemplateEntry(BaseModel):
    name: str
    inputs: List[str]
    command: DagCommand


class DagTemplate(BaseModel):
    name: str
    parameters: List[str]
    entries: List[DagTemplateEntry]


def trigger_dag_node(*args, **kwargs):
    name = kwargs.pop("$name")
    command = kwargs.pop("$command")
    return {"name": name, "command": command, "params": kwargs, "args": args}


def template_to_computable(template: DagTemplate):
    ops = []
    for entry in template.entries:
        op = operation(
            name=entry.name,
            needs=entry.inputs,
            provides=[entry.name],
            params={"$name": entry.name, "$command": entry.command},
        )(trigger_dag_node)
        ops.append(op)
    graph = compose(name=template.name)(*ops)
    return graph


def build_dag(x: Dict[str, Any]):

    template = DagTemplate.parse_obj(x)
    return template_to_computable(template)
