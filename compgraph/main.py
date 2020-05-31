from typing import Dict, Any
from fastapi import FastAPI, Response
import compgraph.dag
import compgraph.commands

app = FastAPI()
app.include_router(compgraph.commands.router)

TEMPLATE_FIELD = "$Template"


# @app.post("/run_command")
# async def run_command(cc: dag.CommandCall):
#     body = {"input_data": cc.input_data}
#     resp = await http_client.post(url=cc.url, json=body)
#     resp.raise_for_status()
#     return resp


@app.post("/triggerProcess")
async def trigger_dag(data: Dict[str, Any]):
    data = dict(data)
    template = data.pop(TEMPLATE_FIELD)
    computable = compgraph.dag.build_dag(template)
    return computable(data)


@app.on_event("shutdown")
async def shutdown():
    await http_client.aclose()
