from typing import Dict, Any
from fastapi import FastAPI, Response
from pydantic import BaseModel
import compgraph.dag

app = FastAPI()

TEMPLATE_FIELD = "$Template"


@app.post("/triggerProcess")
async def trigger_dag(data: Dict[str, Any]):
    data = dict(data)
    template = data.pop(TEMPLATE_FIELD)
    computable = compgraph.dag.build_dag(template)
    return computable(data)


@app.on_event("startup")
async def startup():
    pass


@app.on_event("shutdown")
async def shutdown():
    pass
