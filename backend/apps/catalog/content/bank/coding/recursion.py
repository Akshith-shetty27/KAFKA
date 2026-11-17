from . import P
from .hashing import BOARD

TOPIC = "recursion-and-backtracking"

SOLVED = [
    list("534678912"), list("672195348"), list("198342567"),
    list("859761423"), list("426853791"), list("713924856"),
    list("961537284"), list("287419635"), list("345286179"),
]
NEARLY = [row[:] for row in SOLVED]
for r, c in [(0, 0), (1, 4), (2, 8), (4, 4), (6, 0), (8, 8), (3, 3), (5, 6)]:
    NEARLY[r][c] = "."

PROBLEMS = [
    P(
        "power-of-three", "Is It a Power of Three?", "easy", ["recursion"],
        statement="Return `true` if `n` equals `3^k` for some integer `k ≥ 0`.",
        inputs="- `n`: an integer",
        output="`true` or `false`.",
        constraints="- `-2^31 <= n <= 2^31 - 1`",
        examples=[
            ({"n": 27}, True, "27 = 3³."),
            ({"n": 45}, False, "45 = 3² × 5."),
        ],
        tests=[({"n": 1}, True), ({"n": 0}, False), ({"n": -3}, False)],
        approach="Recursively: 1 is a power of three; any other `n` must be divisible by 3 with `n / 3` also a power of three. Non-positive numbers are never powers of three.",
        explanation="Each call divides by 3, so the recursion depth is about log₃ n. The base cases (≤ 0 and 1) stop it.",
        time="O(log n)", space="O(log n) for the recursion",
        code="""
        def is_power_of_three(n: int) -> bool:
            if n <= 0:
                return False
            if n == 1:
                return True
            return n % 3 == 0 and is_power_of_three(n // 3)
        """,
    ),
    P(
        "all-binary-strings", "All Binary Strings of Length n", "easy", ["recursion", "backtracking"],
        statement="Return every string of length `n` made of `0`s and `1`s, in ascending (lexicographic) order.",
        inputs="- `n`: a positive integer",
        output="A list of `2^n` strings.",
        constraints="- `1 <= n <= 12`",
        examples=[
            ({"n": 2}, ["00", "01", "10", "11"], ""),
            ({"n": 1}, ["0", "1"], ""),
        ],
        approach="Build strings one character at a time: from a prefix, recurse with `prefix + '0'` and then `prefix + '1'`. When the prefix reaches length `n`, record it.",
        explanation="Trying `0` before `1` at every position produces the strings in lexicographic order. This choose-then-recurse shape is the skeleton of every backtracking problem.",
        time="O(n · 2^n)", space="O(n) recursion besides the output",
        code="""
        def binary_strings(n: int) -> list[str]:
            out = []

            def build(prefix: str) -> None:
                if len(prefix) == n:
                    out.append(prefix)
                    return
                build(prefix + "0")
                build(prefix + "1")

            build("")
            return out
        """,
    ),
    P(
        "tower-of-hanoi", "Tower of Hanoi Moves", "easy", ["recursion"],
        statement="Move `n` discs from peg 1 to peg 3 using peg 2, moving one disc at a time and never placing a larger disc on a smaller one. Return the moves in order as `[from, to]` pairs, using the minimum number of moves.",
        inputs="- `n`: the number of discs",
        output="A list of `2^n − 1` moves.",
        constraints="- `1 <= n <= 10`",
        examples=[
            ({"n": 1}, [[1, 3]], ""),
            ({"n": 2}, [[1, 2], [1, 3], [2, 3]], "Small disc aside, big disc across, small disc on top."),
        ],
        tests=[({"n": 3}, [[1, 3], [1, 2], [3, 2], [1, 3], [2, 1], [2, 3], [1, 3]])],
        approach="To move `n` discs from A to C: move the top `n − 1` discs from A to B (using C), move the largest disc from A to C, then move the `n − 1` discs from B to C (using A).",
        explanation="The largest disc can only move when all others are on the spare peg, so this recursion is forced — and it gives the minimum 2ⁿ − 1 moves.",
        time="O(2^n)", space="O(n) recursion besides the output",
        code="""
        def hanoi(n: int) -> list[list[int]]:
            moves = []

            def move(k: int, src: int, dst: int, spare: int) -> None:
                if k == 0:
                    return
                move(k - 1, src, spare, dst)
                moves.append([src, dst])
                move(k - 1, spare, dst, src)

            move(n, 1, 3, 2)
            return moves
        """,
    ),
    P(
        "letter-case-variants", "All Letter-Case Variants", "easy", ["backtracking"],
        statement="Each letter of `s` can be lowercase or uppercase (digits stay as they are). Return all strings you can create, in any order.",
        inputs="- `s`: a string of letters and digits",
        output="A list of all variants.",
        constraints="- `1 <= s.length <= 12`",
        examples=[
            ({"s": "a1b2"}, ["a1b2", "a1B2", "A1b2", "A1B2"], ""),
            ({"s": "3z4"}, ["3z4", "3Z4"], ""),
        ],
        compare="unordered",
        approach="Recurse over positions: a digit has one option; a letter branches into its lower and upper case.",
        explanation="With L letters there are 2^L variants, and the recursion produces each exactly once.",
        time="O(n · 2^L)", space="O(n) recursion besides the output",
        code="""
        def letter_case_permutation(s: str) -> list[str]:
            out = []

            def go(i: int, built: str) -> None:
                if i == len(s):
                    out.append(built)
                    return
                if s[i].isalpha():
                    go(i + 1, built + s[i].lower())
                    go(i + 1, built + s[i].upper())
                else:
                    go(i + 1, built + s[i])

            go(0, "")
            return out
        """,
    ),
    P(
        "flatten-nested-list", "Flatten a Nested List", "easy", ["recursion"],
        statement="`nested` contains integers and lists, which may themselves contain integers and lists, to any depth. Return all the integers in order as a flat list.",
        inputs="- `nested`: a list of integers and nested lists",
        output="A flat list of integers.",
        constraints="- Total number of integers ≤ `10^4`; nesting depth ≤ 50",
        examples=[
            ({"nested": [1, [2, [3, 4]], 5]}, [1, 2, 3, 4, 5], ""),
            ({"nested": [[], [[]]]}, [], "Empty lists contribute nothing."),
        ],
        approach="For each item: if it is an integer, append it; if it is a list, flatten it recursively and append the results.",
        explanation="The recursion mirrors the structure of the data — each nested list is a smaller instance of the same problem.",
        time="O(total items)", space="O(depth) recursion besides the output",
        code="""
        def flatten(nested: list) -> list[int]:
            out = []
            for item in nested:
                if isinstance(item, list):
                    out.extend(flatten(item))
                else:
                    out.append(item)
            return out
        """,
    ),
    P(
        "all-subsets", "All Subsets", "medium", ["backtracking"],
        statement="Return all subsets (the power set) of the distinct integers `nums`, in any order. Each subset lists its elements in the order they appear in `nums`.",
        inputs="- `nums`: a list of distinct integers",
        output="A list of all `2^n` subsets.",
        constraints="- `1 <= nums.length <= 10`",
        examples=[
            ({"nums": [1, 2, 3]}, [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]], ""),
            ({"nums": [0]}, [[], [0]], ""),
        ],
        compare="groups",
        approach="Backtrack over positions: record the current subset, then for each later element, add it, recurse, and remove it again.",
        explanation="Only moving forward from the last chosen index means every subset is generated exactly once.",
        time="O(n · 2^n)", space="O(n) recursion besides the output",
        code="""
        def subsets(nums: list[int]) -> list[list[int]]:
            out, chosen = [], []

            def go(start: int) -> None:
                out.append(chosen[:])
                for i in range(start, len(nums)):
                    chosen.append(nums[i])
                    go(i + 1)
                    chosen.pop()

            go(0)
            return out
        """,
    ),
    P(
        "all-permutations", "All Permutations", "medium", ["backtracking"],
        statement="Return all permutations of the distinct integers `nums`, in any order.",
        inputs="- `nums`: a list of distinct integers",
        output="A list of all `n!` orderings.",
        constraints="- `1 <= nums.length <= 6`",
        examples=[
            ({"nums": [1, 2, 3]}, [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]], ""),
            ({"nums": [0, 1]}, [[0, 1], [1, 0]], ""),
        ],
        compare="unordered",
        approach="Build the permutation position by position: try every unused number, mark it used, recurse, then unmark it (backtrack).",
        explanation="Each level fixes one position, so the recursion tree has exactly n! leaves — one per permutation.",
        time="O(n · n!)", space="O(n) recursion besides the output",
        code="""
        def permute(nums: list[int]) -> list[list[int]]:
            out, current, used = [], [], [False] * len(nums)

            def go() -> None:
                if len(current) == len(nums):
                    out.append(current[:])
                    return
                for i, x in enumerate(nums):
                    if not used[i]:
                        used[i] = True
                        current.append(x)
                        go()
                        current.pop()
                        used[i] = False

            go()
            return out
        """,
    ),
    P(
        "combination-sum", "Combinations Adding Up to a Target", "medium", ["backtracking"],
        statement="Return all unique combinations of `candidates` (distinct positive integers, each usable **any number of times**) that sum to `target`. Combinations are listed with numbers in non-decreasing order; the list may be in any order.",
        inputs="- `candidates`: a list of distinct positive integers\n- `target`: a positive integer",
        output="A list of combinations.",
        constraints="- `1 <= candidates.length <= 30`\n- `1 <= target <= 40`",
        examples=[
            ({"candidates": [2, 3, 6, 7], "target": 7}, [[2, 2, 3], [7]], ""),
            ({"candidates": [2, 3, 5], "target": 8}, [[2, 2, 2, 2], [2, 3, 3], [3, 5]], ""),
        ],
        compare="groups",
        approach="Sort the candidates. Backtrack with a start index: at each step try candidates from `start` onward (allowing the same one again by recursing with the same index), and stop a branch as soon as the candidate exceeds the remaining target.",
        explanation="Never going back to earlier candidates prevents the same combination in different orders; sorting enables the early stop.",
        time="Exponential in target / min(candidate)", space="O(target) recursion",
        code="""
        def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
            candidates = sorted(candidates)
            out, chosen = [], []

            def go(start: int, remaining: int) -> None:
                if remaining == 0:
                    out.append(chosen[:])
                    return
                for i in range(start, len(candidates)):
                    c = candidates[i]
                    if c > remaining:
                        break
                    chosen.append(c)
                    go(i, remaining - c)
                    chosen.pop()

            go(0, target)
            return out
        """,
    ),
    P(
        "balanced-parentheses", "All Balanced Parentheses", "medium", ["backtracking"],
        statement="Return all strings of `n` pairs of correctly matched parentheses, in any order.",
        inputs="- `n`: the number of pairs",
        output="A list of strings.",
        constraints="- `1 <= n <= 8`",
        examples=[
            ({"n": 3}, ["((()))", "(()())", "(())()", "()(())", "()()()"], ""),
            ({"n": 1}, ["()"], ""),
        ],
        compare="unordered",
        approach="Build the string left to right, tracking how many `(` and `)` are used. You may add `(` while fewer than `n` are used, and `)` only while fewer `)` than `(` have been used.",
        explanation="These two rules exactly describe valid prefixes, so no invalid string is ever built — no generate-and-filter needed.",
        time="O(4^n / √n) (the Catalan numbers)", space="O(n) recursion besides the output",
        code="""
        def generate_parentheses(n: int) -> list[str]:
            out = []

            def go(built: str, opened: int, closed: int) -> None:
                if len(built) == 2 * n:
                    out.append(built)
                    return
                if opened < n:
                    go(built + "(", opened + 1, closed)
                if closed < opened:
                    go(built + ")", opened, closed + 1)

            go("", 0, 0)
            return out
        """,
    ),
    P(
        "phone-keypad-words", "Phone Keypad Letter Combinations", "medium", ["backtracking"],
        statement="On a phone keypad, 2 = abc, 3 = def, 4 = ghi, 5 = jkl, 6 = mno, 7 = pqrs, 8 = tuv, 9 = wxyz. Return every letter combination the digit string could represent, in any order (an empty input gives an empty list).",
        inputs="- `digits`: a string of digits 2–9 (possibly empty)",
        output="A list of letter strings.",
        constraints="- `0 <= digits.length <= 4`",
        examples=[
            ({"digits": "23"}, ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"], ""),
            ({"digits": ""}, [], ""),
        ],
        compare="unordered",
        approach="Recurse digit by digit, appending each possible letter for the current digit to the prefix built so far.",
        explanation="The recursion tree has one level per digit and one branch per letter, so it enumerates the Cartesian product of the letter groups.",
        time="O(4^n · n)", space="O(n) recursion besides the output",
        code="""
        KEYS = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}

        def letter_combinations(digits: str) -> list[str]:
            if not digits:
                return []
            out = []

            def go(i: int, built: str) -> None:
                if i == len(digits):
                    out.append(built)
                    return
                for ch in KEYS[digits[i]]:
                    go(i + 1, built + ch)

            go(0, "")
            return out
        """,
    ),
    P(
        "word-in-grid", "Find a Word in a Letter Grid", "medium", ["backtracking", "dfs"],
        statement="Return `true` if `word` can be traced in `board` by moving between horizontally or vertically adjacent cells, using each cell at most once.",
        inputs="- `board`: an `m × n` grid of letters\n- `word`: the word to find",
        output="`true` or `false`.",
        constraints="- `1 <= m, n <= 6`\n- `1 <= word.length <= 15`",
        examples=[
            ({"board": [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "word": "ABCCED"}, True, ""),
            ({"board": [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "word": "ABCB"}, False, "The B can't be reused."),
        ],
        tests=[({"board": [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "word": "SEE"}, True)],
        approach="Try every cell as a start. DFS from a cell matching the next letter: mark it as used, explore the four neighbours for the following letter, then unmark it (backtrack).",
        explanation="Marking cells during the current path enforces \"each cell once\"; unmarking lets other paths use them.",
        time="O(m·n·3^L)", space="O(L) recursion",
        code="""
        def exist(board: list[list[str]], word: str) -> bool:
            rows, cols = len(board), len(board[0])

            def dfs(r: int, c: int, i: int) -> bool:
                if i == len(word):
                    return True
                if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[i]:
                    return False
                saved, board[r][c] = board[r][c], "#"
                found = any(dfs(r + dr, c + dc, i + 1) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                board[r][c] = saved
                return found

            return any(dfs(r, c, 0) for r in range(rows) for c in range(cols))
        """,
    ),
    P(
        "palindrome-partitions", "Split Into Palindromes", "medium", ["backtracking"],
        statement="Return every way to split `s` into pieces that are all palindromes, in any order.",
        inputs="- `s`: a lowercase string",
        output="A list of partitions (each a list of pieces in order).",
        constraints="- `1 <= s.length <= 16`",
        examples=[
            ({"s": "aab"}, [["a", "a", "b"], ["aa", "b"]], ""),
            ({"s": "a"}, [["a"]], ""),
        ],
        compare="unordered",
        approach="From position `start`, try every end `j`: if `s[start:j+1]` is a palindrome, add it to the current partition and recurse from `j + 1`; then remove it.",
        explanation="Every partition is a sequence of cut choices; pruning non-palindromic pieces immediately keeps the search small.",
        time="O(n · 2^n)", space="O(n) recursion besides the output",
        code="""
        def partition(s: str) -> list[list[str]]:
            out, pieces = [], []

            def go(start: int) -> None:
                if start == len(s):
                    out.append(pieces[:])
                    return
                for end in range(start + 1, len(s) + 1):
                    piece = s[start:end]
                    if piece == piece[::-1]:
                        pieces.append(piece)
                        go(end)
                        pieces.pop()

            go(0)
            return out
        """,
    ),
    P(
        "n-queens-count", "Count N-Queens Solutions", "hard", ["backtracking"],
        statement="Place `n` queens on an `n × n` chessboard so that no two attack each other (same row, column or diagonal). Return the number of distinct arrangements.",
        inputs="- `n`: the board size",
        output="The number of solutions.",
        constraints="- `1 <= n <= 9`",
        examples=[
            ({"n": 4}, 2, ""),
            ({"n": 1}, 1, ""),
        ],
        tests=[({"n": 6}, 4), ({"n": 8}, 92), ({"n": 3}, 0)],
        approach="Place one queen per row. Keep sets of used columns and used diagonals (`r − c` and `r + c`). In each row try every free column, recurse to the next row, then undo.",
        explanation="Checking three sets makes each placement test O(1), and rows are filled in order so no arrangement is counted twice.",
        time="O(n!) in the worst case", space="O(n)",
        code="""
        def total_n_queens(n: int) -> int:
            cols, diag, anti = set(), set(), set()

            def place(r: int) -> int:
                if r == n:
                    return 1
                count = 0
                for c in range(n):
                    if c in cols or r - c in diag or r + c in anti:
                        continue
                    cols.add(c); diag.add(r - c); anti.add(r + c)
                    count += place(r + 1)
                    cols.remove(c); diag.remove(r - c); anti.remove(r + c)
                return count

            return place(0)
        """,
    ),
    P(
        "solve-sudoku", "Solve a Sudoku", "hard", ["backtracking"],
        statement="Fill the empty cells (`\".\"`) of a 9 × 9 Sudoku `board` so every row, column and 3 × 3 box contains the digits 1–9 exactly once. The puzzle has exactly one solution. Return the solved board.",
        inputs="- `board`: a 9 × 9 list of one-character strings",
        output="The completed board.",
        constraints="- Exactly one solution exists",
        examples=[
            ({"board": BOARD}, SOLVED, "The classic example puzzle."),
            ({"board": NEARLY}, SOLVED, "A nearly finished grid."),
        ],
        approach="Record which digits each row, column and box already uses. Find an empty cell, try every digit allowed there, recurse, and undo the choice if the rest can't be completed.",
        explanation="The constraint sets prune most digits immediately, so plain backtracking solves typical puzzles quickly. Choosing the empty cell with the fewest options first speeds it up further.",
        time="Exponential in the number of blanks (fast in practice)", space="O(81)",
        code="""
        def solve_sudoku(board: list[list[str]]) -> list[list[str]]:
            rows = [set() for _ in range(9)]
            cols = [set() for _ in range(9)]
            boxes = [set() for _ in range(9)]
            empty = []
            for r in range(9):
                for c in range(9):
                    d = board[r][c]
                    if d == ".":
                        empty.append((r, c))
                    else:
                        rows[r].add(d); cols[c].add(d); boxes[r // 3 * 3 + c // 3].add(d)

            def fill(k: int) -> bool:
                if k == len(empty):
                    return True
                r, c = empty[k]
                b = r // 3 * 3 + c // 3
                for d in "123456789":
                    if d in rows[r] or d in cols[c] or d in boxes[b]:
                        continue
                    board[r][c] = d
                    rows[r].add(d); cols[c].add(d); boxes[b].add(d)
                    if fill(k + 1):
                        return True
                    rows[r].remove(d); cols[c].remove(d); boxes[b].remove(d)
                board[r][c] = "."
                return False

            fill(0)
            return board
        """,
    ),
    P(
        "insert-operators", "Insert Operators to Reach a Target", "hard", ["backtracking"],
        statement="Insert `+`, `-` or `*` between the digits of `num` (or leave digits joined into longer numbers) so the expression evaluates to `target`. Numbers can't have leading zeros. Return all such expressions, in any order.",
        inputs="- `num`: a string of digits\n- `target`: an integer",
        output="A list of expressions (no spaces).",
        constraints="- `1 <= num.length <= 10`",
        examples=[
            ({"num": "123", "target": 6}, ["1*2*3", "1+2+3"], ""),
            ({"num": "232", "target": 8}, ["2*3+2", "2+3*2"], ""),
        ],
        tests=[({"num": "105", "target": 5}, ["1*0+5", "10-5"]), ({"num": "3456237490", "target": 9191}, [])],
        compare="unordered",
        approach="Backtrack over where the next number ends. Track the running value and the **last operand**: for `*`, undo the last operand and add `last × current` instead, which respects multiplication's higher precedence.",
        explanation="Keeping the last operand lets you evaluate as you build, without re-parsing each expression. Skipping numbers that start with `0` (except `0` itself) enforces the leading-zero rule.",
        time="O(4^n · n)", space="O(n) recursion besides the output",
        code="""
        def add_operators(num: str, target: int) -> list[str]:
            out = []

            def go(i: int, expr: str, value: int, last: int) -> None:
                if i == len(num):
                    if value == target:
                        out.append(expr)
                    return
                for j in range(i + 1, len(num) + 1):
                    piece = num[i:j]
                    if len(piece) > 1 and piece[0] == "0":
                        break
                    n = int(piece)
                    if i == 0:
                        go(j, piece, n, n)
                    else:
                        go(j, expr + "+" + piece, value + n, n)
                        go(j, expr + "-" + piece, value - n, -n)
                        go(j, expr + "*" + piece, value - last + last * n, last * n)

            go(0, "", 0, 0)
            return out
        """,
    ),
]
