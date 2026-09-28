"""Multi-model council: parallel answers, three critique rounds, devil's advocate, vote."""

from __future__ import annotations

import asyncio
from pathlib import Path

from grasshopper.providers.factory import build_llm
from grasshopper.providers.llm_mock import MockLLM


class Council:
    def __init__(self, settings, runs_dir: Path):
        self.settings = settings
        self.runs_dir = Path(runs_dir)
        self.calls = 0

    def _model(self, name: str):
        if name.startswith("mock_") or name == "mock":
            return MockLLM(name)
        provider = build_llm(name, self.settings, tier="strong")
        return provider

    async def _ask(self, model, prompt: str) -> str:
        self.calls += 1
        return await model.complete(prompt, tier="strong")

    async def run(self, question: str, *, run_id: str) -> dict:
        debaters = [self._model(name) for name in self.settings.council_providers]
        voters = [self._model(name) for name in self.settings.council_voters]
        lines = [f"# Council {run_id}", "", f"Question: {question}", ""]
        answers = list(await asyncio.gather(*[self._ask(model, question) for model in debaters]))
        lines.append("## Round 0 — independent answers")
        for model, answer in zip(debaters, answers):
            lines.append(f"### {model.name}\n{answer}\n")

        for round_index in range(1, 4):
            async def critique(index: int, model=None, answer=None):
                others = "\n".join(
                    f"{debaters[other].name}: {answers[other]}" for other in range(len(answers)) if other != index
                )
                prompt = (
                    f"You are {model.name}. Critique the other answers, name the weak points, "
                    f"and update your own idea.\nQuestion: {question}\nOthers:\n{others}\n"
                    f"Your previous idea: {answer}"
                )
                return await self._ask(model, prompt)

            answers = list(await asyncio.gather(*[
                critique(index, debaters[index], answers[index]) for index in range(len(debaters))
            ]))
            lines.append(f"## Round {round_index} — cross-critique")
            for model, answer in zip(debaters, answers):
                lines.append(f"### {model.name}\n{answer}\n")

        finals = list(await asyncio.gather(*[
            self._ask(model, f"Give one final idea only.\nQuestion: {question}\nYour notes: {answer}")
            for model, answer in zip(debaters, answers)
        ]))
        lines.append("## Final ideas")
        for model, answer in zip(debaters, finals):
            lines.append(f"### {model.name}\n{answer}\n")

        advocate = self._model("mock_e")
        attack = await self._ask(
            advocate,
            "Write a devil's advocate paragraph that starts with why this cannot win because the demo "
            f"might need a paid key. Question: {question}\nIdeas:\n" + "\n".join(finals),
        )
        lines.append("## Devil's advocate\n" + attack + "\n")

        strengthened = list(await asyncio.gather(*[
            self._ask(
                model,
                f"A critic said: {attack}\nStrengthen your idea so it still wins offline.\nIdea: {idea}\n"
                "Reply with the single strongest revised idea.",
            )
            for model, idea in zip(debaters, finals)
        ]))
        lines.append("## Strengthened")
        for model, answer in zip(debaters, strengthened):
            lines.append(f"### {model.name}\n{answer}\n")

        synthesis_prompt = (
            "Synthesize these strengthened ideas into exactly 3 numbered options.\n"
            + "\n".join(f"{i+1}. {text}" for i, text in enumerate(strengthened))
        )
        synthesis = await self._ask(debaters[0], synthesis_prompt)
        options = _three_options(synthesis, strengthened)
        lines.append("## Synthesis\n" + "\n".join(f"{i+1}. {text}" for i, text in enumerate(options)) + "\n")

        votes = []
        vote_prompts = [
            self._ask(
                voter,
                "Vote for the single strongest option. Reply with VOTE: N where N is 1, 2, or 3.\n"
                + "\n".join(f"{i+1}. {text}" for i, text in enumerate(options)),
            )
            for voter in voters
        ]
        ballots = await asyncio.gather(*vote_prompts)
        tally = [0, 0, 0]
        for ballot in ballots:
            choice = _parse_vote(ballot)
            tally[choice] += 1
            votes.append(choice + 1)
        winner_index = max(range(3), key=lambda index: tally[index])
        winner = options[winner_index]
        lines.append(f"## Votes\nballots={votes} tally={tally}\n\n## Winner\n{winner}\n")

        out = self.runs_dir / run_id / "council.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines), encoding="utf-8")
        return {
            "winner": winner,
            "options": options,
            "tally": tally,
            "path": str(out),
            "calls": self.calls,
        }


def _three_options(synthesis: str, fallback: list[str]) -> list[str]:
    lines = [line.strip() for line in synthesis.splitlines() if line.strip()]
    numbered = []
    for line in lines:
        if line[:2] in {"1.", "2.", "3.", "1)", "2)", "3)"}:
            numbered.append(line[2:].strip())
    while len(numbered) < 3:
        source = fallback[len(numbered) % max(1, len(fallback))]
        numbered.append(source)
    return numbered[:3]


def _parse_vote(text: str) -> int:
    for token in ("3", "2", "1"):
        if f"VOTE: {token}" in text.upper() or f"VOTE:{token}" in text.upper():
            return int(token) - 1
    if "VOTE: 1" in text:
        return 0
    return 0
