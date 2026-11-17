from . import P

TOPIC = "arrays"

PROBLEMS = [
    P(
        "second-largest-distinct", "Second Largest Distinct Value", "easy", [],
        statement="Given an integer array `nums`, return the **second largest distinct** value. If every element is equal, return `-1`.",
        inputs="- `nums`: a list of integers",
        output="An integer: the second largest distinct value, or `-1` if there isn't one.",
        constraints="- `1 <= nums.length <= 10^5`\n- `-10^9 <= nums[i] <= 10^9`",
        examples=[
            ({"nums": [3, 5, 1, 5]}, 3, "5 is the largest; the next distinct value is 3."),
            ({"nums": [7, 7]}, -1, "Only one distinct value exists."),
        ],
        tests=[({"nums": [-1, -2, -3]}, -2), ({"nums": [4]}, -1)],
        approach="Track the largest and second-largest distinct values in one pass. When a new maximum appears, the old maximum becomes the runner-up; values equal to the maximum are skipped.",
        explanation="Sorting would also work in O(n log n), but two variables are enough. Using `None` as \"not seen yet\" avoids picking a sentinel that could clash with real values.",
        time="O(n)", space="O(1)",
        code="""
        def second_largest(nums: list[int]) -> int:
            first = second = None
            for x in nums:
                if first is None or x > first:
                    first, second = x, first
                elif x != first and (second is None or x > second):
                    second = x
            return -1 if second is None else second
        """,
    ),
    P(
        "missing-number", "The Missing Number", "easy", [],
        statement="An array `nums` contains `n` distinct numbers taken from the range `0 … n`, so exactly one number of the range is missing. Return it.",
        inputs="- `nums`: a list of `n` distinct integers from `0` to `n`",
        output="The one integer in `0 … n` that does not appear in `nums`.",
        constraints="- `1 <= n <= 10^4`\n- All values are distinct and in `[0, n]`.",
        examples=[
            ({"nums": [3, 0, 1]}, 2, "n = 3, so the range is 0…3 and 2 is missing."),
            ({"nums": [0, 1]}, 2, "n = 2; the range is 0…2."),
        ],
        tests=[({"nums": [1]}, 0)],
        approach="The numbers 0…n add up to n(n + 1)/2. Subtract the actual sum of the array; the difference is the missing number.",
        explanation="Every present number cancels out of the expected total, leaving only the missing one. (XOR-ing all indices and values works the same way and avoids large sums in fixed-width languages.)",
        time="O(n)", space="O(1)",
        code="""
        def missing_number(nums: list[int]) -> int:
            n = len(nums)
            return n * (n + 1) // 2 - sum(nums)
        """,
    ),
    P(
        "longest-run-of-ones", "Longest Run of Ones", "easy", [],
        statement="Given a binary array `nums` (only 0s and 1s), return the length of the longest run of consecutive 1s.",
        inputs="- `nums`: a list of 0s and 1s",
        output="An integer: the length of the longest block of consecutive 1s.",
        constraints="- `1 <= nums.length <= 10^5`\n- `nums[i]` is `0` or `1`",
        examples=[
            ({"nums": [1, 1, 0, 1, 1, 1]}, 3, "The last three elements are 1s."),
            ({"nums": [0, 0]}, 0, "There are no 1s at all."),
        ],
        approach="Keep a counter of the current run: add one for each 1 and reset to zero on a 0. The answer is the largest value the counter ever reaches.",
        explanation="Each element is looked at once; the counter always equals the length of the run that ends at the current index.",
        time="O(n)", space="O(1)",
        code="""
        def longest_run_of_ones(nums: list[int]) -> int:
            best = current = 0
            for x in nums:
                current = current + 1 if x == 1 else 0
                best = max(best, current)
            return best
        """,
    ),
    P(
        "add-one-to-digits", "Add One to a Digit Array", "easy", [],
        statement="A non-negative integer is stored as an array of its decimal `digits`, most significant digit first, with no leading zeros. Return the digits of that number plus one.",
        inputs="- `digits`: a list of integers from 0 to 9",
        output="A list of digits representing the number + 1.",
        constraints="- `1 <= digits.length <= 100`\n- `0 <= digits[i] <= 9`\n- No leading zeros (except the number 0 itself)",
        examples=[
            ({"digits": [1, 2, 9]}, [1, 3, 0], "129 + 1 = 130."),
            ({"digits": [9, 9]}, [1, 0, 0], "The carry runs all the way through and adds a new digit."),
        ],
        tests=[({"digits": [0]}, [1])],
        approach="Walk from the last digit. A digit below 9 just increases and we're done; a 9 becomes 0 and the carry moves left. If the carry falls off the front, prepend a 1.",
        explanation="This is grade-school addition. Only trailing 9s are touched, so most inputs finish after one step.",
        time="O(n)", space="O(1) extra (O(n) only when a new digit is added)",
        code="""
        def plus_one(digits: list[int]) -> list[int]:
            result = digits[:]
            for i in range(len(result) - 1, -1, -1):
                if result[i] < 9:
                    result[i] += 1
                    return result
                result[i] = 0
            return [1] + result
        """,
    ),
    P(
        "best-single-trade", "Best Single Trade", "easy", ["greedy"],
        statement="`prices[i]` is a share's price on day `i`. You may buy once and sell once, on a **later** day. Return the maximum profit, or `0` if no profitable trade exists.",
        inputs="- `prices`: a list of non-negative integers (one price per day)",
        output="An integer: the best possible profit (never negative).",
        constraints="- `1 <= prices.length <= 10^5`\n- `0 <= prices[i] <= 10^4`",
        examples=[
            ({"prices": [7, 1, 5, 3, 6, 4]}, 5, "Buy at 1 (day 1), sell at 6 (day 4)."),
            ({"prices": [7, 6, 4, 3, 1]}, 0, "Prices only fall, so don't trade."),
        ],
        approach="Scan the days keeping the cheapest price seen so far. Selling today would earn `price - cheapest`; keep the best of those.",
        explanation="For any selling day, the best buying day is the cheapest earlier day — exactly what the running minimum stores. One pass covers every selling day.",
        time="O(n)", space="O(1)",
        code="""
        def max_profit(prices: list[int]) -> int:
            cheapest, best = float("inf"), 0
            for price in prices:
                cheapest = min(cheapest, price)
                best = max(best, price - cheapest)
            return best
        """,
    ),
    P(
        "majority-element", "Majority Element", "medium", [],
        statement="Return the element that appears **more than ⌊n/2⌋ times** in `nums`. Such an element is guaranteed to exist. Aim for O(1) extra space.",
        inputs="- `nums`: a list of integers with a majority element",
        output="The majority element.",
        constraints="- `1 <= nums.length <= 5 × 10^4`\n- A majority element always exists.",
        examples=[
            ({"nums": [2, 2, 1, 1, 1, 2, 2]}, 2, "2 appears 4 times out of 7."),
            ({"nums": [3, 3, 4]}, 3, ""),
        ],
        approach="Boyer–Moore voting: keep a candidate and a count. Equal elements vote for the candidate (+1), different ones against it (−1); when the count hits 0, the next element becomes the new candidate.",
        explanation="Pair each majority element with a different element and cancel them out: since the majority has more than half the votes, it can't be cancelled completely, so it is the candidate left standing.",
        time="O(n)", space="O(1)",
        code="""
        def majority_element(nums: list[int]) -> int:
            candidate, count = None, 0
            for x in nums:
                if count == 0:
                    candidate = x
                count += 1 if x == candidate else -1
            return candidate
        """,
    ),
    P(
        "rotate-array-right", "Rotate an Array to the Right", "medium", [],
        statement="Rotate the array `nums` to the right by `k` steps **in place** (the last `k` elements move to the front) and return it.",
        inputs="- `nums`: a list of integers\n- `k`: a non-negative integer (may be larger than the length)",
        output="The same list, rotated right by `k`.",
        constraints="- `1 <= nums.length <= 10^5`\n- `0 <= k <= 10^9`",
        examples=[
            ({"nums": [1, 2, 3, 4, 5, 6, 7], "k": 3}, [5, 6, 7, 1, 2, 3, 4], ""),
            ({"nums": [-1, -100, 3, 99], "k": 2}, [3, 99, -1, -100], ""),
        ],
        tests=[({"nums": [1, 2], "k": 3}, [2, 1])],
        approach="Use three reversals: reverse the whole array, then reverse the first `k` elements and the remaining `n − k` separately. Take `k mod n` first.",
        explanation="Reversing everything puts the last k elements at the front but backwards; reversing each part fixes the order inside both parts. No extra array is needed.",
        time="O(n)", space="O(1)",
        code="""
        def rotate(nums: list[int], k: int) -> list[int]:
            n = len(nums)
            k %= n

            def reverse(lo: int, hi: int) -> None:
                while lo < hi:
                    nums[lo], nums[hi] = nums[hi], nums[lo]
                    lo, hi = lo + 1, hi - 1

            reverse(0, n - 1)
            reverse(0, k - 1)
            reverse(k, n - 1)
            return nums
        """,
    ),
    P(
        "merge-overlapping-intervals", "Merge Overlapping Intervals", "medium", ["sorting"],
        statement="Given a list of `intervals` `[start, end]`, merge every group of overlapping intervals and return the result sorted by start. Intervals that touch (`[1, 4]` and `[4, 5]`) count as overlapping.",
        inputs="- `intervals`: a list of `[start, end]` pairs with `start <= end`",
        output="A list of merged, non-overlapping intervals sorted by start.",
        constraints="- `1 <= intervals.length <= 10^4`\n- `0 <= start <= end <= 10^4`",
        examples=[
            ({"intervals": [[1, 3], [2, 6], [8, 10], [15, 18]]}, [[1, 6], [8, 10], [15, 18]], "[1, 3] and [2, 6] overlap."),
            ({"intervals": [[1, 4], [4, 5]]}, [[1, 5]], "Touching intervals merge."),
        ],
        tests=[({"intervals": [[5, 6], [1, 2], [2, 3]]}, [[1, 3], [5, 6]])],
        approach="Sort by start. Walk through the intervals: if the current one starts at or before the end of the last merged interval, extend that end; otherwise start a new merged interval.",
        explanation="After sorting, any interval that overlaps the merged block must start before the block ends, so a single comparison with the last block is enough.",
        time="O(n log n)", space="O(n) for the output",
        code="""
        def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
            merged = []
            for start, end in sorted(intervals):
                if merged and start <= merged[-1][1]:
                    merged[-1][1] = max(merged[-1][1], end)
                else:
                    merged.append([start, end])
            return merged
        """,
    ),
    P(
        "spiral-order", "Spiral Order of a Matrix", "medium", [],
        statement="Return all elements of an `m × n` `matrix` in spiral order: along the top row, down the right column, back along the bottom row, up the left column, then inwards.",
        inputs="- `matrix`: a list of `m` rows, each a list of `n` integers",
        output="A list of all `m × n` values in spiral order.",
        constraints="- `1 <= m, n <= 10`\n- `-100 <= matrix[i][j] <= 100`",
        examples=[
            ({"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}, [1, 2, 3, 6, 9, 8, 7, 4, 5], ""),
            ({"matrix": [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]}, [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7], ""),
        ],
        tests=[({"matrix": [[1], [2], [3]]}, [1, 2, 3])],
        approach="Keep four boundaries (top, bottom, left, right). Walk one side, then shrink that boundary. Check the boundaries again before the bottom row and left column so a single remaining row or column isn't visited twice.",
        explanation="Each loop peels one layer off the matrix. The extra checks handle rectangles where the last layer is a single row or column.",
        time="O(m·n)", space="O(1) besides the output",
        code="""
        def spiral_order(matrix: list[list[int]]) -> list[int]:
            out = []
            top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1
            while top <= bottom and left <= right:
                out.extend(matrix[top][c] for c in range(left, right + 1))
                top += 1
                out.extend(matrix[r][right] for r in range(top, bottom + 1))
                right -= 1
                if top <= bottom:
                    out.extend(matrix[bottom][c] for c in range(right, left - 1, -1))
                    bottom -= 1
                if left <= right:
                    out.extend(matrix[r][left] for r in range(bottom, top - 1, -1))
                    left += 1
            return out
        """,
    ),
    P(
        "rotate-square-matrix", "Rotate a Square Matrix", "medium", [],
        statement="Rotate an `n × n` `matrix` by 90 degrees **clockwise**, in place, and return it.",
        inputs="- `matrix`: a list of `n` rows of `n` integers",
        output="The same matrix, rotated 90° clockwise.",
        constraints="- `1 <= n <= 20`\n- `-1000 <= matrix[i][j] <= 1000`",
        examples=[
            ({"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}, [[7, 4, 1], [8, 5, 2], [9, 6, 3]], ""),
            ({"matrix": [[1, 2], [3, 4]]}, [[3, 1], [4, 2]], ""),
        ],
        approach="Transpose the matrix (swap `matrix[i][j]` with `matrix[j][i]`), then reverse every row.",
        explanation="After a transpose, row i holds the old column i top-to-bottom; a clockwise rotation needs that column bottom-to-top as row i, which reversing the row gives.",
        time="O(n²)", space="O(1)",
        code="""
        def rotate_matrix(matrix: list[list[int]]) -> list[list[int]]:
            n = len(matrix)
            for i in range(n):
                for j in range(i + 1, n):
                    matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
            for row in matrix:
                row.reverse()
            return matrix
        """,
    ),
    P(
        "first-missing-positive", "Smallest Missing Positive", "hard", ["hash-map"],
        statement="Given an unsorted integer array `nums`, return the **smallest positive integer** that does not appear in it. Use O(n) time and O(1) extra space.",
        inputs="- `nums`: a list of integers (any values, duplicates allowed)",
        output="The smallest positive integer missing from `nums`.",
        constraints="- `1 <= nums.length <= 10^5`\n- `-2^31 <= nums[i] <= 2^31 - 1`",
        examples=[
            ({"nums": [3, 4, -1, 1]}, 2, "1 is present, 2 is not."),
            ({"nums": [1, 2, 0]}, 3, ""),
        ],
        tests=[({"nums": [7, 8, 9, 11]}, 1), ({"nums": [1, 1]}, 2), ({"nums": [2, 1]}, 3)],
        approach="The answer is in `1 … n + 1`. Use the array itself as a hash table: place each value `v` in `1 … n` at index `v − 1` by swapping. Then the first index `i` with `nums[i] != i + 1` gives the answer `i + 1`.",
        explanation="Each swap puts at least one value in its final position, so there are at most n swaps in total. Values outside 1…n can't be the answer's blockers and are left wherever they land.",
        time="O(n)", space="O(1)",
        code="""
        def first_missing_positive(nums: list[int]) -> int:
            n = len(nums)
            for i in range(n):
                while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
                    j = nums[i] - 1
                    nums[i], nums[j] = nums[j], nums[i]
            for i in range(n):
                if nums[i] != i + 1:
                    return i + 1
            return n + 1
        """,
    ),
]
