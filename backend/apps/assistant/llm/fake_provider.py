"""
Offline provider: deterministic, free, no network. Used by tests and by local
development until an API key is configured. Its replies are clearly labelled
as demo output so nobody mistakes them for real tutoring.
"""

import re
import time
from collections.abc import Iterator

from .base import ChatTurn, Finished, LLMResult, StreamEvent, TextDelta


class FakeProvider:
    name = "fake"
    configured = True

    def __init__(self, *, model: str = "kafka-offline-demo", delay: float = 0.0):
        self.model = model
        self.delay = delay

    def stream(self, *, system: str, messages: list[ChatTurn], max_tokens: int) -> Iterator[StreamEvent]:
        question = re.search(r"^Title: (.+)$", system, re.M)
        mode = re.search(r"^MODE: (\w+)", system, re.M)
        level = re.search(r"^HINT LEVEL: (\d)", system, re.M)
        last = messages[-1].content if messages else ""

        lines = ["_Offline demo mode — set `LLM_PROVIDER=groq` and `GROQ_API_KEY` on the server for real answers._", ""]
        if question:
            lines.append(f"You're working on **{question.group(1)}**.")
        if mode and mode.group(1) == "hint":
            lines.append(f"Here is hint level {level.group(1) if level else 1}: think about which pattern fits the constraints.")
        elif mode and mode.group(1) == "explain":
            lines.append("Here's how the solution works, step by step.")
        elif mode and mode.group(1) == "review":
            lines.append("Let's look at why that option doesn't hold.")
        lines.append(f'You asked: "{last[:120]}"')
        reply = "\n".join(lines)

        for word in re.findall(r"\S+\s*", reply):
            if self.delay:
                time.sleep(self.delay)
            yield TextDelta(word)
        yield Finished(LLMResult(stop_reason="end_turn", model=self.model, input_tokens=0, output_tokens=len(reply.split())))

    def complete_json(
        self, *, system: str, prompt: str, schema: dict, name: str, max_tokens: int, effort: str | None = None
    ) -> tuple[dict, LLMResult]:
        """A schema-shaped demo object built offline (no network, deterministic).

        Strings are labelled as demo text, enums take their first values, and
        any `evidence` field quotes a real line from the <job_description>
        block in the prompt, so demo output passes the same validation as a
        real reply.
        """
        jd = re.search(r"<job_description>(.*?)</job_description>", prompt, re.S)
        lines = [ln.strip() for ln in (jd.group(1) if jd else "").splitlines() if len(ln.strip()) > 20]
        counter = iter(range(10_000))

        def build(node, key=""):
            kind = node.get("type")
            if isinstance(kind, list):  # nullable union → use the non-null type
                kind = next(k for k in kind if k != "null")
            if kind == "object":
                return {k: build(v, k) for k, v in node.get("properties", {}).items()}
            if kind == "array":
                items = node.get("items", {})
                if "enum" in items:
                    return list(items["enum"][:2])
                return [build(items, key) for _ in range(2)]
            if "enum" in node:
                return node["enum"][0]
            if kind == "boolean":
                return True
            if kind in ("number", "integer"):
                return 2
            if key == "evidence":
                return lines[next(counter) % len(lines)] if lines else ""
            if key in ("rejection_reason",):
                return ""
            return f"Offline demo {key.replace('_', ' ')} {next(counter) + 1}"

        data = build(schema)
        return data, LLMResult(stop_reason="end_turn", model=self.model, input_tokens=0, output_tokens=0)
