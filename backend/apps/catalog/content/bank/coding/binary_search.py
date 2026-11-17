from . import P

TOPIC = "binary-search"

PROBLEMS = [
    P(
        "insert-position", "Where Would It Go?", "easy", ["binary-search"],
        statement="Given a sorted array of distinct integers `nums` and a `target`, return the index of `target` if present; otherwise return the index where it would be inserted to keep the array sorted. Use O(log n) time.",
        inputs="- `nums`: a sorted list of distinct integers\n- `target`: an integer",
        output="An index between `0` and `len(nums)`.",
        constraints="- `1 <= nums.length <= 10^4`",
        examples=[
            ({"nums": [1, 3, 5, 6], "target": 5}, 2, "Found at index 2."),
            ({"nums": [1, 3, 5, 6], "target": 2}, 1, "2 belongs between 1 and 3."),
        ],
        tests=[({"nums": [1, 3, 5, 6], "target": 7}, 4), ({"nums": [1, 3, 5, 6], "target": 0}, 0)],
        approach="Binary search for the first index whose value is `>= target` (the *lower bound*). Search over `[0, n]` so `n` is a valid answer.",
        explanation="Invariant: everything before `lo` is smaller than the target and everything from `hi` on is ≥ target. When they meet, `lo` is the insertion point — and also the position of the target if it exists.",
        time="O(log n)", space="O(1)",
        code="""
        def search_insert(nums: list[int], target: int) -> int:
            lo, hi = 0, len(nums)
            while lo < hi:
                mid = (lo + hi) // 2
                if nums[mid] < target:
                    lo = mid + 1
                else:
                    hi = mid
            return lo
        """,
    ),
    P(
        "first-failing-build", "First Failing Build", "easy", ["binary-search"],
        statement="Builds are numbered `0 … n−1`. `failed[i]` tells whether build `i` failed; once a build fails, every later build also fails. Return the index of the first failed build, or `-1` if none failed — checking as few builds as possible.",
        inputs="- `failed`: a list of booleans of the form `[false, …, false, true, …, true]`",
        output="The first index holding `true`, or `-1`.",
        constraints="- `1 <= failed.length <= 10^5`",
        examples=[
            ({"failed": [False, False, True, True, True]}, 2, ""),
            ({"failed": [False, False]}, -1, "No build failed."),
        ],
        tests=[({"failed": [True]}, 0)],
        approach="The array is monotonic (false… then true…), so binary search for the boundary: if `mid` failed, the answer is at `mid` or before; otherwise it is after `mid`.",
        explanation="This is the template behind every *find the first index where a condition becomes true* question; only O(log n) builds are inspected.",
        time="O(log n)", space="O(1)",
        code="""
        def first_failure(failed: list[bool]) -> int:
            lo, hi = 0, len(failed)
            while lo < hi:
                mid = (lo + hi) // 2
                if failed[mid]:
                    hi = mid
                else:
                    lo = mid + 1
            return lo if lo < len(failed) else -1
        """,
    ),
    P(
        "mountain-peak-index", "Peak of a Mountain Array", "easy", ["binary-search"],
        statement="`arr` strictly increases up to a single peak and then strictly decreases. Return the index of the peak in O(log n) time.",
        inputs="- `arr`: a mountain array (length ≥ 3)",
        output="The index of the largest element.",
        constraints="- `3 <= arr.length <= 10^5`",
        examples=[
            ({"arr": [0, 2, 1, 0]}, 1, ""),
            ({"arr": [3, 4, 5, 1]}, 2, ""),
        ],
        approach="Compare `arr[mid]` with `arr[mid + 1]`. If it is smaller, you're on the rising slope and the peak is to the right; otherwise the peak is at `mid` or to its left.",
        explanation="The condition \"`arr[i] > arr[i + 1]`\" is false before the peak and true from the peak on — a monotonic boundary that binary search can find.",
        time="O(log n)", space="O(1)",
        code="""
        def peak_index(arr: list[int]) -> int:
            lo, hi = 0, len(arr) - 1
            while lo < hi:
                mid = (lo + hi) // 2
                if arr[mid] < arr[mid + 1]:
                    lo = mid + 1
                else:
                    hi = mid
            return lo
        """,
    ),
    P(
        "count-negatives-in-grid", "Count Negatives in a Sorted Grid", "easy", ["binary-search"],
        statement="Every row and every column of `grid` is sorted in **non-increasing** order. Return the number of negative numbers.",
        inputs="- `grid`: an `m × n` list of integers",
        output="The count of negative values.",
        constraints="- `1 <= m, n <= 100`\n- `-100 <= grid[i][j] <= 100`",
        examples=[
            ({"grid": [[4, 3, 2, -1], [3, 2, 1, -1], [1, 1, -1, -2], [-1, -1, -2, -3]]}, 8, ""),
            ({"grid": [[3, 2], [1, 0]]}, 0, ""),
        ],
        approach="Binary-search each row for its first negative: the count in that row is `n − index`. (A staircase walk from the bottom-left corner also works in O(m + n).)",
        explanation="Each row is sorted, so its negatives form a suffix whose start is a monotonic boundary.",
        time="O(m log n)", space="O(1)",
        code="""
        def count_negatives(grid: list[list[int]]) -> int:
            total = 0
            for row in grid:
                lo, hi = 0, len(row)
                while lo < hi:
                    mid = (lo + hi) // 2
                    if row[mid] < 0:
                        hi = mid
                    else:
                        lo = mid + 1
                total += len(row) - lo
            return total
        """,
    ),
    P(
        "search-rotated-array", "Search a Rotated Sorted Array", "medium", ["binary-search"],
        statement="A sorted array of distinct integers was rotated at an unknown pivot (e.g. `[0, 1, 2, 4, 5, 6, 7]` → `[4, 5, 6, 7, 0, 1, 2]`). Return the index of `target`, or `-1`, in O(log n).",
        inputs="- `nums`: a rotated sorted list of distinct integers\n- `target`: an integer",
        output="The index of `target` or `-1`.",
        constraints="- `1 <= nums.length <= 5000`",
        examples=[
            ({"nums": [4, 5, 6, 7, 0, 1, 2], "target": 0}, 4, ""),
            ({"nums": [4, 5, 6, 7, 0, 1, 2], "target": 3}, -1, ""),
        ],
        tests=[({"nums": [1], "target": 0}, -1), ({"nums": [5, 1, 3], "target": 5}, 0)],
        approach="At each step one half of `[lo, hi]` is sorted. Check which half is sorted (compare `nums[lo]` with `nums[mid]`), see whether the target lies inside that half's range, and discard the other half accordingly.",
        explanation="A rotation splits the array into two sorted runs; any midpoint leaves at least one side entirely inside one run, whose range check is reliable.",
        time="O(log n)", space="O(1)",
        code="""
        def search_rotated(nums: list[int], target: int) -> int:
            lo, hi = 0, len(nums) - 1
            while lo <= hi:
                mid = (lo + hi) // 2
                if nums[mid] == target:
                    return mid
                if nums[lo] <= nums[mid]:  # left half sorted
                    if nums[lo] <= target < nums[mid]:
                        hi = mid - 1
                    else:
                        lo = mid + 1
                else:  # right half sorted
                    if nums[mid] < target <= nums[hi]:
                        lo = mid + 1
                    else:
                        hi = mid - 1
            return -1
        """,
    ),
    P(
        "find-a-peak", "Find a Peak Element", "medium", ["binary-search"],
        statement="A peak is an element strictly greater than its neighbours (outside the array counts as −∞). Adjacent elements are never equal. Return the index of **a** peak in O(log n); if there are several, any is accepted.",
        inputs="- `nums`: a list of integers with no equal neighbours",
        output="The index of a peak.",
        constraints="- `1 <= nums.length <= 1000`",
        examples=[
            ({"nums": [1, 2, 3, 1]}, 2, "3 is a peak."),
            ({"nums": [1, 2, 1, 3, 5, 6, 4]}, 5, "6 is a peak (index 1 would also be accepted)."),
        ],
        approach="If `nums[mid] < nums[mid + 1]`, a peak must exist to the right (the values keep rising until something falls, or the array ends at −∞). Otherwise one exists at `mid` or to the left.",
        explanation="Walking uphill always reaches a peak, so discarding the downhill side never loses all peaks — the array doesn't need to be sorted for this binary search to work.",
        time="O(log n)", space="O(1)",
        code="""
        def find_peak(nums: list[int]) -> int:
            lo, hi = 0, len(nums) - 1
            while lo < hi:
                mid = (lo + hi) // 2
                if nums[mid] < nums[mid + 1]:
                    lo = mid + 1
                else:
                    hi = mid
            return lo
        """,
    ),
    P(
        "search-sorted-matrix", "Search a Sorted Matrix", "medium", ["binary-search"],
        statement="Each row of `matrix` is sorted, and the first value of each row is greater than the last value of the previous row. Return `true` if `target` is in the matrix, in O(log(m·n)).",
        inputs="- `matrix`: an `m × n` list of integers\n- `target`: an integer",
        output="`true` or `false`.",
        constraints="- `1 <= m, n <= 100`",
        examples=[
            ({"matrix": [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], "target": 3}, True, ""),
            ({"matrix": [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], "target": 13}, False, ""),
        ],
        approach="Read the matrix row by row and it is one sorted list of `m·n` values. Binary search over indices `0 … m·n − 1`, mapping index `k` to `matrix[k // n][k % n]`.",
        explanation="No copying is needed — the index mapping makes the 2-D grid behave like a 1-D sorted array.",
        time="O(log(m·n))", space="O(1)",
        code="""
        def search_matrix(matrix: list[list[int]], target: int) -> bool:
            m, n = len(matrix), len(matrix[0])
            lo, hi = 0, m * n - 1
            while lo <= hi:
                mid = (lo + hi) // 2
                value = matrix[mid // n][mid % n]
                if value == target:
                    return True
                if value < target:
                    lo = mid + 1
                else:
                    hi = mid - 1
            return False
        """,
    ),
    P(
        "slowest-eating-speed", "Slowest Eating Speed", "medium", ["binary-search"],
        statement="There are `piles` of bananas. Each hour you choose one pile and eat up to `k` bananas from it (if the pile has fewer, you finish it and wait out the hour). Return the minimum integer speed `k` that finishes everything within `h` hours.",
        inputs="- `piles`: a list of pile sizes\n- `h`: hours available (`h >= len(piles)`)",
        output="The minimum speed `k`.",
        constraints="- `1 <= piles.length <= 10^4`\n- `piles.length <= h <= 10^9`\n- `1 <= piles[i] <= 10^9`",
        examples=[
            ({"piles": [3, 6, 7, 11], "h": 8}, 4, "Hours at speed 4: 1 + 2 + 2 + 3 = 8."),
            ({"piles": [30, 11, 23, 4, 20], "h": 5}, 30, "One hour per pile forces k = max pile."),
        ],
        tests=[({"piles": [30, 11, 23, 4, 20], "h": 6}, 23)],
        approach="Binary search on the answer `k` in `[1, max(piles)]`. For a candidate speed, the hours needed are `sum(ceil(p / k))`; if that fits in `h`, try slower, else go faster.",
        explanation="Hours needed only decrease as `k` grows, so \"finishes in time\" is a monotonic yes/no test — the classic *binary search on the answer* pattern.",
        time="O(n log max)", space="O(1)",
        code="""
        def min_eating_speed(piles: list[int], h: int) -> int:
            lo, hi = 1, max(piles)
            while lo < hi:
                k = (lo + hi) // 2
                hours = sum((p + k - 1) // k for p in piles)
                if hours <= h:
                    hi = k
                else:
                    lo = k + 1
            return lo
        """,
    ),
    P(
        "ship-within-days", "Ship Packages Within D Days", "medium", ["binary-search"],
        statement="Packages must ship in the given order. Each day the ship is loaded with consecutive packages up to its `capacity`. Return the minimum capacity that ships all `weights` within `days` days.",
        inputs="- `weights`: package weights in order\n- `days`: the number of days available",
        output="The minimum ship capacity.",
        constraints="- `1 <= days <= weights.length <= 5 × 10^4`\n- `1 <= weights[i] <= 500`",
        examples=[
            ({"weights": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "days": 5}, 15, "[1–5], [6, 7], [8], [9], [10]."),
            ({"weights": [3, 2, 2, 4, 1, 4], "days": 3}, 6, "[3, 2], [2, 4], [1, 4]."),
        ],
        tests=[({"weights": [1, 2, 3, 1, 1], "days": 4}, 3)],
        approach="Binary search the capacity between `max(weights)` (every package must fit) and `sum(weights)` (one day). For each candidate, simulate greedily: start a new day whenever the next package would overflow.",
        explanation="A larger capacity never needs more days, so feasibility is monotonic. Greedy loading is optimal for a fixed capacity because packages must stay in order.",
        time="O(n log(sum))", space="O(1)",
        code="""
        def ship_within_days(weights: list[int], days: int) -> int:
            def days_needed(capacity: int) -> int:
                used, load = 1, 0
                for w in weights:
                    if load + w > capacity:
                        used += 1
                        load = 0
                    load += w
                return used

            lo, hi = max(weights), sum(weights)
            while lo < hi:
                mid = (lo + hi) // 2
                if days_needed(mid) <= days:
                    hi = mid
                else:
                    lo = mid + 1
            return lo
        """,
    ),
    P(
        "single-unpaired-element", "The Unpaired Element", "medium", ["binary-search"],
        statement="In a sorted array every element appears exactly twice except one, which appears once. Return that element in O(log n) time and O(1) space.",
        inputs="- `nums`: a sorted list of odd length",
        output="The element that appears once.",
        constraints="- `1 <= nums.length <= 10^5`",
        examples=[
            ({"nums": [1, 1, 2, 3, 3, 4, 4, 8, 8]}, 2, ""),
            ({"nums": [3, 3, 7, 7, 10, 11, 11]}, 10, ""),
        ],
        tests=[({"nums": [5]}, 5)],
        approach="Before the single element, pairs start at even indices; after it, at odd indices. Look at an even `mid`: if `nums[mid] == nums[mid + 1]` the single element is to the right, otherwise at `mid` or to the left.",
        explanation="Forcing `mid` to be even makes the pair check uniform. The pair-alignment property is monotonic, so binary search applies.",
        time="O(log n)", space="O(1)",
        code="""
        def single_non_duplicate(nums: list[int]) -> int:
            lo, hi = 0, len(nums) - 1
            while lo < hi:
                mid = (lo + hi) // 2
                if mid % 2:
                    mid -= 1
                if nums[mid] == nums[mid + 1]:
                    lo = mid + 2
                else:
                    hi = mid
            return nums[lo]
        """,
    ),
    P(
        "median-of-two-sorted-arrays", "Median of Two Sorted Arrays", "hard", ["binary-search"],
        statement="Return the median of the combined values of two sorted arrays `a` and `b`, in O(log(min(m, n))) time.",
        inputs="- `a`: a sorted list of integers\n- `b`: a sorted list of integers (not both empty)",
        output="The median as a floating-point number.",
        constraints="- `0 <= m, n <= 1000`\n- `1 <= m + n <= 2000`",
        examples=[
            ({"a": [1, 3], "b": [2]}, 2.0, "Merged: [1, 2, 3]."),
            ({"a": [1, 2], "b": [3, 4]}, 2.5, "Merged: [1, 2, 3, 4] → (2 + 3) / 2."),
        ],
        tests=[({"a": [], "b": [1]}, 1.0), ({"a": [0, 0], "b": [0, 0]}, 0.0), ({"a": [2], "b": [1, 3, 4, 5]}, 3.0)],
        approach="Binary search how many elements `i` of the shorter array go into the left half; the longer array contributes `half − i`. A split is correct when every left element ≤ every right element: `a[i−1] ≤ b[j]` and `b[j−1] ≤ a[i]`. Then the median comes from the border values.",
        explanation="Moving `i` right increases `a[i−1]` and decreases `b[j−1]`, so the two conditions fail in opposite directions — which tells binary search which way to move. Using −∞/+∞ at the array ends avoids special cases.",
        time="O(log(min(m, n)))", space="O(1)",
        code="""
        def find_median(a: list[int], b: list[int]) -> float:
            if len(a) > len(b):
                a, b = b, a
            m, n = len(a), len(b)
            half = (m + n + 1) // 2
            lo, hi = 0, m
            while True:
                i = (lo + hi) // 2
                j = half - i
                a_left = a[i - 1] if i > 0 else float("-inf")
                a_right = a[i] if i < m else float("inf")
                b_left = b[j - 1] if j > 0 else float("-inf")
                b_right = b[j] if j < n else float("inf")
                if a_left <= b_right and b_left <= a_right:
                    if (m + n) % 2:
                        return float(max(a_left, b_left))
                    return (max(a_left, b_left) + min(a_right, b_right)) / 2
                if a_left > b_right:
                    hi = i - 1
                else:
                    lo = i + 1
        """,
    ),
]
