from typing import Dict, Any
from fastapi import FastAPI, Response
from .dag import build_dag

app = FastAPI()

TEMPLATE_FIELD = "$Template"


@app.post("/triggerProcess")
async def trigger_dag(data: Dict[str, Any]):
    data = dict(data)
    template = data.pop(TEMPLATE_FIELD)
    computable = await build_dag(template)
    return await computable(data)


@app.on_event("shutdown")
async def shutdown():
    await http_client.aclose()
