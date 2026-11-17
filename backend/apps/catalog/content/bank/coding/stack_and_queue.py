from . import P

TOPIC = "stack-and-queue"

PROBLEMS = [
    P(
        "remove-adjacent-duplicates", "Remove Adjacent Duplicate Letters", "easy", ["stack"],
        statement="Repeatedly delete two **adjacent equal** letters from `s` until no such pair remains. Return the final string (it is unique).",
        inputs="- `s`: a lowercase string",
        output="The string after all removals.",
        constraints="- `1 <= s.length <= 10^5`",
        examples=[
            ({"s": "abbaca"}, "ca", "Remove 'bb' → 'aaca', then 'aa' → 'ca'."),
            ({"s": "azxxzy"}, "ay", ""),
        ],
        approach="Push letters onto a stack; if the incoming letter equals the top of the stack, pop instead of pushing. The stack is the answer.",
        explanation="A removal can expose a new adjacent pair (as in 'abba'); the stack top is always the letter that would become adjacent next, so one pass handles the chain reactions.",
        time="O(n)", space="O(n)",
        code="""
        def remove_duplicates(s: str) -> str:
            stack = []
            for ch in s:
                if stack and stack[-1] == ch:
                    stack.pop()
                else:
                    stack.append(ch)
            return "".join(stack)
        """,
    ),
    P(
        "backspace-compare", "Compare Strings With Backspaces", "easy", ["stack"],
        statement="In strings `s` and `t`, the character `#` means *backspace* (delete the previous character, if any). Return `true` if both strings produce the same text.",
        inputs="- `s`, `t`: strings of lowercase letters and `#`",
        output="`true` or `false`.",
        constraints="- `1 <= s.length, t.length <= 200`",
        examples=[
            ({"s": "ab#c", "t": "ad#c"}, True, "Both become 'ac'."),
            ({"s": "a#c", "t": "b"}, False, "'c' vs 'b'."),
        ],
        tests=[({"s": "a##c", "t": "#a#c"}, True)],
        approach="Type each string into a stack: push letters, pop on `#` (if the stack isn't empty). Compare the two stacks.",
        explanation="A stack models a text editor exactly. (An O(1)-space version walks both strings from the end, counting pending backspaces.)",
        time="O(m + n)", space="O(m + n)",
        code="""
        def backspace_compare(s: str, t: str) -> bool:
            def typed(text: str) -> list[str]:
                stack = []
                for ch in text:
                    if ch == "#":
                        if stack:
                            stack.pop()
                    else:
                        stack.append(ch)
                return stack

            return typed(s) == typed(t)
        """,
    ),
    P(
        "queue-from-two-stacks", "Queue From Two Stacks", "easy", ["stack"],
        statement="Implement a first-in-first-out queue `MyQueue` using only two stacks. Support `push(x)`, `pop()` (remove and return the front), `peek()` (return the front) and `empty()`.",
        inputs="- `MyQueue()`, then a sequence of method calls (`pop`/`peek` are only called on a non-empty queue)",
        output="The values returned by `pop`, `peek` and `empty`, in order.",
        constraints="- At most 100 calls",
        examples=[
            ({"calls": [("MyQueue",), ("push", 1), ("push", 2), ("peek",), ("pop",), ("empty",)]}, [1, 1, False], ""),
            ({"calls": [("MyQueue",), ("push", 5), ("pop",), ("empty",)]}, [5, True], ""),
        ],
        approach="Push into an `inbox` stack. When you need the front and the `outbox` stack is empty, move everything from `inbox` to `outbox` — reversing it — so the oldest element ends on top.",
        explanation="Each element is moved at most once from inbox to outbox, so every operation is O(1) amortised.",
        time="O(1) amortised per operation", space="O(n)",
        code="""
        class MyQueue:
            def __init__(self):
                self.inbox, self.outbox = [], []

            def push(self, x: int) -> None:
                self.inbox.append(x)

            def _shift(self) -> None:
                if not self.outbox:
                    while self.inbox:
                        self.outbox.append(self.inbox.pop())

            def pop(self) -> int:
                self._shift()
                return self.outbox.pop()

            def peek(self) -> int:
                self._shift()
                return self.outbox[-1]

            def empty(self) -> bool:
                return not self.inbox and not self.outbox
        """,
    ),
    P(
        "score-tally", "Score Tally With Corrections", "easy", ["stack"],
        statement="""
        Keep score from a list of `ops`:

        - an integer string: record that score;
        - `"+"`: record the sum of the previous two scores;
        - `"D"`: record double the previous score;
        - `"C"`: cancel (remove) the previous score.

        Return the sum of the recorded scores at the end.
        """,
        inputs="- `ops`: a list of strings (every operation is valid)",
        output="The total of the remaining scores.",
        constraints="- `1 <= ops.length <= 1000`",
        examples=[
            ({"ops": ["5", "2", "C", "D", "+"]}, 30, "Scores: 5, (2 cancelled), 10, 15 → 30."),
            ({"ops": ["5", "-2", "4", "C", "D", "9", "+", "+"]}, 27, ""),
        ],
        approach="Use a stack of scores: push numbers, push the computed value for `+` and `D`, pop for `C`. Sum the stack at the end.",
        explanation="Every operation looks only at the most recent scores, which is exactly what a stack exposes.",
        time="O(n)", space="O(n)",
        code="""
        def cal_points(ops: list[str]) -> int:
            stack = []
            for op in ops:
                if op == "+":
                    stack.append(stack[-1] + stack[-2])
                elif op == "D":
                    stack.append(2 * stack[-1])
                elif op == "C":
                    stack.pop()
                else:
                    stack.append(int(op))
            return sum(stack)
        """,
    ),
    P(
        "days-until-warmer", "Days Until a Warmer Day", "medium", ["monotonic-stack"],
        statement="For each day in `temps`, return how many days you must wait for a **strictly warmer** temperature, or `0` if none comes.",
        inputs="- `temps`: a list of daily temperatures",
        output="A list of waits, one per day.",
        constraints="- `1 <= temps.length <= 10^5`\n- `30 <= temps[i] <= 100`",
        examples=[
            ({"temps": [73, 74, 75, 71, 69, 72, 76, 73]}, [1, 1, 4, 2, 1, 1, 0, 0], ""),
            ({"temps": [30, 40, 50, 60]}, [1, 1, 1, 0], ""),
        ],
        approach="Keep a stack of indices of days still waiting, with temperatures decreasing from bottom to top. For each new day, pop every waiting day that is colder and set its answer to the index difference; then push today.",
        explanation="A day stays on the stack only while no warmer day has appeared. Each index is pushed and popped once, so the scan is linear.",
        time="O(n)", space="O(n)",
        code="""
        def daily_temperatures(temps: list[int]) -> list[int]:
            answer = [0] * len(temps)
            waiting = []
            for i, t in enumerate(temps):
                while waiting and temps[waiting[-1]] < t:
                    j = waiting.pop()
                    answer[j] = i - j
                waiting.append(i)
            return answer
        """,
    ),
    P(
        "simplify-file-path", "Simplify a File Path", "medium", ["stack"],
        statement="Convert an absolute Unix-style `path` to its canonical form: one leading `/`, single slashes between names, no trailing slash, `.` (current directory) removed and `..` going up one level (going up from `/` stays at `/`).",
        inputs="- `path`: an absolute path starting with `/`",
        output="The canonical path.",
        constraints="- `1 <= path.length <= 3000`",
        examples=[
            ({"path": "/home//foo/"}, "/home/foo", ""),
            ({"path": "/a/./b/../../c/"}, "/c", ""),
        ],
        tests=[({"path": "/../"}, "/"), ({"path": "/.../a"}, "/.../a")],
        approach="Split on `/`. Push each real name onto a stack, ignore empty parts and `.`, and pop on `..` when the stack isn't empty. Join the stack with `/`.",
        explanation="The stack holds the directories from the root to the current location; `..` simply removes the deepest one. Names like `...` are ordinary directory names.",
        time="O(n)", space="O(n)",
        code="""
        def simplify_path(path: str) -> str:
            stack = []
            for part in path.split("/"):
                if part in ("", "."):
                    continue
                if part == "..":
                    if stack:
                        stack.pop()
                else:
                    stack.append(part)
            return "/" + "/".join(stack)
        """,
    ),
    P(
        "decode-repeat-notation", "Decode Repeat Notation", "medium", ["stack"],
        statement="Decode a string where `k[text]` means `text` repeated `k` times. Brackets can be nested, e.g. `3[a2[c]]`.",
        inputs="- `s`: a valid encoded string (lowercase letters, digits and brackets)",
        output="The decoded string.",
        constraints="- `1 <= s.length <= 30`\n- `1 <= k <= 300`",
        examples=[
            ({"s": "3[a]2[bc]"}, "aaabcbc", ""),
            ({"s": "3[a2[c]]"}, "accaccacc", "Inner first: a2[c] = acc."),
        ],
        tests=[({"s": "2[abc]3[cd]ef"}, "abcabccdcdcdef")],
        approach="Scan with a stack of `(text so far, repeat count)`. Digits build the count; `[` pushes the current text and count and starts fresh; `]` pops and sets `text = previous + count × current`.",
        explanation="The stack remembers the context outside each bracket pair, so nested pairs are decoded innermost-first naturally.",
        time="O(length of output)", space="O(length of output)",
        code="""
        def decode_string(s: str) -> str:
            stack, current, k = [], "", 0
            for ch in s:
                if ch.isdigit():
                    k = k * 10 + int(ch)
                elif ch == "[":
                    stack.append((current, k))
                    current, k = "", 0
                elif ch == "]":
                    previous, repeat = stack.pop()
                    current = previous + current * repeat
                else:
                    current += ch
            return current
        """,
    ),
    P(
        "asteroid-collisions", "Asteroid Collisions", "medium", ["stack"],
        statement="Asteroids move along a line: the absolute value is the size, the sign the direction (positive = right). When two meet, the smaller explodes; equal sizes both explode. Asteroids moving the same way never meet. Return the asteroids left after all collisions.",
        inputs="- `asteroids`: a list of non-zero integers",
        output="The surviving asteroids, in order.",
        constraints="- `2 <= asteroids.length <= 10^4`",
        examples=[
            ({"asteroids": [5, 10, -5]}, [5, 10], "-5 hits 10 and explodes."),
            ({"asteroids": [8, -8]}, [], "Equal sizes: both explode."),
        ],
        tests=[({"asteroids": [10, 2, -5]}, [10]), ({"asteroids": [-2, -1, 1, 2]}, [-2, -1, 1, 2])],
        approach="Use a stack of survivors. A left-moving asteroid collides with right-moving ones on top of the stack: pop smaller ones, stop if the top is bigger, pop both if equal. Push it if it survives.",
        explanation="Only a right-moving asteroid followed by a left-moving one can collide, and the most recent right-mover is hit first — stack order.",
        time="O(n)", space="O(n)",
        code="""
        def asteroid_collision(asteroids: list[int]) -> list[int]:
            stack = []
            for a in asteroids:
                alive = True
                while alive and a < 0 and stack and stack[-1] > 0:
                    if stack[-1] < -a:
                        stack.pop()
                        continue
                    if stack[-1] == -a:
                        stack.pop()
                    alive = False
                if alive:
                    stack.append(a)
            return stack
        """,
    ),
    P(
        "remove-k-digits", "Smallest Number After Removing k Digits", "medium", ["monotonic-stack", "greedy"],
        statement="Remove exactly `k` digits from the number string `num` so that the remaining number is as small as possible. Return it without leading zeros (`\"0\"` if nothing is left).",
        inputs="- `num`: a string of digits without leading zeros\n- `k`: digits to remove",
        output="The smallest possible result as a string.",
        constraints="- `1 <= k <= num.length <= 10^5`",
        examples=[
            ({"num": "1432219", "k": 3}, "1219", "Remove 4, 3 and 2."),
            ({"num": "10200", "k": 1}, "200", "Remove the 1; leading zeros are dropped."),
        ],
        tests=[({"num": "10", "k": 2}, "0"), ({"num": "112", "k": 1}, "11")],
        approach="Build the answer on a stack. Before pushing a digit, pop larger digits from the top while you still have removals left. If removals remain at the end, cut them from the end. Strip leading zeros.",
        explanation="The leftmost digits matter most: whenever a smaller digit follows a larger one, deleting the larger one makes the number smaller. The stack keeps the digits non-decreasing.",
        time="O(n)", space="O(n)",
        code="""
        def remove_k_digits(num: str, k: int) -> str:
            stack = []
            for d in num:
                while k and stack and stack[-1] > d:
                    stack.pop()
                    k -= 1
                stack.append(d)
            if k:
                stack = stack[:-k]
            return "".join(stack).lstrip("0") or "0"
        """,
    ),
    P(
        "largest-histogram-rectangle", "Largest Rectangle in a Histogram", "hard", ["monotonic-stack"],
        statement="`heights[i]` is the height of bar `i` of a histogram; each bar is 1 wide. Return the area of the largest rectangle that fits inside the histogram.",
        inputs="- `heights`: a list of non-negative integers",
        output="The largest rectangle area.",
        constraints="- `1 <= heights.length <= 10^5`\n- `0 <= heights[i] <= 10^4`",
        examples=[
            ({"heights": [2, 1, 5, 6, 2, 3]}, 10, "Bars 5 and 6 give 5 × 2 = 10."),
            ({"heights": [2, 4]}, 4, ""),
        ],
        tests=[({"heights": [2, 2, 2]}, 6), ({"heights": [0]}, 0)],
        approach="Keep a stack of bar indices with increasing heights. When a lower bar arrives, pop taller bars: each popped bar's rectangle extends from just after the new stack top to just before the current index. Use a 0-height sentinel at the end to flush the stack.",
        explanation="For every bar the stack finds its nearest lower bar on both sides at the moment it is popped — those are the edges of the widest rectangle using that bar's full height.",
        time="O(n)", space="O(n)",
        code="""
        def largest_rectangle(heights: list[int]) -> int:
            stack, best = [], 0
            for i, h in enumerate(heights + [0]):
                while stack and heights[stack[-1]] >= h:
                    height = heights[stack.pop()]
                    left = stack[-1] + 1 if stack else 0
                    best = max(best, height * (i - left))
                stack.append(i)
            return best
        """,
    ),
    P(
        "expression-calculator", "Calculator With Parentheses", "hard", ["stack"],
        statement="Evaluate a valid expression `s` containing non-negative integers, `+`, `-`, parentheses and spaces. A `-` may also be unary (e.g. `-(2+3)`). Don't use `eval`.",
        inputs="- `s`: a valid expression",
        output="The integer result.",
        constraints="- `1 <= s.length <= 3 × 10^5`\n- Every intermediate result fits in a 32-bit integer",
        examples=[
            ({"s": " 2-1 + 2 "}, 3, ""),
            ({"s": "(1+(4+5+2)-3)+(6+8)"}, 23, ""),
        ],
        tests=[({"s": "-(2+3)"}, -5), ({"s": "1 - (5 - 6)"}, 2)],
        approach="Scan once with a running `result` and the `sign` of the next number. On `(`, push the current result and sign and start fresh; on `)`, finish the inner result, multiply by the pushed sign and add the pushed result.",
        explanation="With only `+` and `-`, a parenthesised group is just a signed sub-total. The stack saves the outer state, which handles any nesting depth in linear time.",
        time="O(n)", space="O(depth of nesting)",
        code="""
        def calculate(s: str) -> int:
            stack, result, number, sign = [], 0, 0, 1
            for ch in s:
                if ch.isdigit():
                    number = number * 10 + int(ch)
                elif ch in "+-":
                    result += sign * number
                    number, sign = 0, (1 if ch == "+" else -1)
                elif ch == "(":
                    stack.append((result, sign))
                    result, sign = 0, 1
                elif ch == ")":
                    result += sign * number
                    number = 0
                    outer, outer_sign = stack.pop()
                    result = outer + outer_sign * result
            return result + sign * number
        """,
    ),
]
