from typing import List, Dict, Any, Optional
from fastapi import APIRouter

router = APIRouter()


def identity(data: Dict[str, Any]):
    return data


async def add(a: Any, b: Any):
    return a + b


@router.post("/add")
async def http_add(data: Dict[str, Any]):
    return await add(*data.values())


# async def add(a: Any, b: Any):
#     try:
#         return a+b
#     # what's the right thing to raise here?
#     except AttributeError:
#         print("Object does not hold __add__ attribute")
#         return None
