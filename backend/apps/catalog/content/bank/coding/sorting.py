from . import P

TOPIC = "sorting"

PROBLEMS = [
    P(
        "evens-before-odds", "Evens Before Odds", "easy", ["sorting", "two-pointers"],
        statement="Rearrange `nums` so that all even numbers come before all odd numbers, keeping the original order **within** the evens and within the odds. Return the result.",
        inputs="- `nums`: a list of non-negative integers",
        output="The rearranged list.",
        constraints="- `1 <= nums.length <= 5000`",
        examples=[
            ({"nums": [3, 1, 2, 4]}, [2, 4, 3, 1], ""),
            ({"nums": [0]}, [0], ""),
        ],
        approach="A stable partition: collect the evens, then the odds. (Equivalently, a stable sort with key `x % 2`.)",
        explanation="Stability is what keeps the relative order inside each group; Python's `sorted` is stable, as is building two lists.",
        time="O(n)", space="O(n)",
        code="""
        def sort_by_parity(nums: list[int]) -> list[int]:
            return [x for x in nums if x % 2 == 0] + [x for x in nums if x % 2]
        """,
    ),
    P(
        "relative-order-sort", "Sort by Another Array's Order", "easy", ["sorting", "hash-map"],
        statement="Sort `arr1` so that values appearing in `arr2` come first, in the order of `arr2` (with repeats grouped together), followed by the remaining values in ascending order. `arr2` has distinct values, all present in `arr1`.",
        inputs="- `arr1`: a list of integers\n- `arr2`: a list of distinct integers",
        output="The sorted `arr1`.",
        constraints="- `1 <= arr1.length, arr2.length <= 1000`",
        examples=[
            ({"arr1": [2, 3, 1, 3, 2, 4, 6, 7, 9, 2, 19], "arr2": [2, 1, 4, 3, 9, 6]}, [2, 2, 2, 1, 4, 3, 3, 9, 6, 7, 19], ""),
            ({"arr1": [28, 6, 22, 8, 44, 17], "arr2": [22, 28, 8, 6]}, [22, 28, 8, 6, 17, 44], ""),
        ],
        approach="Map each value of `arr2` to its position. Sort `arr1` with the key `(rank, value)`, where values not in `arr2` get rank `len(arr2)` so they come last in ascending order.",
        explanation="A tuple key encodes the two-level order in one sort.",
        time="O(n log n)", space="O(n)",
        code="""
        def relative_sort(arr1: list[int], arr2: list[int]) -> list[int]:
            rank = {v: i for i, v in enumerate(arr2)}
            return sorted(arr1, key=lambda v: (rank.get(v, len(arr2)), v))
        """,
    ),
    P(
        "out-of-place-heights", "Students Out of Place", "easy", ["sorting"],
        statement="Students should stand in non-decreasing order of height. Given the current `heights`, return how many positions hold a different height than they would in the sorted line.",
        inputs="- `heights`: a list of positive integers",
        output="The number of mismatched positions.",
        constraints="- `1 <= heights.length <= 100`",
        examples=[
            ({"heights": [1, 1, 4, 2, 1, 3]}, 3, "Expected [1, 1, 1, 2, 3, 4]; positions 2, 4 and 5 differ."),
            ({"heights": [5, 1, 2, 3, 4]}, 5, ""),
        ],
        tests=[({"heights": [1, 2, 3]}, 0)],
        approach="Sort a copy and count positions where the copy and the original differ.",
        explanation="With heights limited to a small range, counting sort would make this O(n), but a normal sort is perfectly fine for 100 students.",
        time="O(n log n)", space="O(n)",
        code="""
        def height_checker(heights: list[int]) -> int:
            return sum(a != b for a, b in zip(heights, sorted(heights)))
        """,
    ),
    P(
        "largest-product-of-three", "Largest Product of Three", "easy", ["sorting"],
        statement="Return the largest product you can get by multiplying three numbers from `nums` (different positions).",
        inputs="- `nums`: a list of integers",
        output="The maximum product of three elements.",
        constraints="- `3 <= nums.length <= 10^4`\n- `-1000 <= nums[i] <= 1000`",
        examples=[
            ({"nums": [1, 2, 3]}, 6, ""),
            ({"nums": [-10, -10, 1, 3, 2]}, 300, "(−10) × (−10) × 3."),
        ],
        tests=[({"nums": [-1, -2, -3]}, -6)],
        approach="After sorting, the answer is either the three largest numbers, or the two smallest (possibly large negatives) times the largest.",
        explanation="Two negatives make a positive, so the two most negative numbers can beat the second and third largest. No other combination can win.",
        time="O(n log n)", space="O(1) besides sorting",
        code="""
        def maximum_product(nums: list[int]) -> int:
            nums = sorted(nums)
            return max(nums[-1] * nums[-2] * nums[-3], nums[0] * nums[1] * nums[-1])
        """,
    ),
    P(
        "largest-triangle-perimeter", "Largest Triangle Perimeter", "easy", ["sorting", "greedy"],
        statement="Return the largest perimeter of a triangle with **non-zero area** formed from three of the lengths in `sides`, or `0` if no such triangle exists.",
        inputs="- `sides`: a list of positive integers",
        output="The largest perimeter, or `0`.",
        constraints="- `3 <= sides.length <= 10^4`",
        examples=[
            ({"sides": [2, 1, 2]}, 5, ""),
            ({"sides": [1, 2, 1, 10]}, 0, "No three lengths satisfy the triangle inequality."),
        ],
        approach="Sort descending. For each consecutive triple `a ≥ b ≥ c`, a triangle exists exactly when `b + c > a`; the first triple that works gives the answer.",
        explanation="For a fixed longest side `a`, the best partners are the next two largest lengths — they maximise both the perimeter and `b + c`.",
        time="O(n log n)", space="O(1) besides sorting",
        code="""
        def largest_perimeter(sides: list[int]) -> int:
            sides = sorted(sides, reverse=True)
            for i in range(len(sides) - 2):
                if sides[i + 1] + sides[i + 2] > sides[i]:
                    return sides[i] + sides[i + 1] + sides[i + 2]
            return 0
        """,
    ),
    P(
        "closest-value-pairs", "Pairs With the Smallest Difference", "easy", ["sorting"],
        statement="Given distinct integers `arr`, return every pair `[a, b]` (with `a < b`) whose difference equals the minimum difference between any two elements. List the pairs in ascending order.",
        inputs="- `arr`: a list of distinct integers",
        output="A list of pairs.",
        constraints="- `2 <= arr.length <= 10^5`",
        examples=[
            ({"arr": [4, 2, 1, 3]}, [[1, 2], [2, 3], [3, 4]], "The minimum difference is 1."),
            ({"arr": [3, 8, -10, 23, 19, -4, -14, 27]}, [[-14, -10], [19, 23], [23, 27]], "The minimum difference is 4."),
        ],
        approach="Sort. The closest pair of numbers is always adjacent in sorted order, so compute the minimum adjacent difference, then collect the adjacent pairs with that difference.",
        explanation="If two numbers had another value between them, that value would be closer to each — so only neighbours matter.",
        time="O(n log n)", space="O(n)",
        code="""
        def minimum_abs_difference(arr: list[int]) -> list[list[int]]:
            arr = sorted(arr)
            best = min(b - a for a, b in zip(arr, arr[1:]))
            return [[a, b] for a, b in zip(arr, arr[1:]) if b - a == best]
        """,
    ),
    P(
        "merge-sort", "Sort an Array (Merge Sort)", "medium", ["sorting", "recursion"],
        statement="Sort `nums` in ascending order **without** using a built-in sort, in O(n log n) time.",
        inputs="- `nums`: a list of integers",
        output="The sorted list.",
        constraints="- `1 <= nums.length <= 5 × 10^4`",
        examples=[
            ({"nums": [5, 2, 3, 1]}, [1, 2, 3, 5], ""),
            ({"nums": [5, 1, 1, 2, 0, 0]}, [0, 0, 1, 1, 2, 5], ""),
        ],
        approach="Merge sort: split the list in half, sort each half recursively, then merge the two sorted halves with two pointers.",
        explanation="There are log n levels of splitting and each level does O(n) merging work. Unlike quicksort it never degrades to O(n²), and taking from the left half on ties keeps it stable.",
        time="O(n log n)", space="O(n)",
        code="""
        def merge_sort(nums: list[int]) -> list[int]:
            if len(nums) <= 1:
                return nums[:]
            mid = len(nums) // 2
            left, right = merge_sort(nums[:mid]), merge_sort(nums[mid:])
            merged, i, j = [], 0, 0
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    merged.append(left[i])
                    i += 1
                else:
                    merged.append(right[j])
                    j += 1
            return merged + left[i:] + right[j:]
        """,
    ),
    P(
        "kth-largest", "The k-th Largest Element", "medium", ["sorting"],
        statement="Return the `k`-th largest element of `nums` (in sorted order, so duplicates count separately). Try to beat a full sort.",
        inputs="- `nums`: a list of integers\n- `k`: `1 <= k <= len(nums)`",
        output="The k-th largest value.",
        constraints="- `1 <= nums.length <= 10^5`",
        examples=[
            ({"nums": [3, 2, 1, 5, 6, 4], "k": 2}, 5, ""),
            ({"nums": [3, 2, 3, 1, 2, 4, 5, 5, 6], "k": 4}, 4, "Sorted descending: 6, 5, 5, 4, …"),
        ],
        approach="Keep a min-heap of the `k` largest values seen so far: push each value and pop the smallest whenever the heap grows past `k`. The heap's top is the answer.",
        explanation="The heap never holds more than k items, so each step is O(log k). (Quickselect averages O(n) but has an O(n²) worst case.)",
        time="O(n log k)", space="O(k)",
        code="""
        import heapq

        def find_kth_largest(nums: list[int], k: int) -> int:
            heap = []
            for x in nums:
                heapq.heappush(heap, x)
                if len(heap) > k:
                    heapq.heappop(heap)
            return heap[0]
        """,
    ),
    P(
        "largest-concatenated-number", "Largest Number From Pieces", "medium", ["sorting", "greedy"],
        statement="Arrange the non-negative integers `nums` so that their concatenation forms the largest possible number, and return it as a string.",
        inputs="- `nums`: a list of non-negative integers",
        output="The largest number as a string (no leading zeros unless the result is `0`).",
        constraints="- `1 <= nums.length <= 100`\n- `0 <= nums[i] <= 10^9`",
        examples=[
            ({"nums": [10, 2]}, "210", ""),
            ({"nums": [3, 30, 34, 5, 9]}, "9534330", ""),
        ],
        tests=[({"nums": [0, 0]}, "0")],
        approach="Sort the numbers as strings with a custom comparison: `a` goes before `b` if `a + b > b + a`. Join them; if the first piece is `0`, the whole answer is `0`.",
        explanation="Comparing the two possible concatenations decides the order of any pair, and this comparison is transitive, so sorting with it yields the best overall order.",
        time="O(n log n · d)", space="O(n · d)",
        code="""
        from functools import cmp_to_key

        def largest_number(nums: list[int]) -> str:
            pieces = sorted(map(str, nums), key=cmp_to_key(lambda a, b: -1 if a + b > b + a else (1 if a + b < b + a else 0)))
            return "0" if pieces[0] == "0" else "".join(pieces)
        """,
    ),
    P(
        "meeting-rooms-needed", "Meeting Rooms Needed", "medium", ["sorting"],
        statement="Each meeting is `[start, end)` (it ends just before `end`, so a meeting starting at `end` can reuse the room). Return the minimum number of rooms needed to hold all `intervals`.",
        inputs="- `intervals`: a list of `[start, end]` with `start < end`",
        output="The minimum number of rooms.",
        constraints="- `1 <= intervals.length <= 10^4`",
        examples=[
            ({"intervals": [[0, 30], [5, 10], [15, 20]]}, 2, ""),
            ({"intervals": [[7, 10], [2, 4]]}, 1, ""),
        ],
        tests=[({"intervals": [[1, 5], [5, 10]]}, 1)],
        approach="Sort the start times and the end times separately. Sweep through the starts; each start needs a room unless some meeting has already ended by then (advance the end pointer and reuse its room).",
        explanation="The number of rooms in use at any time is (starts so far) − (ends so far); its maximum is the answer. Ends at the same moment as a start are processed first because of `<=`.",
        time="O(n log n)", space="O(n)",
        code="""
        def min_meeting_rooms(intervals: list[list[int]]) -> int:
            starts = sorted(s for s, _ in intervals)
            ends = sorted(e for _, e in intervals)
            rooms = j = 0
            for s in starts:
                if ends[j] <= s:
                    j += 1
                else:
                    rooms += 1
            return rooms
        """,
    ),
    P(
        "research-h-index", "A Researcher's h-index", "medium", ["sorting"],
        statement="`citations[i]` is the number of citations of paper `i`. The h-index is the largest `h` such that at least `h` papers have at least `h` citations each. Return it.",
        inputs="- `citations`: a list of non-negative integers",
        output="The h-index.",
        constraints="- `1 <= citations.length <= 5000`",
        examples=[
            ({"citations": [3, 0, 6, 1, 5]}, 3, "Three papers have ≥ 3 citations."),
            ({"citations": [1, 3, 1]}, 1, ""),
        ],
        tests=[({"citations": [0]}, 0), ({"citations": [100]}, 1)],
        approach="Sort in descending order. Walk through: the paper at position `i` (0-based) is the `(i + 1)`-th best; while its citations are at least `i + 1`, `h = i + 1` is achievable.",
        explanation="After sorting, \"at least h papers with ≥ h citations\" is the same as \"the h-th best paper has ≥ h citations\".",
        time="O(n log n)", space="O(n)",
        code="""
        def h_index(citations: list[int]) -> int:
            h = 0
            for i, c in enumerate(sorted(citations, reverse=True)):
                if c >= i + 1:
                    h = i + 1
                else:
                    break
            return h
        """,
    ),
    P(
        "insert-an-interval", "Insert an Interval", "medium", ["sorting"],
        statement="`intervals` is sorted by start and non-overlapping. Insert `new` and merge where necessary so the list stays sorted and non-overlapping. Return the result.",
        inputs="- `intervals`: a sorted list of non-overlapping `[start, end]`\n- `new`: the interval to insert",
        output="The updated list of intervals.",
        constraints="- `0 <= intervals.length <= 10^4`",
        examples=[
            ({"intervals": [[1, 3], [6, 9]], "new": [2, 5]}, [[1, 5], [6, 9]], ""),
            ({"intervals": [[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], "new": [4, 8]}, [[1, 2], [3, 10], [12, 16]], "[4, 8] overlaps three intervals."),
        ],
        tests=[({"intervals": [], "new": [5, 7]}, [[5, 7]])],
        approach="Three phases: copy intervals ending before `new` starts; merge every interval that overlaps `new` into it (min of starts, max of ends); copy the rest.",
        explanation="Because the input is already sorted and disjoint, one linear pass is enough — no re-sorting needed.",
        time="O(n)", space="O(n)",
        code="""
        def insert(intervals: list[list[int]], new: list[int]) -> list[list[int]]:
            out, i, n = [], 0, len(intervals)
            start, end = new
            while i < n and intervals[i][1] < start:
                out.append(intervals[i])
                i += 1
            while i < n and intervals[i][0] <= end:
                start, end = min(start, intervals[i][0]), max(end, intervals[i][1])
                i += 1
            out.append([start, end])
            return out + intervals[i:]
        """,
    ),
    P(
        "count-inversions", "Count Inversions", "hard", ["sorting", "recursion"],
        statement="An **inversion** is a pair of indices `i < j` with `nums[i] > nums[j]`. Count the inversions in `nums` in O(n log n) time.",
        inputs="- `nums`: a list of integers",
        output="The number of inversions.",
        constraints="- `1 <= nums.length <= 10^5`",
        examples=[
            ({"nums": [2, 4, 1, 3, 5]}, 3, "(2, 1), (4, 1), (4, 3)."),
            ({"nums": [5, 4, 3, 2, 1]}, 10, "Every pair is inverted."),
        ],
        tests=[({"nums": [1, 2, 3]}, 0), ({"nums": [1, 1]}, 0)],
        approach="Modify merge sort: while merging two sorted halves, every time an element of the right half is placed before remaining elements of the left half, it forms an inversion with each of them — add `len(left) − i`.",
        explanation="Inversions inside each half are counted recursively; inversions across halves are counted during the merge, where the sorted order makes the count a single subtraction.",
        time="O(n log n)", space="O(n)",
        code="""
        def count_inversions(nums: list[int]) -> int:
            def sort(arr: list[int]) -> tuple[list[int], int]:
                if len(arr) <= 1:
                    return arr, 0
                mid = len(arr) // 2
                left, a = sort(arr[:mid])
                right, b = sort(arr[mid:])
                merged, i, j, count = [], 0, 0, a + b
                while i < len(left) and j < len(right):
                    if left[i] <= right[j]:
                        merged.append(left[i])
                        i += 1
                    else:
                        merged.append(right[j])
                        count += len(left) - i
                        j += 1
                return merged + left[i:] + right[j:], count

            return sort(nums)[1]
        """,
    ),
    P(
        "maximum-sorted-gap", "Largest Gap After Sorting", "hard", ["sorting"],
        statement="Return the largest difference between two successive elements of `nums` **in sorted order**, in linear time and space. Return `0` if there are fewer than two elements.",
        inputs="- `nums`: a list of non-negative integers",
        output="The maximum gap.",
        constraints="- `1 <= nums.length <= 10^5`\n- `0 <= nums[i] <= 10^9`",
        examples=[
            ({"nums": [3, 6, 9, 1]}, 3, "Sorted: 1, 3, 6, 9."),
            ({"nums": [10]}, 0, ""),
        ],
        tests=[({"nums": [1, 10000000]}, 9999999), ({"nums": [1, 1, 1]}, 0)],
        approach="Pigeonhole buckets: with `n` values between `lo` and `hi`, the maximum gap is at least `(hi − lo)/(n − 1)`. Use buckets of that size and record only each bucket's min and max; the answer is the largest jump from one non-empty bucket's max to the next one's min.",
        explanation="Two values in the same bucket differ by less than the bucket size, which is at most the answer, so gaps inside buckets can be ignored.",
        time="O(n)", space="O(n)",
        code="""
        def maximum_gap(nums: list[int]) -> int:
            if len(nums) < 2:
                return 0
            lo, hi, n = min(nums), max(nums), len(nums)
            if lo == hi:
                return 0
            size = max(1, (hi - lo) // (n - 1))
            count = (hi - lo) // size + 1
            mins, maxs = [None] * count, [None] * count
            for x in nums:
                b = (x - lo) // size
                mins[b] = x if mins[b] is None else min(mins[b], x)
                maxs[b] = x if maxs[b] is None else max(maxs[b], x)
            best, prev = 0, lo
            for b in range(count):
                if mins[b] is not None:
                    best = max(best, mins[b] - prev)
                    prev = maxs[b]
            return best
        """,
    ),
    P(
        "smaller-after-self", "Smaller Numbers to the Right", "hard", ["sorting", "recursion"],
        statement="For each element of `nums`, count how many elements **to its right** are strictly smaller. Return the list of counts.",
        inputs="- `nums`: a list of integers",
        output="A list of counts, one per element.",
        constraints="- `1 <= nums.length <= 10^5`",
        examples=[
            ({"nums": [5, 2, 6, 1]}, [2, 1, 1, 0], "To the right of 5 are 2 and 1."),
            ({"nums": [-1, -1]}, [0, 0], "Equal values don't count."),
        ],
        tests=[({"nums": [-1]}, [0])],
        approach="Merge sort the **indices** by value. During each merge, when an element from the left half is placed, every right-half element already placed is smaller and lies to its right — add that number to its count.",
        explanation="It is the inversion count done per element: the merge step attributes each cross-half inversion to the left element that forms it.",
        time="O(n log n)", space="O(n)",
        code="""
        def count_smaller(nums: list[int]) -> list[int]:
            counts = [0] * len(nums)

            def sort(idx: list[int]) -> list[int]:
                if len(idx) <= 1:
                    return idx
                mid = len(idx) // 2
                left, right = sort(idx[:mid]), sort(idx[mid:])
                merged, j = [], 0
                for i in left:
                    while j < len(right) and nums[right[j]] < nums[i]:
                        merged.append(right[j])
                        j += 1
                    counts[i] += j
                    merged.append(i)
                return merged + right[j:]

            sort(list(range(len(nums))))
            return counts
        """,
    ),
]
