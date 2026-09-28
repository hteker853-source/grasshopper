"""python -m grasshopper.cli \"task text\""""

from __future__ import annotations

import asyncio
import sys

from grasshopper.runtime import get_context


async def _run(text: str) -> int:
    ctx = get_context()
    task = ctx.orchestrator.accept(text, channel="cli")
    if task.scheduled_at:
        delay = max(0.0, (task.scheduled_at - task.created_at).total_seconds())
        print(f"scheduled {task.id} in {delay:.0f}s")
        await asyncio.sleep(delay + 0.2)
    result = await ctx.orchestrator.execute(task.id)
    print(result.model_dump_json(indent=2))
    return 0 if result.status.value in {"done", "waiting_approval"} else 1


def main() -> None:
    text = " ".join(sys.argv[1:]).strip()
    if not text:
        print('Usage: python -m grasshopper.cli "task text"')
        raise SystemExit(2)
    raise SystemExit(asyncio.run(_run(text)))


if __name__ == "__main__":
    main()
