from typing import Any, Dict

from fastapi import FastAPI

from .dag import build_dag

app = FastAPI()

TEMPLATE_FIELD = "$Template"


class DAGService:
    def __init__(self):
        pass

    async def shutdown(self):
        pass

    async def setup(self):
        pass


@app.post("/triggerProcess")
async def trigger_dag(data: Dict[str, Any]):
    data = dict(data)
    template = data.pop(TEMPLATE_FIELD)
    computable = await build_dag(template)
    return await computable(data)
