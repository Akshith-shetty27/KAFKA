from . import P

TOPIC = "two-pointers"

PROBLEMS = [
    P(
        "squares-of-sorted-array", "Squares of a Sorted Array", "easy", ["two-pointers"],
        statement="Given an integer array `nums` sorted in non-decreasing order, return the squares of its numbers, also sorted in non-decreasing order, in O(n) time.",
        inputs="- `nums`: a sorted list of integers (may include negatives)",
        output="A sorted list of the squares.",
        constraints="- `1 <= nums.length <= 10^4`\n- `-10^4 <= nums[i] <= 10^4`",
        examples=[
            ({"nums": [-4, -1, 0, 3, 10]}, [0, 1, 9, 16, 100], ""),
            ({"nums": [-7, -3, 2, 3, 11]}, [4, 9, 9, 49, 121], ""),
        ],
        approach="The largest square is at one of the two ends (the most negative or the most positive number). Compare the ends, write the larger square into the output from the back, and move that pointer inward.",
        explanation="Squares decrease from both ends towards zero, so the ends always hold the biggest remaining square. Filling the result right to left produces sorted order without sorting.",
        time="O(n)", space="O(n) for the output",
        code="""
        def sorted_squares(nums: list[int]) -> list[int]:
            result = [0] * len(nums)
            lo, hi = 0, len(nums) - 1
            for k in range(len(nums) - 1, -1, -1):
                if abs(nums[lo]) > abs(nums[hi]):
                    result[k] = nums[lo] ** 2
                    lo += 1
                else:
                    result[k] = nums[hi] ** 2
                    hi -= 1
            return result
        """,
    ),
    P(
        "reverse-only-vowels", "Reverse Only the Vowels", "easy", ["two-pointers"],
        statement="Reverse only the vowels (`a e i o u`, either case) of the string `s`; every other character stays where it is.",
        inputs="- `s`: a string of printable ASCII characters",
        output="The string with its vowels in reverse order.",
        constraints="- `1 <= s.length <= 3 × 10^5`",
        examples=[
            ({"s": "hello"}, "holle", "The vowels e, o swap places."),
            ({"s": "programming"}, "prigrammong", "o, a, i become i, a, o."),
        ],
        approach="Two pointers from both ends: move each inward until it sits on a vowel, swap the two vowels, and continue until the pointers meet.",
        explanation="Swapping the outermost unswapped vowels each time reverses the vowel sequence while consonants are never moved.",
        time="O(n)", space="O(n) (strings are immutable in Python)",
        code="""
        def reverse_vowels(s: str) -> str:
            vowels = set("aeiouAEIOU")
            chars = list(s)
            lo, hi = 0, len(chars) - 1
            while lo < hi:
                if chars[lo] not in vowels:
                    lo += 1
                elif chars[hi] not in vowels:
                    hi -= 1
                else:
                    chars[lo], chars[hi] = chars[hi], chars[lo]
                    lo, hi = lo + 1, hi - 1
            return "".join(chars)
        """,
    ),
    P(
        "merge-two-sorted-arrays", "Merge Two Sorted Arrays", "easy", ["two-pointers"],
        statement="Given two sorted integer arrays `a` and `b`, return one sorted array containing all elements of both.",
        inputs="- `a`: a sorted list of integers\n- `b`: a sorted list of integers",
        output="A sorted list with all `len(a) + len(b)` elements.",
        constraints="- `0 <= a.length, b.length <= 10^5`",
        examples=[
            ({"a": [1, 2, 3], "b": [2, 5, 6]}, [1, 2, 2, 3, 5, 6], ""),
            ({"a": [], "b": [1]}, [1], "One array may be empty."),
        ],
        approach="Keep a pointer into each array; repeatedly append the smaller of the two current elements and advance that pointer. When one array runs out, append the rest of the other.",
        explanation="This is the merge step of merge sort: the smallest remaining element is always at one of the two pointers.",
        time="O(m + n)", space="O(m + n)",
        code="""
        def merge_sorted(a: list[int], b: list[int]) -> list[int]:
            i = j = 0
            out = []
            while i < len(a) and j < len(b):
                if a[i] <= b[j]:
                    out.append(a[i])
                    i += 1
                else:
                    out.append(b[j])
                    j += 1
            return out + a[i:] + b[j:]
        """,
    ),
    P(
        "remove-value-in-place", "Remove a Value in Place", "easy", ["two-pointers"],
        statement="Remove every occurrence of `val` from `nums` **in place**. Return `k`, the number of remaining elements; the first `k` positions of `nums` must hold them (in any order).",
        inputs="- `nums`: a list of integers\n- `val`: the value to remove",
        output="An integer `k`: how many elements are not equal to `val`.",
        constraints="- `0 <= nums.length <= 100`\n- `0 <= nums[i], val <= 100`",
        examples=[
            ({"nums": [3, 2, 2, 3], "val": 3}, 2, "nums starts with [2, 2]."),
            ({"nums": [0, 1, 2, 2, 3, 0, 4, 2], "val": 2}, 5, "nums starts with 0, 1, 3, 0, 4."),
        ],
        approach="A *write* pointer marks where the next kept element goes. Scan with a *read* pointer; copy every element that isn't `val` to the write position and advance it.",
        explanation="Kept elements are copied forward in their original order, and nothing past the write pointer matters to the caller.",
        time="O(n)", space="O(1)",
        code="""
        def remove_element(nums: list[int], val: int) -> int:
            write = 0
            for x in nums:
                if x != val:
                    nums[write] = x
                    write += 1
            return write
        """,
    ),
    P(
        "sort-three-colours", "Sort Three Colours", "medium", ["two-pointers"],
        statement="`nums` contains only `0`, `1` and `2` (three colours). Sort it **in place in a single pass** without a library sort, and return it.",
        inputs="- `nums`: a list of 0s, 1s and 2s",
        output="The same list, sorted.",
        constraints="- `1 <= nums.length <= 300`",
        examples=[
            ({"nums": [2, 0, 2, 1, 1, 0]}, [0, 0, 1, 1, 2, 2], ""),
            ({"nums": [2, 0, 1]}, [0, 1, 2], ""),
        ],
        approach="Dutch national flag: three pointers `low`, `mid`, `high`. A 0 at `mid` is swapped to `low` (both advance); a 1 just advances `mid`; a 2 is swapped to `high` (only `high` moves back, because the swapped-in value is unchecked).",
        explanation="Invariant: everything before `low` is 0, between `low` and `mid` is 1, after `high` is 2. Each step shrinks the unknown region by one.",
        time="O(n)", space="O(1)",
        code="""
        def sort_colours(nums: list[int]) -> list[int]:
            low = mid = 0
            high = len(nums) - 1
            while mid <= high:
                if nums[mid] == 0:
                    nums[low], nums[mid] = nums[mid], nums[low]
                    low += 1
                    mid += 1
                elif nums[mid] == 1:
                    mid += 1
                else:
                    nums[mid], nums[high] = nums[high], nums[mid]
                    high -= 1
            return nums
        """,
    ),
    P(
        "three-sum-closest", "Three Numbers Closest to a Target", "medium", ["two-pointers", "sorting"],
        statement="Choose three elements of `nums` (different positions) whose sum is **closest** to `target`, and return that sum. Exactly one closest sum exists.",
        inputs="- `nums`: a list of integers\n- `target`: an integer",
        output="The sum of the best triple.",
        constraints="- `3 <= nums.length <= 500`\n- `-1000 <= nums[i] <= 1000`\n- `-10^4 <= target <= 10^4`",
        examples=[
            ({"nums": [-1, 2, 1, -4], "target": 1}, 2, "-1 + 2 + 1 = 2 is the closest."),
            ({"nums": [0, 0, 0], "target": 1}, 0, ""),
        ],
        approach="Sort. Fix the first element `i`; search the rest with two pointers: if the current sum is below the target move the left pointer right, otherwise move the right pointer left. Track the closest sum seen.",
        explanation="With the array sorted, moving the left pointer can only increase the sum and moving the right one can only decrease it, so the pair loop examines every useful option in linear time per `i`.",
        time="O(n²)", space="O(1) besides sorting",
        code="""
        def three_sum_closest(nums: list[int], target: int) -> int:
            nums = sorted(nums)
            best = nums[0] + nums[1] + nums[2]
            for i in range(len(nums) - 2):
                lo, hi = i + 1, len(nums) - 1
                while lo < hi:
                    total = nums[i] + nums[lo] + nums[hi]
                    if abs(total - target) < abs(best - target):
                        best = total
                    if total < target:
                        lo += 1
                    elif total > target:
                        hi -= 1
                    else:
                        return total
            return best
        """,
    ),
    P(
        "keep-at-most-two-duplicates", "Keep At Most Two of Each", "medium", ["two-pointers"],
        statement="`nums` is sorted. Remove duplicates **in place** so each value appears at most twice, keeping the order. Return `k`, the length of the result (its elements fill the first `k` positions).",
        inputs="- `nums`: a sorted list of integers",
        output="An integer `k`.",
        constraints="- `1 <= nums.length <= 3 × 10^4`",
        examples=[
            ({"nums": [1, 1, 1, 2, 2, 3]}, 5, "nums starts with [1, 1, 2, 2, 3]."),
            ({"nums": [0, 0, 1, 1, 1, 1, 2, 3, 3]}, 7, "nums starts with [0, 0, 1, 1, 2, 3, 3]."),
        ],
        approach="A write pointer `k`. Copy `x` to position `k` unless it equals `nums[k − 2]` — then we already kept two copies of it.",
        explanation="Because the array is sorted, a third copy of `x` would sit right after two equal values; comparing with the element two places back detects exactly that.",
        time="O(n)", space="O(1)",
        code="""
        def remove_duplicates(nums: list[int]) -> int:
            k = 0
            for x in nums:
                if k < 2 or nums[k - 2] != x:
                    nums[k] = x
                    k += 1
            return k
        """,
    ),
    P(
        "boats-for-everyone", "Boats for Everyone", "medium", ["two-pointers", "greedy"],
        statement="`people[i]` is the weight of person `i`. Each boat carries **at most two** people and at most `limit` kilograms. Return the minimum number of boats needed to carry everyone (no person is heavier than `limit`).",
        inputs="- `people`: a list of weights\n- `limit`: the maximum load of one boat",
        output="The minimum number of boats.",
        constraints="- `1 <= people.length <= 5 × 10^4`\n- `1 <= people[i] <= limit <= 3 × 10^4`",
        examples=[
            ({"people": [3, 2, 2, 1], "limit": 3}, 3, "(1, 2), (2), (3)."),
            ({"people": [3, 5, 3, 4], "limit": 5}, 4, "No two people fit together."),
        ],
        tests=[({"people": [1, 2], "limit": 3}, 1)],
        approach="Sort the weights. Put the heaviest remaining person in a boat; if the lightest remaining person fits with them, add them too. Move the pointers and count boats.",
        explanation="The heaviest person needs a boat anyway. If anyone can share it, the lightest can — and pairing the lightest with the heaviest never makes a later pairing impossible (exchange argument).",
        time="O(n log n)", space="O(1) besides sorting",
        code="""
        def num_boats(people: list[int], limit: int) -> int:
            people = sorted(people)
            lo, hi, boats = 0, len(people) - 1, 0
            while lo <= hi:
                if people[lo] + people[hi] <= limit:
                    lo += 1
                hi -= 1
                boats += 1
            return boats
        """,
    ),
    P(
        "palindrome-after-one-deletion", "Palindrome After At Most One Deletion", "medium", ["two-pointers"],
        statement="Return `true` if the string `s` can become a palindrome after deleting **at most one** character.",
        inputs="- `s`: a string of lowercase letters",
        output="`true` or `false`.",
        constraints="- `1 <= s.length <= 10^5`",
        examples=[
            ({"s": "abca"}, True, "Delete 'c' (or 'b')."),
            ({"s": "abc"}, False, ""),
        ],
        tests=[({"s": "aba"}, True), ({"s": "deeee"}, True), ({"s": "eedede"}, True)],
        approach="Move two pointers inward while the characters match. At the first mismatch you must delete one of the two characters: check whether `s[lo+1 … hi]` or `s[lo … hi-1]` is a palindrome.",
        explanation="Everything outside the first mismatch already matches, so only these two choices can work. Each check is linear, so the total stays O(n).",
        time="O(n)", space="O(1)",
        code="""
        def valid_palindrome(s: str) -> bool:
            def is_pal(lo: int, hi: int) -> bool:
                while lo < hi:
                    if s[lo] != s[hi]:
                        return False
                    lo, hi = lo + 1, hi - 1
                return True

            lo, hi = 0, len(s) - 1
            while lo < hi:
                if s[lo] != s[hi]:
                    return is_pal(lo + 1, hi) or is_pal(lo, hi - 1)
                lo, hi = lo + 1, hi - 1
            return True
        """,
    ),
    P(
        "four-sum", "Four Numbers Summing to a Target", "hard", ["two-pointers", "sorting"],
        statement="Return all **unique** quadruplets `[a, b, c, d]` of elements of `nums` (different positions) with `a + b + c + d == target`. Each quadruplet is listed in ascending order; the list may be in any order.",
        inputs="- `nums`: a list of integers\n- `target`: an integer",
        output="A list of unique quadruplets.",
        constraints="- `1 <= nums.length <= 200`\n- `-10^9 <= nums[i], target <= 10^9`",
        examples=[
            ({"nums": [1, 0, -1, 0, -2, 2], "target": 0}, [[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]], ""),
            ({"nums": [2, 2, 2, 2, 2], "target": 8}, [[2, 2, 2, 2]], "Only one unique quadruplet."),
        ],
        compare="unordered",
        approach="Sort. Fix the first two elements with two nested loops (skipping repeated values), then find the remaining pair with two pointers, skipping duplicates after each match.",
        explanation="Sorting makes duplicates adjacent, so skipping equal neighbours at every level guarantees each quadruplet appears once. The two-pointer inner search turns O(n⁴) into O(n³).",
        time="O(n³)", space="O(1) besides output",
        code="""
        def four_sum(nums: list[int], target: int) -> list[list[int]]:
            nums = sorted(nums)
            n, result = len(nums), []
            for i in range(n - 3):
                if i and nums[i] == nums[i - 1]:
                    continue
                for j in range(i + 1, n - 2):
                    if j > i + 1 and nums[j] == nums[j - 1]:
                        continue
                    lo, hi = j + 1, n - 1
                    while lo < hi:
                        total = nums[i] + nums[j] + nums[lo] + nums[hi]
                        if total < target:
                            lo += 1
                        elif total > target:
                            hi -= 1
                        else:
                            result.append([nums[i], nums[j], nums[lo], nums[hi]])
                            lo += 1
                            while lo < hi and nums[lo] == nums[lo - 1]:
                                lo += 1
                            hi -= 1
            return result
        """,
    ),
]
