"""
Coding problems added in v2, one module per topic.

Problems are written with `P(...)`: examples are given as real Python values
(arguments and expected result), which are rendered into the same text format
as the original content, *and* executed against the reference solution by
`apps/catalog/tests/test_coding_bank.py`. A wrong expected output therefore
fails the test suite instead of reaching students.

Argument/return types that aren't plain JSON values:
    types={"head": "list"}  → a linked list built from a Python list (ListNode)
    types={"root": "tree"}  → a binary tree from a level-order list with None gaps
    returns="list" | "tree" → convert the result back the same way
Design problems (a class with methods): examples are
    ({"calls": [("push", 1), ("top",)]}, [1])   — results of the calls that return something
Comparison: compare="unordered" (outer order doesn't matter),
            "groups" (neither outer nor inner order matters).
"""

import importlib
import json
import re
import textwrap

NEW_TOPICS = [
    {"slug": "hashing", "name": "Hashing", "description": "Hash maps and sets: constant-time membership, counting and grouping."},
    {"slug": "sorting", "name": "Sorting", "description": "Ordering data first so the rest of the problem becomes simple — and sorting algorithms themselves."},
    {"slug": "recursion-and-backtracking", "name": "Recursion & Backtracking", "description": "Solve a problem through smaller copies of itself; explore choices and undo them."},
    {"slug": "greedy", "name": "Greedy", "description": "Commit to the locally best choice when an exchange argument proves it is safe."},
]

TOPIC_MODULES = [
    "arrays", "strings", "two_pointers", "sliding_window", "prefix_sum", "binary_search", "linked_lists",
    "stack_and_queue", "trees_and_graphs", "dynamic_programming", "hashing", "sorting", "recursion", "greedy",
]


# --- rendering values the way the original content writes them ------------------------

def fmt(value) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, float):
        return f"{value:.1f}" if value.is_integer() else f"{value:.5f}".rstrip("0")
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(fmt(v) for v in value) + "]"
    return str(value)


def fmt_linked(values) -> str:
    return " → ".join(fmt(v) for v in values) if values else "(empty)"


def fmt_typed(value, kind) -> str:
    if kind == "list":
        return fmt_linked(value)
    if kind == "tree":
        return fmt(value)
    return fmt(value)


def render_call(call) -> str:
    name, *args = call
    return f"{name}({', '.join(fmt(a) for a in args)})"


class Problem(dict):
    """A content dict (what seed_content reads) that also keeps its executable examples."""


def P(slug, title, difficulty, patterns, *, statement, inputs, output, constraints, examples, approach, explanation,
      time, space, code, entry=None, types=None, returns=None, compare="exact", tests=()):
    types = types or {}
    rendered = []
    for args, expected, note in examples:
        if "calls" in args:
            text_in = ", ".join(render_call(c) for c in args["calls"])
            text_out = ", ".join(fmt(v) for v in expected)
        else:
            text_in = ", ".join(f"{k} = {fmt_typed(v, types.get(k))}" for k, v in args.items())
            text_out = fmt_typed(expected, returns)
        rendered.append({"input": text_in, "output": text_out, "explanation": note})
    body = textwrap.dedent(statement).strip()
    io = f"### Input\n{textwrap.dedent(inputs).strip()}\n\n### Output\n{textwrap.dedent(output).strip()}"
    code = textwrap.dedent(code).strip() + "\n"
    if entry is None:
        is_design = any("calls" in a for a, _, _ in examples)
        classes = [c for c in re.findall(r"^class (\w+)", code, re.M) if c not in ("ListNode", "TreeNode")]
        entry = classes[-1] if is_design else re.findall(r"^def (\w+)", code, re.M)[-1]
    problem = Problem(
        slug=slug, title=title, type="coding", difficulty=difficulty, patterns=list(patterns),
        statement=f"{body}\n\n{io}", constraints=textwrap.dedent(constraints).strip(), examples=rendered,
        approach=textwrap.dedent(approach).strip(), explanation=textwrap.dedent(explanation).strip(),
        time=time, space=space, solutions={"python": code},
    )
    problem.runnable = {
        "entry": entry, "types": types, "returns": returns, "compare": compare,
        "cases": [(a, e) for a, e, _ in examples] + list(tests),
    }
    return problem


def _modules():
    return [importlib.import_module(f"{__name__}.{name}") for name in TOPIC_MODULES]


def all_problems() -> dict[str, list[Problem]]:
    """topic slug → problems (each module declares TOPIC and PROBLEMS)."""
    out: dict[str, list[Problem]] = {}
    for module in _modules():
        out.setdefault(module.TOPIC, []).extend(module.PROBLEMS)
    return out


def questions_for(topic_slug: str) -> list[dict]:
    return [dict(p) for p in all_problems().get(topic_slug, [])]


# --- running reference solutions (tests and authoring) -----------------------------------

class _ListNode:
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next


class _TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def _to_linked(values, cls):
    head = None
    for v in reversed(values):
        head = cls(v, head)
    return head


def _from_linked(node, limit=10_000):
    out = []
    while node is not None and len(out) < limit:
        out.append(node.val)
        node = node.next
    return out


def _to_tree(values, cls):
    if not values or values[0] is None:
        return None
    nodes = [None if v is None else cls(v) for v in values]
    kids = iter(nodes[1:])
    for node in nodes:
        if node is None:
            continue
        node.left = next(kids, None)
        node.right = next(kids, None)
    return nodes[0]


def _from_tree(root):
    from collections import deque

    out, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        queue.extend([node.left, node.right])
    while out and out[-1] is None:
        out.pop()
    return out


def _normalise(value, compare):
    if compare == "unordered":
        return sorted(value, key=repr)
    if compare == "groups":
        return sorted((sorted(g, key=repr) for g in value), key=repr)
    if isinstance(value, float):
        return round(value, 5)
    return value


def run_problem(problem) -> list[str]:
    """Run every example/test case through the reference solution; return failure messages."""
    import copy

    spec = problem.runnable
    failures = []
    for args, expected in spec["cases"]:
        namespace = {"ListNode": _ListNode, "TreeNode": _TreeNode, "__name__": "kafka_reference"}
        exec(compile(problem["solutions"]["python"], f"<{problem['slug']}>", "exec"), namespace)
        target = namespace[spec["entry"]]
        list_cls, tree_cls = namespace["ListNode"], namespace["TreeNode"]
        try:
            if "calls" in args:
                obj, got = None, []
                for name, *call_args in args["calls"]:
                    if obj is None:
                        obj = target(*call_args)
                        continue
                    result = getattr(obj, name)(*copy.deepcopy(call_args))
                    if result is not None:
                        got.append(result)
            else:
                kwargs = {}
                for k, v in copy.deepcopy(args).items():
                    kind = spec["types"].get(k)
                    kwargs[k] = _to_linked(v, list_cls) if kind == "list" else _to_tree(v, tree_cls) if kind == "tree" else v
                got = target(**kwargs)
                if spec["returns"] == "list":
                    got = _from_linked(got)
                elif spec["returns"] == "tree":
                    got = _from_tree(got)
        except Exception as exc:  # noqa: BLE001 — report, don't crash the whole run
            failures.append(f"{problem['slug']}: {args} raised {exc!r}")
            continue
        if _normalise(got, spec["compare"]) != _normalise(expected, spec["compare"]):
            failures.append(f"{problem['slug']}: {args} → {got!r}, expected {expected!r}")
    return failures
