from . import P

TOPIC = "dynamic-programming"

PROBLEMS = [
    P(
        "nth-fibonacci", "The n-th Fibonacci Number", "easy", ["dynamic-programming"],
        statement="The Fibonacci numbers are `F(0) = 0`, `F(1) = 1` and `F(n) = F(n − 1) + F(n − 2)`. Return `F(n)`.",
        inputs="- `n`: a non-negative integer",
        output="`F(n)`.",
        constraints="- `0 <= n <= 90`",
        examples=[
            ({"n": 4}, 3, "0, 1, 1, 2, 3."),
            ({"n": 10}, 55, ""),
        ],
        tests=[({"n": 0}, 0), ({"n": 1}, 1)],
        approach="Build the values bottom-up keeping only the last two.",
        explanation="The naive recursion recomputes the same values exponentially many times; storing (or carrying) previous results makes it linear. This is the smallest example of dynamic programming.",
        time="O(n)", space="O(1)",
        code="""
        def fib(n: int) -> int:
            a, b = 0, 1
            for _ in range(n):
                a, b = b, a + b
            return a
        """,
    ),
    P(
        "cheapest-climb", "Cheapest Way Up the Stairs", "easy", ["dynamic-programming"],
        statement="`cost[i]` is the price of stepping on stair `i`. From a stair you may climb one or two steps. You may start on stair 0 or 1. Return the minimum cost to reach the top (just past the last stair).",
        inputs="- `cost`: a list of non-negative integers",
        output="The minimum total cost.",
        constraints="- `2 <= cost.length <= 1000`\n- `0 <= cost[i] <= 999`",
        examples=[
            ({"cost": [10, 15, 20]}, 15, "Start on stair 1 (15) and jump two steps to the top."),
            ({"cost": [1, 100, 1, 1, 1, 100, 1, 1, 100, 1]}, 6, "Step on all the 1s."),
        ],
        approach="Let `best[i]` be the cheapest cost to stand on stair `i`: `cost[i] + min(best[i−1], best[i−2])`. The top is reached from either of the last two stairs.",
        explanation="Each state depends only on the two before it, so two variables are enough.",
        time="O(n)", space="O(1)",
        code="""
        def min_cost_climbing(cost: list[int]) -> int:
            two_back, one_back = cost[0], cost[1]
            for c in cost[2:]:
                two_back, one_back = one_back, c + min(two_back, one_back)
            return min(two_back, one_back)
        """,
    ),
    P(
        "pascal-row", "A Row of Pascal's Triangle", "easy", ["dynamic-programming"],
        statement="Return row `row_index` (0-indexed) of Pascal's triangle, where each number is the sum of the two numbers above it.",
        inputs="- `row_index`: a non-negative integer",
        output="The list of numbers in that row.",
        constraints="- `0 <= row_index <= 33`",
        examples=[
            ({"row_index": 3}, [1, 3, 3, 1], ""),
            ({"row_index": 0}, [1], ""),
        ],
        approach="Start with `[1]`. To get the next row in place, append a 1 and update entries from right to left: `row[j] += row[j − 1]`.",
        explanation="Updating right to left uses each old value before it is overwritten, so a single list suffices.",
        time="O(k²)", space="O(k)",
        code="""
        def get_row(row_index: int) -> list[int]:
            row = [1]
            for _ in range(row_index):
                row.append(1)
                for j in range(len(row) - 2, 0, -1):
                    row[j] += row[j - 1]
            return row
        """,
    ),
    P(
        "grid-paths", "Paths Through a Grid", "medium", ["dynamic-programming"],
        statement="A robot starts at the top-left of an `m × n` grid and can only move **right** or **down**. How many distinct paths lead to the bottom-right cell?",
        inputs="- `m`: rows\n- `n`: columns",
        output="The number of paths.",
        constraints="- `1 <= m, n <= 100`",
        examples=[
            ({"m": 3, "n": 7}, 28, ""),
            ({"m": 3, "n": 2}, 3, "Right-down-down, down-right-down, down-down-right."),
        ],
        approach="Paths to a cell = paths to the cell above + paths to the cell on the left. Fill row by row using a single array.",
        explanation="Every path enters a cell from exactly one of those two neighbours, so the counts add without double counting.",
        time="O(m·n)", space="O(n)",
        code="""
        def unique_paths(m: int, n: int) -> int:
            row = [1] * n
            for _ in range(1, m):
                for j in range(1, n):
                    row[j] += row[j - 1]
            return row[-1]
        """,
    ),
    P(
        "longest-increasing-subsequence", "Longest Increasing Subsequence", "medium", ["dynamic-programming", "binary-search"],
        statement="Return the length of the longest **strictly increasing** subsequence of `nums` (elements in order, not necessarily adjacent).",
        inputs="- `nums`: a list of integers",
        output="The length of the longest strictly increasing subsequence.",
        constraints="- `1 <= nums.length <= 2500`",
        examples=[
            ({"nums": [10, 9, 2, 5, 3, 7, 101, 18]}, 4, "[2, 3, 7, 101] (or [2, 5, 7, 18])."),
            ({"nums": [7, 7, 7, 7]}, 1, "Equal values don't increase."),
        ],
        tests=[({"nums": [0, 1, 0, 3, 2, 3]}, 4)],
        approach="Keep `tails[k]` = the smallest possible last value of an increasing subsequence of length `k + 1`. For each number, binary-search the first tail ≥ it and replace it (or append if none).",
        explanation="`tails` stays sorted, and a smaller tail is always better for extending later. Its final length is the answer. (The O(n²) DP comparing every pair is the simpler first step.)",
        time="O(n log n)", space="O(n)",
        code="""
        from bisect import bisect_left

        def length_of_lis(nums: list[int]) -> int:
            tails = []
            for x in nums:
                i = bisect_left(tails, x)
                if i == len(tails):
                    tails.append(x)
                else:
                    tails[i] = x
            return len(tails)
        """,
    ),
    P(
        "word-break", "Split Into Dictionary Words", "medium", ["dynamic-programming"],
        statement="Return `true` if `s` can be split into a sequence of one or more words from `words` (a word may be reused).",
        inputs="- `s`: a lowercase string\n- `words`: a list of dictionary words",
        output="`true` or `false`.",
        constraints="- `1 <= s.length <= 300`\n- `1 <= words.length <= 1000`",
        examples=[
            ({"s": "applepenapple", "words": ["apple", "pen"]}, True, "apple + pen + apple."),
            ({"s": "catsandog", "words": ["cats", "dog", "sand", "and", "cat"]}, False, ""),
        ],
        approach="`ok[i]` is true if the prefix `s[:i]` can be split. `ok[0] = true`; `ok[i]` is true if some word `w` ends at `i` and `ok[i − len(w)]` is true.",
        explanation="Each prefix is decided once from shorter prefixes, avoiding the exponential blow-up of trying every split recursively.",
        time="O(n · W · L)", space="O(n)",
        code="""
        def word_break(s: str, words: list[str]) -> bool:
            ok = [True] + [False] * len(s)
            for i in range(1, len(s) + 1):
                ok[i] = any(ok[i - len(w)] and s[i - len(w):i] == w for w in words if len(w) <= i)
            return ok[-1]
        """,
    ),
    P(
        "ways-to-make-change", "Ways to Make Change", "medium", ["dynamic-programming"],
        statement="Return the number of **combinations** of `coins` (unlimited supply of each) that add up to `amount`. Order doesn't matter: 1 + 2 and 2 + 1 are the same combination.",
        inputs="- `amount`: a non-negative integer\n- `coins`: a list of distinct positive denominations",
        output="The number of combinations.",
        constraints="- `0 <= amount <= 5000`\n- `1 <= coins.length <= 300`",
        examples=[
            ({"amount": 5, "coins": [1, 2, 5]}, 4, "5, 2+2+1, 2+1+1+1, 1+1+1+1+1."),
            ({"amount": 3, "coins": [2]}, 0, ""),
        ],
        tests=[({"amount": 0, "coins": [7]}, 1)],
        approach="`ways[a]` = number of combinations for amount `a`, starting with `ways[0] = 1`. Process the coins one at a time (outer loop) and for each coin add `ways[a − coin]` to `ways[a]`.",
        explanation="Putting coins in the outer loop builds each combination in one fixed coin order, so permutations of the same coins aren't counted twice.",
        time="O(amount · coins)", space="O(amount)",
        code="""
        def change(amount: int, coins: list[int]) -> int:
            ways = [1] + [0] * amount
            for coin in coins:
                for a in range(coin, amount + 1):
                    ways[a] += ways[a - coin]
            return ways[amount]
        """,
    ),
    P(
        "equal-sum-split", "Split Into Two Equal Sums", "medium", ["dynamic-programming"],
        statement="Return `true` if `nums` can be divided into two subsets with equal sums.",
        inputs="- `nums`: a list of positive integers",
        output="`true` or `false`.",
        constraints="- `1 <= nums.length <= 200`\n- `1 <= nums[i] <= 100`",
        examples=[
            ({"nums": [1, 5, 11, 5]}, True, "[1, 5, 5] and [11]."),
            ({"nums": [1, 2, 3, 5]}, False, "The total 11 is odd."),
        ],
        approach="The total must be even; then ask whether some subset sums to `total / 2`. Track the set of reachable sums (a 0/1 knapsack): for each number, every reachable sum `s` also makes `s + x` reachable.",
        explanation="Each number is used at most once because new sums are added from the previous set. Stop early once the target appears.",
        time="O(n · total)", space="O(total)",
        code="""
        def can_partition(nums: list[int]) -> bool:
            total = sum(nums)
            if total % 2:
                return False
            target, reachable = total // 2, {0}
            for x in nums:
                reachable |= {s + x for s in reachable if s + x <= target}
                if target in reachable:
                    return True
            return False
        """,
    ),
    P(
        "decode-digit-message", "Ways to Decode a Digit Message", "medium", ["dynamic-programming"],
        statement="Letters were encoded as numbers `A = 1 … Z = 26` and concatenated. Given the digit string `s`, return the number of ways to decode it. A part can't start with `0` (`\"06\"` is invalid).",
        inputs="- `s`: a string of digits",
        output="The number of decodings (0 if none).",
        constraints="- `1 <= s.length <= 100`",
        examples=[
            ({"s": "12"}, 2, "AB (1, 2) or L (12)."),
            ({"s": "226"}, 3, "BZ, VF, BBF."),
        ],
        tests=[({"s": "06"}, 0), ({"s": "10"}, 1), ({"s": "2101"}, 1)],
        approach="`ways[i]` counts decodings of `s[:i]`. The last part is either one digit (valid if not `0`) — add `ways[i − 1]` — or two digits between 10 and 26 — add `ways[i − 2]`.",
        explanation="Like climbing stairs one or two at a time, except some steps are illegal. Zeros are only valid as the second digit of 10 or 20.",
        time="O(n)", space="O(1)",
        code="""
        def num_decodings(s: str) -> int:
            prev2, prev1 = 1, (1 if s[0] != "0" else 0)
            for i in range(1, len(s)):
                current = 0
                if s[i] != "0":
                    current += prev1
                if 10 <= int(s[i - 1:i + 1]) <= 26:
                    current += prev2
                prev2, prev1 = prev1, current
            return prev1
        """,
    ),
    P(
        "edit-distance", "Edit Distance", "hard", ["dynamic-programming"],
        statement="Return the minimum number of single-character operations — **insert**, **delete** or **replace** — needed to turn `word1` into `word2`.",
        inputs="- `word1`, `word2`: lowercase strings",
        output="The minimum number of operations.",
        constraints="- `0 <= word1.length, word2.length <= 500`",
        examples=[
            ({"word1": "horse", "word2": "ros"}, 3, "horse → rorse → rose → ros."),
            ({"word1": "intention", "word2": "execution"}, 5, ""),
        ],
        tests=[({"word1": "", "word2": "abc"}, 3)],
        approach="`d[i][j]` = edits to turn `word1[:i]` into `word2[:j]`. If the last letters match, `d[i][j] = d[i−1][j−1]`; otherwise `1 + min(d[i−1][j] (delete), d[i][j−1] (insert), d[i−1][j−1] (replace))`. Base cases: `d[i][0] = i`, `d[0][j] = j`.",
        explanation="Any optimal edit sequence ends with one of these three operations (or a free match) on the last characters, so the recurrence covers every option. Keeping one previous row gives O(n) space.",
        time="O(m·n)", space="O(n)",
        code="""
        def min_distance(word1: str, word2: str) -> int:
            prev = list(range(len(word2) + 1))
            for i, a in enumerate(word1, start=1):
                curr = [i] + [0] * len(word2)
                for j, b in enumerate(word2, start=1):
                    if a == b:
                        curr[j] = prev[j - 1]
                    else:
                        curr[j] = 1 + min(prev[j], curr[j - 1], prev[j - 1])
                prev = curr
            return prev[-1]
        """,
    ),
    P(
        "count-distinct-subsequences", "Count Hidden Copies of a Word", "hard", ["dynamic-programming"],
        statement="Return the number of distinct ways to choose characters of `s` (keeping their order) that spell `t` — i.e. the number of subsequences of `s` equal to `t`.",
        inputs="- `s`, `t`: strings of letters",
        output="The number of matching subsequences.",
        constraints="- `1 <= s.length, t.length <= 1000`\n- The answer fits in a 32-bit integer",
        examples=[
            ({"s": "rabbbit", "t": "rabbit"}, 3, "Any two of the three b's."),
            ({"s": "babgbag", "t": "bag"}, 5, ""),
        ],
        approach="`ways[j]` = number of ways to form `t[:j]` from the part of `s` read so far, with `ways[0] = 1`. For each character of `s`, update `j` from right to left: if `s[i] == t[j−1]`, add `ways[j−1]` to `ways[j]`.",
        explanation="Each character of s can either be skipped (ways unchanged) or used to extend a match of t[:j−1]. Updating right to left makes sure a character is used at most once per subsequence.",
        time="O(m·n)", space="O(n)",
        code="""
        def num_distinct(s: str, t: str) -> int:
            ways = [1] + [0] * len(t)
            for ch in s:
                for j in range(len(t), 0, -1):
                    if t[j - 1] == ch:
                        ways[j] += ways[j - 1]
            return ways[-1]
        """,
    ),
]
