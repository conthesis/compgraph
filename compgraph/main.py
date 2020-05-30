import httpx
from typing import Dict, Any
from fastapi import FastAPI, Response
import compgraph.dag

app = FastAPI()
http_client = httpx.AsyncClient()

TEMPLATE_FIELD = "$Template"


@app.post("/run_command")
async def run_command(entry: compgraph.dag.DagTemplateEntry):
    body = {'inputs': entry.inputs}
    resp = await http_client.post(url=entry.command.url, json=body)
    resp.raise_for_status()
    return resp


@app.post("/triggerProcess")
async def trigger_dag(data: Dict[str, Any]):
    data = dict(data)
    template = data.pop(TEMPLATE_FIELD)
    computable = compgraph.dag.build_dag(template)
    return computable(data)


@app.on_event("shutdown")
async def shutdown():
    await http_client.aclose()
