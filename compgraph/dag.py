import asyncio
import inspect
from typing import Any, Dict, List

import httpx
from graphkit import compose, operation
from pydantic import BaseModel

http_client = httpx.Client()


class DagTemplateEntry(BaseModel):
    name: str
    inputs: List[str]
    action: str


class DagTemplate(BaseModel):
    name: str
    entries: List[DagTemplateEntry]


async def await_dict(d):
    return {k: await v if inspect.isawaitable(v) else v for (k, v) in d.items()}


def inputs_to_property_list(data: dict):
    for (k, v) in data.values():
        yield {"name": k, "kind": "LITERAL", "value": v}


async def perform_dag_step(inputs, entry):
    properties = list(inputs_to_property_list(inputs))
    res = await http_client.post(
        "http://actions:8000/internal/compute",
        json={kind: entry.action, properties: properties},
    )
    res.raise_for_status()
    return await res.json()


async def trigger_dag_node(*args, entry):
    infused_inputs = await await_dict(dict(zip(entry.inputs, args)))
    coro = perform_dag_step(infused_inputs, entry)
    return asyncio.create_task(coro)


def mkfuture(val):
    f = asyncio.get_event_loop().create_future()
    f.set_result(val)
    return f


async def graph_runner(graph):
    async def inner(data):
        future_args = {k: mkfuture(v) for (k, v) in data.items()}
        return await await_dict(graph(future_args))

    return inner


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
    return graph_runner(graph)


def build_dag(x: Dict[str, Any]):
    template = DagTemplate.parse_obj(x)
    return template_to_computable(template)
