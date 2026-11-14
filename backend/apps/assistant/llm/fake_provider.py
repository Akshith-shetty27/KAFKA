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
