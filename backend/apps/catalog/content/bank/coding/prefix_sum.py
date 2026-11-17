from . import P

TOPIC = "prefix-sum"

MATRIX = [[3, 0, 1, 4, 2], [5, 6, 3, 2, 1], [1, 2, 0, 1, 5], [4, 1, 0, 1, 7], [1, 0, 3, 0, 5]]

PROBLEMS = [
    P(
        "running-sum", "Running Sum", "easy", ["prefix-sum"],
        statement="Return the running sum of `nums`: element `i` of the result is `nums[0] + nums[1] + … + nums[i]`.",
        inputs="- `nums`: a list of integers",
        output="A list of the same length with the running totals.",
        constraints="- `1 <= nums.length <= 1000`\n- `-10^6 <= nums[i] <= 10^6`",
        examples=[
            ({"nums": [1, 2, 3, 4]}, [1, 3, 6, 10], ""),
            ({"nums": [3, 1, 2, 10, 1]}, [3, 4, 6, 16, 17], ""),
        ],
        approach="Each running total is the previous total plus the current element.",
        explanation="This is the prefix-sum array itself — the building block for every other problem in this topic.",
        time="O(n)", space="O(n) for the output",
        code="""
        def running_sum(nums: list[int]) -> list[int]:
            out, total = [], 0
            for x in nums:
                total += x
                out.append(total)
            return out
        """,
    ),
    P(
        "highest-altitude", "Highest Altitude on a Ride", "easy", ["prefix-sum"],
        statement="A cyclist starts at altitude `0`. `gain[i]` is the change in altitude between point `i` and point `i + 1`. Return the highest altitude reached (including the start).",
        inputs="- `gain`: a list of altitude changes",
        output="The highest altitude.",
        constraints="- `1 <= gain.length <= 100`\n- `-100 <= gain[i] <= 100`",
        examples=[
            ({"gain": [-5, 1, 5, 0, -7]}, 1, "Altitudes: 0, −5, −4, 1, 1, −6."),
            ({"gain": [-4, -3, -2, -1, 4, 3, 2]}, 0, "The start is the highest point."),
        ],
        approach="Altitudes are the prefix sums of `gain`, starting from 0. Track the running total and its maximum.",
        explanation="Starting the maximum at 0 includes the starting point, which matters when every gain is negative.",
        time="O(n)", space="O(1)",
        code="""
        def largest_altitude(gain: list[int]) -> int:
            altitude = best = 0
            for g in gain:
                altitude += g
                best = max(best, altitude)
            return best
        """,
    ),
    P(
        "left-right-sum-difference", "Left and Right Sum Differences", "easy", ["prefix-sum"],
        statement="For each index `i`, let `left` be the sum of the elements **before** `i` and `right` the sum of the elements **after** `i`. Return the list of `|left − right|`.",
        inputs="- `nums`: a list of positive integers",
        output="A list of absolute differences, one per index.",
        constraints="- `1 <= nums.length <= 1000`\n- `1 <= nums[i] <= 10^5`",
        examples=[
            ({"nums": [10, 4, 8, 3]}, [15, 1, 11, 22], "Left sums 0, 10, 14, 22; right sums 15, 11, 3, 0."),
            ({"nums": [1]}, [0], ""),
        ],
        approach="Compute the total once. Walking left to right, `right = total − left − nums[i]`; then add `nums[i]` to `left`.",
        explanation="One running sum gives both sides, so no second array is needed.",
        time="O(n)", space="O(1) besides the output",
        code="""
        def left_right_difference(nums: list[int]) -> list[int]:
            total, left, out = sum(nums), 0, []
            for x in nums:
                right = total - left - x
                out.append(abs(left - right))
                left += x
            return out
        """,
    ),
    P(
        "minimum-start-value", "Smallest Safe Starting Value", "easy", ["prefix-sum"],
        statement="You start with a positive integer `start` and add the elements of `nums` one by one. Return the smallest `start` such that the running total is **at least 1 at every step**.",
        inputs="- `nums`: a list of integers",
        output="The minimum positive starting value.",
        constraints="- `1 <= nums.length <= 100`\n- `-100 <= nums[i] <= 100`",
        examples=[
            ({"nums": [-3, 2, -3, 4, 2]}, 5, "With 5 the totals are 2, 4, 1, 5, 7."),
            ({"nums": [1, 2]}, 1, "The start must still be positive."),
        ],
        tests=[({"nums": [1, -2, -3]}, 5)],
        approach="Find the lowest prefix sum `m`. The start must satisfy `start + m >= 1`, so the answer is `max(1, 1 − m)`.",
        explanation="Only the worst moment matters: if the running total survives its lowest point, it survives every point.",
        time="O(n)", space="O(1)",
        code="""
        def min_start_value(nums: list[int]) -> int:
            total = lowest = 0
            for x in nums:
                total += x
                lowest = min(lowest, total)
            return max(1, 1 - lowest)
        """,
    ),
    P(
        "subarrays-divisible-by-k", "Subarrays With Sum Divisible by k", "medium", ["prefix-sum", "hash-map"],
        statement="Count the non-empty contiguous subarrays of `nums` whose sum is divisible by `k`.",
        inputs="- `nums`: a list of integers\n- `k`: a positive integer",
        output="The number of such subarrays.",
        constraints="- `1 <= nums.length <= 3 × 10^4`\n- `-10^4 <= nums[i] <= 10^4`\n- `2 <= k <= 10^4`",
        examples=[
            ({"nums": [4, 5, 0, -2, -3, 1], "k": 5}, 7, ""),
            ({"nums": [5], "k": 9}, 0, ""),
        ],
        approach="A subarray sum is `prefix[j] − prefix[i]`; it is divisible by `k` exactly when the two prefixes have the same remainder mod `k`. Count remainders as you go; each earlier prefix with the same remainder forms one subarray.",
        explanation="Start the counter with remainder 0 seen once (the empty prefix). Python's `%` returns a non-negative remainder even for negative sums; in Java/C++ add `k` before taking the remainder.",
        time="O(n)", space="O(k)",
        code="""
        def subarrays_div_by_k(nums: list[int], k: int) -> int:
            seen = {0: 1}
            total = count = 0
            for x in nums:
                total += x
                r = total % k
                count += seen.get(r, 0)
                seen[r] = seen.get(r, 0) + 1
            return count
        """,
    ),
    P(
        "multiple-of-k-subarray", "A Subarray Summing to a Multiple of k", "medium", ["prefix-sum", "hash-map"],
        statement="Return `true` if `nums` has a contiguous subarray of **length at least 2** whose sum is a multiple of `k` (0 counts as a multiple).",
        inputs="- `nums`: a list of non-negative integers\n- `k`: a positive integer",
        output="`true` or `false`.",
        constraints="- `1 <= nums.length <= 10^5`\n- `1 <= k <= 2^31 - 1`",
        examples=[
            ({"nums": [23, 2, 4, 6, 7], "k": 6}, True, "[2, 4] sums to 6."),
            ({"nums": [23, 2, 6, 4, 7], "k": 13}, False, ""),
        ],
        tests=[({"nums": [0, 0], "k": 7}, True), ({"nums": [5, 0], "k": 3}, False)],
        approach="Store the **first** index where each prefix remainder mod `k` appears (remainder 0 at index −1). When a remainder repeats at index `j` and its first index `i` satisfies `j − i >= 2`, the subarray between them works.",
        explanation="Keeping only the earliest index maximises the length, which is what the ‘at least 2’ condition needs.",
        time="O(n)", space="O(min(n, k))",
        code="""
        def check_subarray_sum(nums: list[int], k: int) -> bool:
            first = {0: -1}
            total = 0
            for j, x in enumerate(nums):
                total = (total + x) % k
                if total in first:
                    if j - first[total] >= 2:
                        return True
                else:
                    first[total] = j
            return False
        """,
    ),
    P(
        "matrix-region-sum", "Sum of a Matrix Region", "medium", ["prefix-sum"],
        statement="Design a class `NumMatrix` built from a 2-D `matrix` that answers many queries `sum_region(r1, c1, r2, c2)`: the sum of the rectangle with top-left `(r1, c1)` and bottom-right `(r2, c2)`, inclusive — each in O(1).",
        inputs="- `NumMatrix(matrix)`: the constructor\n- `sum_region(r1, c1, r2, c2)`: a query with `r1 <= r2`, `c1 <= c2`",
        output="Each query returns an integer sum.",
        constraints="- `1 <= rows, cols <= 200`\n- Up to `10^4` queries",
        examples=[
            ({"calls": [("NumMatrix", MATRIX), ("sum_region", 2, 1, 4, 3), ("sum_region", 1, 1, 2, 2), ("sum_region", 1, 2, 2, 4)]}, [8, 11, 12], "Three queries on the same matrix."),
            ({"calls": [("NumMatrix", [[1, 2], [3, 4]]), ("sum_region", 0, 0, 1, 1), ("sum_region", 1, 0, 1, 1)]}, [10, 7], ""),
        ],
        approach="Precompute `P[r][c]` = sum of the rectangle from `(0, 0)` to `(r − 1, c − 1)`. A query is then `P[r2+1][c2+1] − P[r1][c2+1] − P[r2+1][c1] + P[r1][c1]`.",
        explanation="Inclusion–exclusion: subtract the strip above and the strip to the left, then add back their overlap, which was subtracted twice.",
        time="O(rows·cols) to build, O(1) per query", space="O(rows·cols)",
        code="""
        class NumMatrix:
            def __init__(self, matrix: list[list[int]]):
                rows, cols = len(matrix), len(matrix[0])
                self.p = [[0] * (cols + 1) for _ in range(rows + 1)]
                for r in range(rows):
                    for c in range(cols):
                        self.p[r + 1][c + 1] = matrix[r][c] + self.p[r][c + 1] + self.p[r + 1][c] - self.p[r][c]

            def sum_region(self, r1: int, c1: int, r2: int, c2: int) -> int:
                p = self.p
                return p[r2 + 1][c2 + 1] - p[r1][c2 + 1] - p[r2 + 1][c1] + p[r1][c1]
        """,
    ),
    P(
        "range-additions", "Apply Range Additions", "medium", ["prefix-sum"],
        statement="An array of `length` zeros receives `updates`, each `[start, end, inc]`: add `inc` to every element from `start` to `end` inclusive. Return the final array.",
        inputs="- `length`: the array length\n- `updates`: a list of `[start, end, inc]`",
        output="The array after all updates.",
        constraints="- `1 <= length <= 10^5`\n- `0 <= updates.length <= 10^4`",
        examples=[
            ({"length": 5, "updates": [[1, 3, 2], [2, 4, 3], [0, 2, -2]]}, [-2, 0, 3, 5, 3], ""),
            ({"length": 3, "updates": [[0, 2, 1]]}, [1, 1, 1], ""),
        ],
        approach="Use a difference array: for each update add `inc` at `start` and subtract it at `end + 1`. The prefix sums of the difference array are the final values.",
        explanation="Each update becomes O(1) work instead of O(end − start), and a single prefix-sum pass applies them all.",
        time="O(length + updates)", space="O(length)",
        code="""
        def apply_updates(length: int, updates: list[list[int]]) -> list[int]:
            diff = [0] * (length + 1)
            for start, end, inc in updates:
                diff[start] += inc
                diff[end + 1] -= inc
            out, total = [], 0
            for i in range(length):
                total += diff[i]
                out.append(total)
            return out
        """,
    ),
    P(
        "shared-ride-capacity", "Can the Shared Ride Fit Everyone?", "medium", ["prefix-sum"],
        statement="A van drives east only. Each trip `[passengers, start, end]` picks up `passengers` at kilometre `start` and drops them at kilometre `end`. Return `true` if the van's `capacity` is never exceeded.",
        inputs="- `trips`: a list of `[passengers, start, end]` with `start < end`\n- `capacity`: seats in the van",
        output="`true` or `false`.",
        constraints="- `1 <= trips.length <= 1000`\n- `0 <= start < end <= 1000`",
        examples=[
            ({"trips": [[2, 1, 5], [3, 3, 7]], "capacity": 4}, False, "Between km 3 and 5 there are 5 passengers."),
            ({"trips": [[2, 1, 5], [3, 3, 7]], "capacity": 5}, True, ""),
        ],
        tests=[({"trips": [[2, 1, 5], [3, 5, 7]], "capacity": 3}, True)],
        approach="Record +passengers at each pickup point and −passengers at each drop-off point, then sweep the kilometres in order, keeping a running load.",
        explanation="Passengers leave at `end` before new ones board there, so applying the drop-off at the same index as a later pickup is correct.",
        time="O(trips + max km)", space="O(max km)",
        code="""
        def car_pooling(trips: list[list[int]], capacity: int) -> bool:
            change = [0] * 1001
            for passengers, start, end in trips:
                change[start] += passengers
                change[end] -= passengers
            load = 0
            for delta in change:
                load += delta
                if load > capacity:
                    return False
            return True
        """,
    ),
    P(
        "odd-sum-subarrays", "Subarrays With an Odd Sum", "medium", ["prefix-sum"],
        statement="Count the contiguous subarrays of `arr` whose sum is **odd**.",
        inputs="- `arr`: a list of positive integers",
        output="The number of odd-sum subarrays.",
        constraints="- `1 <= arr.length <= 10^5`",
        examples=[
            ({"arr": [1, 3, 5]}, 4, "[1], [3], [5] and [1, 3, 5]."),
            ({"arr": [2, 4, 6]}, 0, ""),
        ],
        tests=[({"arr": [1, 2, 3, 4, 5, 6, 7]}, 16)],
        approach="A subarray sum is odd when its two bounding prefix sums have different parity. Count even and odd prefixes as you go (the empty prefix is even); a new odd prefix pairs with every earlier even one, and vice versa.",
        explanation="Only parities matter, so two counters replace a full hash map.",
        time="O(n)", space="O(1)",
        code="""
        def num_odd_subarrays(arr: list[int]) -> int:
            even, odd, total, count = 1, 0, 0, 0
            for x in arr:
                total += x
                if total % 2:
                    count += even
                    odd += 1
                else:
                    count += odd
                    even += 1
            return count
        """,
    ),
    P(
        "submatrices-summing-to-target", "Submatrices Summing to a Target", "hard", ["prefix-sum", "hash-map"],
        statement="Count the non-empty submatrices (rectangles of cells) of `matrix` whose sum equals `target`.",
        inputs="- `matrix`: a 2-D list of integers\n- `target`: an integer",
        output="The number of such submatrices.",
        constraints="- `1 <= rows, cols <= 100`\n- `-1000 <= matrix[i][j] <= 1000`",
        examples=[
            ({"matrix": [[0, 1, 0], [1, 1, 1], [0, 1, 0]], "target": 0}, 4, "The four corner zeros."),
            ({"matrix": [[1, -1], [-1, 1]], "target": 0}, 5, "Two 1×2, two 2×1 and the whole 2×2."),
        ],
        tests=[({"matrix": [[904]], "target": 0}, 0)],
        approach="Fix a pair of rows `top ≤ bottom`. Collapse the rows between them into one array of column sums; now count subarrays of that array summing to `target` with prefix sums and a hash map (as in *Subarrays Summing to K*).",
        explanation="Every rectangle is uniquely determined by its row range and its column range, and each row range is handled with a linear-time 1-D count.",
        time="O(rows² · cols)", space="O(cols)",
        code="""
        def num_submatrix_sum_target(matrix: list[list[int]], target: int) -> int:
            rows, cols = len(matrix), len(matrix[0])
            count = 0
            for top in range(rows):
                col_sums = [0] * cols
                for bottom in range(top, rows):
                    for c in range(cols):
                        col_sums[c] += matrix[bottom][c]
                    seen, running = {0: 1}, 0
                    for value in col_sums:
                        running += value
                        count += seen.get(running - target, 0)
                        seen[running] = seen.get(running, 0) + 1
            return count
        """,
    ),
]
