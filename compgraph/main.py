import asyncio
import os
import traceback

import orjson
from nats.aio.client import Client as NATS

from dag import Dag

TEMPLATE_FIELD = "$Template"

ACTION_TOPIC = "conthesis.action.TriggerDAG"


class DAGService:
    def __init__(self):
        self.nc = NATS()
        self.shutdown_f = asyncio.get_running_loop().create_future()

    async def wait_for_shutdown(self):
        await self.shutdown_f

    async def shutdown(self):
        try:
            await self.nc.drain()
        finally:
            self.shutdown_f.set_result(True)

    async def setup(self):
        await self.nc.connect(os.environ["NATS_URL"])
        await self.nc.subscribe(ACTION_TOPIC, cb=self.handle_msg)

    async def reply(self, msg, data):
        reply = msg.reply
        if reply:
            serialized = orjson.dumps(data)
            await self.nc.publish(reply, serialized)

    async def handle_msg(self, msg):
        try:
            data = orjson.loads(msg.data)
            template = data.pop(TEMPLATE_FIELD)
            dag = Dag(template, self.nc)
            res = await dag.compute(data)
            await self.reply(msg, res)
        except Exception:
            traceback.print_exc()


async def main():
    ds = DAGService()
    await ds.setup()
    await ds.wait_for_shutdown()
