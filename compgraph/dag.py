import asyncio
from typing import Any, Dict, List, Optional, Set, Tuple

import orjson
from nats.aio.client import Client as NATS
from pydantic import BaseModel

ACTION_TOPIC = "conthesis.actions.literal"


class DagTemplateEntry(BaseModel):
    name: str
    inputs: List[str]
    action: str
    dependencies: Optional[List[str]]

    def __hash__(self):
        return hash(self.name)


class DagTemplate(BaseModel):
    name: str
    # TODO: give DAG its own entry structure and make entries a dict for easier iteration
    entries: List[DagTemplateEntry]


class Dag:
    def __init__(self, template: Dict[str, Any], nc: NATS):
        self.nc = nc
        template = DagTemplate.parse_obj(template)
        self.name = template.name
        self.levels = self._build_levels(template.entries)
        super(Dag).__init__()

    def _build_levels(self, entries: List[DagTemplateEntry]):
        levels: List[List[DagTemplateEntry]] = []
        solved_dependencies: Set[DagTemplateEntry.name] = set()
        remaining = entries

        while len(remaining) != 0:
            level, remaining, solved_dependencies = self._build_level(
                remaining, solved_dependencies
            )
            if len(level) == 0 and len(remaining) != 0:
                raise RuntimeError(
                    "Dag cannot be built, there are dependencies not solved for entries: {}".format(
                        ", ".join([entry.name for entry in remaining])
                    )
                )
            levels.append(level)

        return levels

    def _build_level(
        self, remaining: List[DagTemplateEntry], solved_dependencies: Set[str]
    ) -> Tuple[List[DagTemplateEntry], List[DagTemplateEntry], Set[str]]:
        level, new_remaining = [], []
        new_solved_dependencies = solved_dependencies.copy()
        for entry in remaining:
            if entry.dependencies is None or all(
                dependency in solved_dependencies for dependency in entry.dependencies
            ):
                level.append(entry)
                new_solved_dependencies.add(entry.name)
            else:
                new_remaining.append(entry)

        return level, new_remaining, new_solved_dependencies

    async def compute(self, external_inputs: Dict[str, Any]):
        # results are inputs for the next level
        results = external_inputs.copy()
        for level in self.levels:
            level_results = await self._compute_level(level, results)
            print(level_results)
            # TODO: await?
            results.update(level_results)

        # TODO: when we introduce map filter on entries insted
        return {k: v for (k, v) in results.items() if k not in external_inputs}

    async def _get_entry_inputs(
        self, entry: DagTemplateEntry, level_inputs: Dict[str, Any]
    ):
        entry_inputs = {k: v for (k, v) in level_inputs.items() if k in entry.inputs}
        if not all(entry in entry_inputs for entry in entry.inputs):
            raise RuntimeError(
                "Entry {} is missing inputs: {}".format(
                    entry.name,
                    ", ".join(
                        [
                            input_
                            for input_ in entry.inputs
                            if input_ not in entry_inputs
                        ]
                    ),
                )
            )

        return entry_inputs

    async def _compute_level(
        self, level: List[DagTemplateEntry], level_inputs: Dict[str, Any]
    ) -> Dict[DagTemplateEntry, Any]:
        results = await asyncio.gather(
            *[
                self._compute_node(
                    entry, await self._get_entry_inputs(entry, level_inputs)
                )
                for entry in level
            ]
        )

        return dict(zip([entry.name for entry in level], results))

    async def _compute_node(self, entry, entry_inputs) -> Any:
        body = {
            "meta": {"TriggeredBy": "compgraph"},
            "action_source": "LITERAL",
            "action": {
                "kind": entry.action,
                "properties": [
                    {"name": k, "value": v, "kind": "LITERAL",}
                    for (k, v) in entry_inputs.values()
                ],
            },
        }

        return await self.nc.request(ACTION_TOPIC, orjson.dumps(body))
