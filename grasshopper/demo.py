"""Run S1–S9 and print a one-screen table. Usage: python -m grasshopper.demo"""

from __future__ import annotations

import asyncio

from grasshopper.demo_scenarios import ORDER, run_scenario
from grasshopper.runtime import get_context


async def main() -> None:
    ctx = get_context()
    print(f"{'scenario':<8} {'status':<18} {'steps':<8} {'rate':<8} {'llm':<6} {'ms':<8}")
    for name, text, _expected in ORDER:
        approve = name != "S7"
        result = await run_scenario(ctx, text, approve=approve)
        rate = f"{result.success_rate * 100:.0f}%"
        print(
            f"{name:<8} {result.status.value:<18} {result.steps_ok}/{result.steps_total:<5} "
            f"{rate:<8} {result.llm_calls:<6} {result.duration_ms:<8}"
        )


if __name__ == "__main__":
    asyncio.run(main())
