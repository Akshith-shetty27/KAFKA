"""
Coding content. Problem statements are written for KAFKA; the underlying
problems are classic interview exercises.

Format (read by `manage.py seed_content`):
  topic    → slug, name, description, questions[]
  question → slug, title, type="coding", difficulty, patterns[], statement,
             constraints, examples[{input, output, explanation}], approach,
             explanation, time, space, solutions{language: code}
Strings may be indented; the loader dedents them. Order = list order.
"""

PATTERNS = [
    {"slug": "hash-map", "name": "Hash Map", "description": "Trade memory for O(1) lookups of what you've already seen."},
    {"slug": "two-pointers", "name": "Two Pointers", "description": "Move two indices toward each other (or together) to avoid a nested loop."},
    {"slug": "sliding-window", "name": "Sliding Window", "description": "Maintain a contiguous window and update it incrementally as it slides."},
    {"slug": "prefix-sum", "name": "Prefix Sum", "description": "Precompute running totals so any range sum is a subtraction."},
    {"slug": "binary-search", "name": "Binary Search", "description": "Halve the search space using a monotonic condition."},
    {"slug": "fast-slow-pointers", "name": "Fast & Slow Pointers", "description": "Two pointers moving at different speeds detect cycles and midpoints."},
    {"slug": "in-place-reversal", "name": "In-place Reversal", "description": "Re-point links one node at a time without extra memory."},
    {"slug": "stack", "name": "Stack", "description": "Last-in, first-out: match the most recent unresolved item."},
    {"slug": "monotonic-stack", "name": "Monotonic Stack", "description": "A stack kept sorted to find the next greater/smaller element in one pass."},
    {"slug": "bfs", "name": "Breadth-First Search", "description": "Explore level by level with a queue."},
    {"slug": "dfs", "name": "Depth-First Search", "description": "Explore as deep as possible before backtracking."},
    {"slug": "dynamic-programming", "name": "Dynamic Programming", "description": "Build answers from answers to smaller subproblems."},
    {"slug": "greedy", "name": "Greedy", "description": "Make the locally best choice when it provably leads to the global best."},
]

CATEGORY = {
    "slug": "coding",
    "name": "Coding",
    "glyph": "{ }",
    "description": "Data structures and algorithms, organised by the patterns interviewers actually test.",
    "topics": [
        # ------------------------------------------------------------------ arrays
        {
            "slug": "arrays",
            "name": "Arrays",
            "description": "Indexing, scanning and bookkeeping over contiguous data.",
            "questions": [
                {
                    "slug": "pair-with-target-sum",
                    "title": "Pair With Target Sum",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": ["hash-map"],
                    "statement": """
                        You are given an integer array `nums` and an integer `target`.
                        Return the **indices** of the two different elements whose values add up to `target`.

                        Exactly one valid pair exists. You may return the two indices in any order.
                    """,
                    "constraints": """
                        - `2 <= nums.length <= 10^5`
                        - `-10^9 <= nums[i], target <= 10^9`
                        - Exactly one valid answer exists.
                    """,
                    "examples": [
                        {"input": "nums = [4, 9, 1, 7], target = 8", "output": "[2, 3]", "explanation": "nums[2] + nums[3] = 1 + 7 = 8."},
                        {"input": "nums = [5, 5], target = 10", "output": "[0, 1]", "explanation": "The two 5s are different elements."},
                    ],
                    "approach": """
                        Checking every pair is O(n²). Instead, walk the array once and remember every value
                        you've seen in a hash map (`value → index`). For each number `x`, the partner you need
                        is `target - x`. If that partner is already in the map, you've found the pair.
                    """,
                    "explanation": """
                        Every pair (i, j) with i < j is discovered exactly when the scan reaches j, because
                        `nums[i]` was stored earlier. Storing *after* the check prevents pairing an element
                        with itself (e.g. `target = 10`, `x = 5` seen once).
                    """,
                    "time": "O(n)",
                    "space": "O(n)",
                    "solutions": {
                        "python": """
                            def pair_with_target_sum(nums: list[int], target: int) -> list[int]:
                                seen = {}  # value -> index
                                for i, x in enumerate(nums):
                                    partner = target - x
                                    if partner in seen:
                                        return [seen[partner], i]
                                    seen[x] = i
                                return []  # unreachable: one answer is guaranteed
                        """,
                    },
                },
                {
                    "slug": "maximum-subarray-sum",
                    "title": "Maximum Subarray Sum",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["greedy", "dynamic-programming"],
                    "statement": """
                        Given an integer array `nums`, find the contiguous, non-empty subarray with the
                        **largest sum** and return that sum.
                    """,
                    "constraints": """
                        - `1 <= nums.length <= 10^5`
                        - `-10^4 <= nums[i] <= 10^4`
                    """,
                    "examples": [
                        {"input": "nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]", "output": "6", "explanation": "The subarray [4, -1, 2, 1] sums to 6."},
                        {"input": "nums = [-3, -1, -2]", "output": "-1", "explanation": "All negative: the best subarray is the single largest element."},
                    ],
                    "approach": """
                        Scan left to right keeping `best_ending_here`: the best sum of a subarray that ends at
                        the current index. At each element you either **extend** the previous subarray or
                        **start fresh** at this element — whichever is larger (Kadane's algorithm).
                    """,
                    "explanation": """
                        If the best subarray ending at `i - 1` has a negative sum, attaching it to `nums[i]`
                        can only make things worse, so starting fresh is optimal. The overall answer is the
                        maximum of `best_ending_here` over all positions. Initialising with `nums[0]` (not 0)
                        handles all-negative arrays.
                    """,
                    "time": "O(n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def max_subarray_sum(nums: list[int]) -> int:
                                best_ending_here = best = nums[0]
                                for x in nums[1:]:
                                    best_ending_here = max(x, best_ending_here + x)
                                    best = max(best, best_ending_here)
                                return best
                        """,
                    },
                },
                {
                    "slug": "move-zeroes-to-end",
                    "title": "Move Zeroes to the End",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": ["two-pointers"],
                    "statement": """
                        Given an integer array `nums`, move every `0` to the end while keeping the relative
                        order of the non-zero elements. Do it **in place** and return the array.
                    """,
                    "constraints": """
                        - `1 <= nums.length <= 10^4`
                        - `-2^31 <= nums[i] <= 2^31 - 1`
                    """,
                    "examples": [
                        {"input": "nums = [0, 1, 0, 3, 12]", "output": "[1, 3, 12, 0, 0]", "explanation": ""},
                        {"input": "nums = [0]", "output": "[0]", "explanation": ""},
                    ],
                    "approach": """
                        Keep a `write` pointer for where the next non-zero value belongs. Scan with a `read`
                        pointer; every non-zero value is swapped into position `write`, then `write` advances.
                    """,
                    "explanation": """
                        Everything left of `write` is exactly the non-zero values seen so far, in their original
                        order. Swapping (rather than overwriting) pushes the zeros forward, so when the scan ends
                        all zeros sit after `write`. One pass, no extra array.
                    """,
                    "time": "O(n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def move_zeroes(nums: list[int]) -> list[int]:
                                write = 0
                                for read in range(len(nums)):
                                    if nums[read] != 0:
                                        nums[write], nums[read] = nums[read], nums[write]
                                        write += 1
                                return nums
                        """,
                    },
                },
                {
                    "slug": "product-except-self",
                    "title": "Product of Everything Else",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["prefix-sum"],
                    "statement": """
                        Given an integer array `nums`, return an array `answer` where `answer[i]` is the product
                        of every element of `nums` **except** `nums[i]`. You may not use division, and the
                        solution must run in O(n).
                    """,
                    "constraints": """
                        - `2 <= nums.length <= 10^5`
                        - `-30 <= nums[i] <= 30`
                        - Every prefix and suffix product fits in a 32-bit integer.
                    """,
                    "examples": [
                        {"input": "nums = [1, 2, 3, 4]", "output": "[24, 12, 8, 6]", "explanation": ""},
                        {"input": "nums = [-1, 1, 0, -3, 3]", "output": "[0, 0, 9, 0, 0]", "explanation": ""},
                    ],
                    "approach": """
                        `answer[i]` = (product of everything left of `i`) × (product of everything right of `i`).
                        Fill `answer` with left products in one pass, then sweep from the right multiplying in a
                        running right product.
                    """,
                    "explanation": """
                        This is the prefix-sum idea with multiplication. Division would fail on zeros, and
                        recomputing products per index is O(n²). Reusing the output array for the left products
                        keeps extra space at O(1) (the output itself doesn't count).
                    """,
                    "time": "O(n)",
                    "space": "O(1) extra",
                    "solutions": {
                        "python": """
                            def product_except_self(nums: list[int]) -> list[int]:
                                n = len(nums)
                                answer = [1] * n
                                for i in range(1, n):
                                    answer[i] = answer[i - 1] * nums[i - 1]
                                right = 1
                                for i in range(n - 1, -1, -1):
                                    answer[i] *= right
                                    right *= nums[i]
                                return answer
                        """,
                    },
                },
            ],
        },
        # ----------------------------------------------------------------- strings
        {
            "slug": "strings",
            "name": "Strings",
            "description": "Character counting, canonical forms and string building.",
            "questions": [
                {
                    "slug": "anagram-check",
                    "title": "Anagram Check",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": ["hash-map"],
                    "statement": """
                        Given two strings `s` and `t`, return `true` if `t` is an anagram of `s` — that is,
                        it uses exactly the same characters the same number of times — and `false` otherwise.
                    """,
                    "constraints": """
                        - `1 <= s.length, t.length <= 5 * 10^4`
                        - Both strings contain lowercase English letters only.
                    """,
                    "examples": [
                        {"input": 's = "listen", t = "silent"', "output": "true", "explanation": "Same letters, different order."},
                        {"input": 's = "rat", t = "car"', "output": "false", "explanation": "'t' and 'c' differ."},
                    ],
                    "approach": """
                        Different lengths can never be anagrams. Otherwise count each character of `s`, then
                        decrement the counts with the characters of `t`. Every count must end at zero.
                    """,
                    "explanation": """
                        Two strings are anagrams exactly when their character frequency tables are equal.
                        With a fixed 26-letter alphabet the table is constant size, so space is O(1).
                        Sorting both strings also works but costs O(n log n).
                    """,
                    "time": "O(n)",
                    "space": "O(1) — at most 26 keys",
                    "solutions": {
                        "python": """
                            from collections import Counter

                            def is_anagram(s: str, t: str) -> bool:
                                if len(s) != len(t):
                                    return False
                                return Counter(s) == Counter(t)
                        """,
                    },
                },
                {
                    "slug": "group-anagrams",
                    "title": "Group Anagrams",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["hash-map"],
                    "statement": """
                        Given a list of strings `words`, group the words that are anagrams of each other.
                        Return the groups in any order; the order of words inside a group doesn't matter.
                    """,
                    "constraints": """
                        - `1 <= words.length <= 10^4`
                        - `0 <= words[i].length <= 100`
                        - Lowercase English letters only.
                    """,
                    "examples": [
                        {"input": 'words = ["eat", "tea", "tan", "ate", "nat", "bat"]', "output": '[["eat","tea","ate"], ["tan","nat"], ["bat"]]', "explanation": ""},
                        {"input": 'words = [""]', "output": '[[""]]', "explanation": "The empty string is its own group."},
                    ],
                    "approach": """
                        Anagrams share a **canonical key**. Use a 26-length letter-count tuple (or the sorted
                        word) as the key in a hash map from key → list of words.
                    """,
                    "explanation": """
                        Two words land in the same bucket if and only if their keys are equal, which is
                        exactly the anagram condition. The count-tuple key costs O(k) per word versus
                        O(k log k) for sorting, where k is the word length.
                    """,
                    "time": "O(n · k)",
                    "space": "O(n · k)",
                    "solutions": {
                        "python": """
                            from collections import defaultdict

                            def group_anagrams(words: list[str]) -> list[list[str]]:
                                groups = defaultdict(list)
                                for word in words:
                                    counts = [0] * 26
                                    for ch in word:
                                        counts[ord(ch) - ord("a")] += 1
                                    groups[tuple(counts)].append(word)
                                return list(groups.values())
                        """,
                    },
                },
                {
                    "slug": "first-unique-character",
                    "title": "First Unique Character",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": ["hash-map"],
                    "statement": """
                        Given a string `s`, return the index of the first character that appears exactly once.
                        If there is none, return `-1`.
                    """,
                    "constraints": """
                        - `1 <= s.length <= 10^5`
                        - Lowercase English letters only.
                    """,
                    "examples": [
                        {"input": 's = "placement"', "output": "0", "explanation": "'p' appears once."},
                        {"input": 's = "aabbcd"', "output": "4", "explanation": "'c' at index 4 is the first unique character."},
                        {"input": 's = "aabb"', "output": "-1", "explanation": ""},
                    ],
                    "approach": """
                        Two passes: first count every character, then walk the string again and return the
                        first index whose count is 1.
                    """,
                    "explanation": """
                        A single pass can't know whether a character repeats later, so the counts must be
                        complete before deciding. Both passes are linear and the table has at most 26 entries.
                    """,
                    "time": "O(n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            from collections import Counter

                            def first_unique(s: str) -> int:
                                counts = Counter(s)
                                for i, ch in enumerate(s):
                                    if counts[ch] == 1:
                                        return i
                                return -1
                        """,
                    },
                },
                {
                    "slug": "longest-palindromic-substring",
                    "title": "Longest Palindromic Substring",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["two-pointers"],
                    "statement": """
                        Given a string `s`, return the longest contiguous substring that reads the same forwards
                        and backwards. If several have the same length, return any of them.
                    """,
                    "constraints": """
                        - `1 <= s.length <= 1000`
                        - Letters and digits only.
                    """,
                    "examples": [
                        {"input": 's = "forgeeksskeegfor"', "output": '"geeksskeeg"', "explanation": ""},
                        {"input": 's = "cbbd"', "output": '"bb"', "explanation": ""},
                    ],
                    "approach": """
                        Every palindrome has a centre — a single character (odd length) or a gap between two
                        characters (even length). For each of the `2n - 1` centres, expand outwards while both
                        ends match, and keep the longest.
                    """,
                    "explanation": """
                        Checking every substring is O(n³). Expanding around centres finds every maximal
                        palindrome in O(n) per centre, O(n²) overall, with no extra memory. (Manacher's algorithm
                        does it in O(n), but expand-around-centre is what interviewers expect.)
                    """,
                    "time": "O(n²)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def longest_palindrome(s: str) -> str:
                                def expand(left: int, right: int) -> tuple[int, int]:
                                    while left >= 0 and right < len(s) and s[left] == s[right]:
                                        left -= 1
                                        right += 1
                                    return left + 1, right  # slice bounds of the palindrome

                                best_start, best_end = 0, 1
                                for centre in range(len(s)):
                                    for start, end in (expand(centre, centre), expand(centre, centre + 1)):
                                        if end - start > best_end - best_start:
                                            best_start, best_end = start, end
                                return s[best_start:best_end]
                        """,
                    },
                },
            ],
        },
        # ------------------------------------------------------------ two pointers
        {
            "slug": "two-pointers",
            "name": "Two Pointers",
            "description": "Shrink a search space from both ends instead of nesting loops.",
            "questions": [
                {
                    "slug": "palindrome-after-cleaning",
                    "title": "Palindrome After Cleaning",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": ["two-pointers"],
                    "statement": """
                        A phrase is a palindrome if, after converting letters to lowercase and removing every
                        non-alphanumeric character, it reads the same forwards and backwards.
                        Given a string `s`, return `true` if it is a palindrome under this rule.
                    """,
                    "constraints": """
                        - `1 <= s.length <= 2 * 10^5`
                        - `s` contains printable ASCII characters.
                    """,
                    "examples": [
                        {"input": 's = "Was it a car or a cat I saw?"', "output": "true", "explanation": 'Cleaned: "wasitacaroracatisaw".'},
                        {"input": 's = "placement"', "output": "false", "explanation": ""},
                    ],
                    "approach": """
                        Put one pointer at each end. Skip characters that aren't letters or digits, compare
                        the two characters case-insensitively, and move both pointers inward.
                    """,
                    "explanation": """
                        A string is a palindrome iff every mirrored pair matches. The pointers visit each
                        mirrored pair exactly once and never build the cleaned string, so extra space is O(1).
                    """,
                    "time": "O(n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def is_clean_palindrome(s: str) -> bool:
                                left, right = 0, len(s) - 1
                                while left < right:
                                    if not s[left].isalnum():
                                        left += 1
                                    elif not s[right].isalnum():
                                        right -= 1
                                    elif s[left].lower() != s[right].lower():
                                        return False
                                    else:
                                        left += 1
                                        right -= 1
                                return True
                        """,
                    },
                },
                {
                    "slug": "widest-water-container",
                    "title": "Widest Water Container",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["two-pointers", "greedy"],
                    "statement": """
                        `heights[i]` is the height of a vertical wall at position `i`. Choose two walls; together
                        with the ground they form a container holding `min(heights[i], heights[j]) * (j - i)`
                        units of water. Return the **maximum** amount of water any two walls can hold.
                    """,
                    "constraints": """
                        - `2 <= heights.length <= 10^5`
                        - `0 <= heights[i] <= 10^4`
                    """,
                    "examples": [
                        {"input": "heights = [1, 8, 6, 2, 5, 4, 8, 3, 7]", "output": "49", "explanation": "Walls at index 1 (8) and 8 (7): min(8, 7) * 7 = 49."},
                        {"input": "heights = [2, 2]", "output": "2", "explanation": ""},
                    ],
                    "approach": """
                        Start with the widest container (both ends). The shorter wall limits the water, and
                        moving the taller wall inward can never help (width shrinks, height can't exceed the
                        shorter wall). So always move the pointer at the **shorter** wall.
                    """,
                    "explanation": """
                        When `heights[left] < heights[right]`, every container using `left` with any wall
                        between them is no better than the current one, so `left` can be discarded safely.
                        Each step discards one wall, giving a single O(n) pass.
                    """,
                    "time": "O(n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def max_water(heights: list[int]) -> int:
                                left, right = 0, len(heights) - 1
                                best = 0
                                while left < right:
                                    width = right - left
                                    best = max(best, min(heights[left], heights[right]) * width)
                                    if heights[left] < heights[right]:
                                        left += 1
                                    else:
                                        right -= 1
                                return best
                        """,
                    },
                },
                {
                    "slug": "trapped-rainwater",
                    "title": "Trapped Rainwater",
                    "type": "coding",
                    "difficulty": "hard",
                    "patterns": ["two-pointers"],
                    "statement": """
                        `elevation[i]` is the height of a bar of width 1. After it rains, water collects in the
                        dips between bars. Return the total units of water trapped.
                    """,
                    "constraints": """
                        - `1 <= elevation.length <= 2 * 10^4`
                        - `0 <= elevation[i] <= 10^5`
                    """,
                    "examples": [
                        {"input": "elevation = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]", "output": "6", "explanation": ""},
                        {"input": "elevation = [4, 2, 0, 3, 2, 5]", "output": "9", "explanation": ""},
                    ],
                    "approach": """
                        Water above bar `i` is `min(max_left(i), max_right(i)) - elevation[i]`. Instead of two
                        prefix arrays, use two pointers with running `left_max` and `right_max`: whichever side
                        has the smaller max is the limiting side, so its water can be settled immediately.
                    """,
                    "explanation": """
                        If `left_max <= right_max`, the true right maximum for the left pointer is at least
                        `right_max`, so the left bar's water is fully determined by `left_max`. Symmetrically
                        for the right side. Each bar is settled once.
                    """,
                    "time": "O(n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def trapped_water(elevation: list[int]) -> int:
                                left, right = 0, len(elevation) - 1
                                left_max = right_max = water = 0
                                while left < right:
                                    if elevation[left] <= elevation[right]:
                                        left_max = max(left_max, elevation[left])
                                        water += left_max - elevation[left]
                                        left += 1
                                    else:
                                        right_max = max(right_max, elevation[right])
                                        water += right_max - elevation[right]
                                        right -= 1
                                return water
                        """,
                    },
                },
                {
                    "slug": "pair-sum-sorted",
                    "title": "Pair Sum in a Sorted Array",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": ["two-pointers"],
                    "statement": """
                        `numbers` is sorted in non-decreasing order. Return the **1-based** indices `[i, j]`
                        (`i < j`) of the two numbers that add up to `target`. Exactly one answer exists. Use only
                        O(1) extra space.
                    """,
                    "constraints": """
                        - `2 <= numbers.length <= 3 * 10^4`
                        - `numbers` is sorted ascending.
                    """,
                    "examples": [
                        {"input": "numbers = [2, 7, 11, 15], target = 9", "output": "[1, 2]", "explanation": ""},
                        {"input": "numbers = [-3, -1, 0, 4, 8], target = 5", "output": "[1, 5]", "explanation": "-3 + 8 = 5"},
                    ],
                    "approach": """
                        Start with pointers at both ends. If the sum is too small, move the left pointer right
                        (to a larger value); if too large, move the right pointer left.
                    """,
                    "explanation": """
                        Sortedness makes each move safe: when the sum is too small, the current left value can't
                        pair with anything (the right pointer is already at the largest remaining value), so it is
                        discarded. Compare with the hash-map version, which needs O(n) memory.
                    """,
                    "time": "O(n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def pair_sum_sorted(numbers: list[int], target: int) -> list[int]:
                                left, right = 0, len(numbers) - 1
                                while left < right:
                                    total = numbers[left] + numbers[right]
                                    if total == target:
                                        return [left + 1, right + 1]
                                    if total < target:
                                        left += 1
                                    else:
                                        right -= 1
                                return []
                        """,
                    },
                },
                {
                    "slug": "three-sum-zero",
                    "title": "Triplets Summing to Zero",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["two-pointers"],
                    "statement": """
                        Given an integer array `nums`, return every **unique** triplet `[a, b, c]` of elements at
                        distinct positions with `a + b + c = 0`. The result must not contain duplicate triplets.
                    """,
                    "constraints": """
                        - `3 <= nums.length <= 3000`
                        - `-10^5 <= nums[i] <= 10^5`
                    """,
                    "examples": [
                        {"input": "nums = [-1, 0, 1, 2, -1, -4]", "output": "[[-1, -1, 2], [-1, 0, 1]]", "explanation": ""},
                        {"input": "nums = [0, 0, 0, 0]", "output": "[[0, 0, 0]]", "explanation": "Duplicates collapse into one triplet."},
                    ],
                    "approach": """
                        Sort the array. Fix the first number `nums[i]`, then solve "pair sum = -nums[i]" on the
                        rest with two pointers. Skip equal neighbours (for `i`, and for the pointers after a match)
                        so each triplet is produced once.
                    """,
                    "explanation": """
                        Sorting costs O(n log n) but turns the inner search into an O(n) two-pointer sweep, for
                        O(n²) overall instead of O(n³). Because the array is sorted, duplicates are adjacent, so
                        skipping repeats is a simple comparison with the previous element.
                    """,
                    "time": "O(n²)",
                    "space": "O(1) besides the output (sorting in place)",
                    "solutions": {
                        "python": """
                            def three_sum(nums: list[int]) -> list[list[int]]:
                                nums.sort()
                                result = []
                                for i in range(len(nums) - 2):
                                    if i > 0 and nums[i] == nums[i - 1]:
                                        continue
                                    left, right = i + 1, len(nums) - 1
                                    while left < right:
                                        total = nums[i] + nums[left] + nums[right]
                                        if total < 0:
                                            left += 1
                                        elif total > 0:
                                            right -= 1
                                        else:
                                            result.append([nums[i], nums[left], nums[right]])
                                            left += 1
                                            right -= 1
                                            while left < right and nums[left] == nums[left - 1]:
                                                left += 1
                                return result
                        """,
                    },
                },
            ],
        },
        # ---------------------------------------------------------- sliding window
        {
            "slug": "sliding-window",
            "name": "Sliding Window",
            "description": "Contiguous ranges updated incrementally instead of recomputed.",
            "questions": [
                {
                    "slug": "best-average-window",
                    "title": "Best Average Window",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": ["sliding-window"],
                    "statement": """
                        Given an integer array `nums` and an integer `k`, find the contiguous subarray of
                        length exactly `k` with the largest average, and return that average.
                    """,
                    "constraints": """
                        - `1 <= k <= nums.length <= 10^5`
                        - `-10^4 <= nums[i] <= 10^4`
                    """,
                    "examples": [
                        {"input": "nums = [1, 12, -5, -6, 50, 3], k = 4", "output": "12.75", "explanation": "(12 - 5 - 6 + 50) / 4 = 12.75"},
                        {"input": "nums = [5], k = 1", "output": "5.0", "explanation": ""},
                    ],
                    "approach": """
                        Sum the first `k` elements. Then slide: add the element entering on the right and
                        subtract the one leaving on the left. Track the maximum sum and divide by `k` once.
                    """,
                    "explanation": """
                        Consecutive windows share `k - 1` elements, so each new window sum is an O(1) update of
                        the previous one. Maximising the sum is the same as maximising the average because
                        `k` is fixed.
                    """,
                    "time": "O(n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def best_average(nums: list[int], k: int) -> float:
                                window = sum(nums[:k])
                                best = window
                                for i in range(k, len(nums)):
                                    window += nums[i] - nums[i - k]
                                    best = max(best, window)
                                return best / k
                        """,
                    },
                },
                {
                    "slug": "longest-unique-substring",
                    "title": "Longest Substring Without Repeats",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["sliding-window", "hash-map"],
                    "statement": """
                        Given a string `s`, return the length of the longest substring in which no character
                        appears more than once.
                    """,
                    "constraints": """
                        - `0 <= s.length <= 5 * 10^4`
                        - `s` may contain letters, digits, symbols and spaces.
                    """,
                    "examples": [
                        {"input": 's = "abcabcbb"', "output": "3", "explanation": '"abc" is the longest such substring.'},
                        {"input": 's = "pwwkew"', "output": "3", "explanation": '"wke". Note "pwke" is not contiguous.'},
                    ],
                    "approach": """
                        Grow a window `[left, right]`. Remember the last index of each character. When
                        `s[right]` already appears inside the window, jump `left` to one past that previous
                        occurrence. The window is always repeat-free; record its largest size.
                    """,
                    "explanation": """
                        `left` only ever moves forward, so each index enters and leaves the window at most once.
                        Using `max(left, last[ch] + 1)` ignores stale occurrences that are already left of the
                        window.
                    """,
                    "time": "O(n)",
                    "space": "O(min(n, alphabet))",
                    "solutions": {
                        "python": """
                            def longest_unique_substring(s: str) -> int:
                                last = {}
                                left = best = 0
                                for right, ch in enumerate(s):
                                    if ch in last and last[ch] >= left:
                                        left = last[ch] + 1
                                    last[ch] = right
                                    best = max(best, right - left + 1)
                                return best
                        """,
                    },
                },
                {
                    "slug": "shortest-subarray-at-least-target",
                    "title": "Shortest Subarray With Sum ≥ Target",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["sliding-window"],
                    "statement": """
                        Given an array of **positive** integers `nums` and a positive integer `target`, return the
                        length of the shortest contiguous subarray whose sum is at least `target`, or `0` if there
                        is none.
                    """,
                    "constraints": """
                        - `1 <= nums.length <= 10^5`
                        - `1 <= nums[i] <= 10^4`
                        - `1 <= target <= 10^9`
                    """,
                    "examples": [
                        {"input": "nums = [2, 3, 1, 2, 4, 3], target = 7", "output": "2", "explanation": "[4, 3]"},
                        {"input": "nums = [1, 1, 1], target = 11", "output": "0", "explanation": ""},
                    ],
                    "approach": """
                        Grow the window on the right. Whenever its sum reaches `target`, record its length and
                        shrink from the left while the sum stays ≥ `target`.
                    """,
                    "explanation": """
                        With positive numbers, extending a window only increases its sum and shrinking only
                        decreases it — that monotonicity is what makes a variable-size window valid. Each index
                        enters and leaves the window once, so the loop is O(n).
                    """,
                    "time": "O(n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def min_subarray_len(target: int, nums: list[int]) -> int:
                                best = float("inf")
                                left = window = 0
                                for right, x in enumerate(nums):
                                    window += x
                                    while window >= target:
                                        best = min(best, right - left + 1)
                                        window -= nums[left]
                                        left += 1
                                return 0 if best == float("inf") else best
                        """,
                    },
                },
                {
                    "slug": "minimum-window-substring",
                    "title": "Minimum Window Containing All Characters",
                    "type": "coding",
                    "difficulty": "hard",
                    "patterns": ["sliding-window", "hash-map"],
                    "statement": """
                        Given strings `s` and `t`, return the shortest substring of `s` that contains every
                        character of `t` (including repeats). Return `""` if no such window exists.
                    """,
                    "constraints": """
                        - `1 <= s.length, t.length <= 10^5`
                        - Upper- and lowercase English letters.
                    """,
                    "examples": [
                        {"input": 's = "ADOBECODEBANC", t = "ABC"', "output": '"BANC"', "explanation": ""},
                        {"input": 's = "a", t = "aa"', "output": '""', "explanation": "t needs two 'a's."},
                    ],
                    "approach": """
                        Count what `t` needs. Expand the window to the right, tracking how many required
                        characters are fully satisfied. Once all are satisfied, shrink from the left as far as
                        possible, recording the smallest valid window.
                    """,
                    "explanation": """
                        `missing` counts how many characters (with multiplicity) the window still lacks, so the
                        "is it valid?" check is O(1) instead of comparing two tables. Both pointers only move
                        forward, so the total work is O(|s| + |t|).
                    """,
                    "time": "O(|s| + |t|)",
                    "space": "O(alphabet)",
                    "solutions": {
                        "python": """
                            from collections import Counter

                            def min_window(s: str, t: str) -> str:
                                need = Counter(t)
                                missing = len(t)
                                left = 0
                                best = (0, float("inf"))
                                for right, ch in enumerate(s):
                                    if need[ch] > 0:
                                        missing -= 1
                                    need[ch] -= 1
                                    while missing == 0:
                                        if right - left < best[1] - best[0]:
                                            best = (left, right)
                                        need[s[left]] += 1
                                        if need[s[left]] > 0:
                                            missing += 1
                                        left += 1
                                return "" if best[1] == float("inf") else s[best[0]:best[1] + 1]
                        """,
                    },
                },
            ],
        },
        # -------------------------------------------------------------- prefix sum
        {
            "slug": "prefix-sum",
            "name": "Prefix Sum",
            "description": "Running totals that turn range questions into subtraction.",
            "questions": [
                {
                    "slug": "range-sum-queries",
                    "title": "Range Sum Queries",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": ["prefix-sum"],
                    "statement": """
                        You are given an array `nums` and a list of queries, each `[left, right]` (inclusive,
                        0-indexed). Return the sum of `nums[left..right]` for every query.
                    """,
                    "constraints": """
                        - `1 <= nums.length, queries.length <= 10^5`
                        - `0 <= left <= right < nums.length`
                    """,
                    "examples": [
                        {"input": "nums = [3, -1, 4, 2, 5], queries = [[0, 2], [1, 4], [3, 3]]", "output": "[6, 10, 2]", "explanation": "3-1+4 = 6; -1+4+2+5 = 10; 2."},
                    ],
                    "approach": """
                        Build `prefix` where `prefix[i]` is the sum of the first `i` elements (so
                        `prefix[0] = 0`). Then `sum(left..right) = prefix[right + 1] - prefix[left]`.
                    """,
                    "explanation": """
                        Summing each query directly is O(n) per query → O(n·q). One O(n) preprocessing pass
                        makes every query O(1). The extra leading 0 removes the special case for `left = 0`.
                    """,
                    "time": "O(n + q)",
                    "space": "O(n)",
                    "solutions": {
                        "python": """
                            def range_sums(nums: list[int], queries: list[list[int]]) -> list[int]:
                                prefix = [0]
                                for x in nums:
                                    prefix.append(prefix[-1] + x)
                                return [prefix[r + 1] - prefix[l] for l, r in queries]
                        """,
                    },
                },
                {
                    "slug": "subarrays-summing-to-k",
                    "title": "Subarrays Summing to K",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["prefix-sum", "hash-map"],
                    "statement": """
                        Given an integer array `nums` (which may contain negatives) and an integer `k`, return
                        the number of contiguous subarrays whose sum equals `k`.
                    """,
                    "constraints": """
                        - `1 <= nums.length <= 2 * 10^4`
                        - `-1000 <= nums[i] <= 1000`
                        - `-10^7 <= k <= 10^7`
                    """,
                    "examples": [
                        {"input": "nums = [1, 1, 1], k = 2", "output": "2", "explanation": "[1,1] at indices 0–1 and 1–2."},
                        {"input": "nums = [3, 4, -7, 7], k = 7", "output": "3", "explanation": "[3, 4], [7] and [3, 4, -7, 7]."},
                    ],
                    "approach": """
                        A subarray `(i, j]` sums to `k` exactly when `prefix[j] - prefix[i] = k`, i.e. when an
                        earlier prefix equals `prefix[j] - k`. Scan once, keeping a hash map of how many times
                        each prefix sum has occurred, starting with `{0: 1}`.
                    """,
                    "explanation": """
                        A sliding window doesn't work here because negative numbers break the "grow / shrink"
                        monotonicity. Counting matching earlier prefixes counts every valid start for each end.
                        For `[3, 4, -7, 7]` with k = 7 the prefixes are 0, 3, 7, 0, 7. The first 7 matches one
                        earlier 0 → `[3, 4]`. The last 7 matches two earlier 0s → `[3, 4, -7, 7]` and `[7]`.
                    """,
                    "time": "O(n)",
                    "space": "O(n)",
                    "solutions": {
                        "python": """
                            from collections import defaultdict

                            def count_subarrays(nums: list[int], k: int) -> int:
                                seen = defaultdict(int)
                                seen[0] = 1
                                running = count = 0
                                for x in nums:
                                    running += x
                                    count += seen[running - k]
                                    seen[running] += 1
                                return count
                        """,
                    },
                },
                {
                    "slug": "balance-index",
                    "title": "Balance Index",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": ["prefix-sum"],
                    "statement": """
                        Return the leftmost index `i` of `nums` where the sum of the elements strictly to its
                        left equals the sum strictly to its right. Return `-1` if no such index exists.
                    """,
                    "constraints": """
                        - `1 <= nums.length <= 10^4`
                        - `-1000 <= nums[i] <= 1000`
                    """,
                    "examples": [
                        {"input": "nums = [1, 7, 3, 6, 5, 6]", "output": "3", "explanation": "1 + 7 + 3 = 11 = 5 + 6"},
                        {"input": "nums = [2, 1, -1]", "output": "0", "explanation": "Left of index 0 is empty (0); right is 1 - 1 = 0."},
                    ],
                    "approach": """
                        Compute the total once. Walking left to right with a running `left_sum`, the right sum at
                        index `i` is `total - left_sum - nums[i]`.
                    """,
                    "explanation": """
                        One prefix total replaces recomputing both sides for every index (O(n²)). Checking before
                        adding `nums[i]` to `left_sum` keeps the element itself out of both sides.
                    """,
                    "time": "O(n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def balance_index(nums: list[int]) -> int:
                                total = sum(nums)
                                left_sum = 0
                                for i, x in enumerate(nums):
                                    if left_sum == total - left_sum - x:
                                        return i
                                    left_sum += x
                                return -1
                        """,
                    },
                },
                {
                    "slug": "longest-balanced-binary-subarray",
                    "title": "Longest Subarray With Equal 0s and 1s",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["prefix-sum", "hash-map"],
                    "statement": """
                        Given a binary array `nums`, return the length of the longest contiguous subarray with an
                        equal number of `0`s and `1`s.
                    """,
                    "constraints": """
                        - `1 <= nums.length <= 10^5`
                        - `nums[i]` is `0` or `1`.
                    """,
                    "examples": [
                        {"input": "nums = [0, 1, 0]", "output": "2", "explanation": "[0, 1] or [1, 0]"},
                        {"input": "nums = [0, 0, 1, 0, 1, 1, 0]", "output": "6", "explanation": "nums[1..6] or nums[0..5]"},
                    ],
                    "approach": """
                        Treat `0` as `-1`. A subarray is balanced exactly when its sum is 0, i.e. when the same
                        running sum appears twice. Store the **first** index where each running sum occurs.
                    """,
                    "explanation": """
                        If the running sum at `j` equals the running sum at an earlier `i`, the elements in
                        `(i, j]` sum to 0. Keeping only the first occurrence maximises `j - i`. Seeding the map
                        with `{0: -1}` handles subarrays that start at index 0.
                    """,
                    "time": "O(n)",
                    "space": "O(n)",
                    "solutions": {
                        "python": """
                            def longest_balanced(nums: list[int]) -> int:
                                first_seen = {0: -1}
                                running = best = 0
                                for i, x in enumerate(nums):
                                    running += 1 if x == 1 else -1
                                    if running in first_seen:
                                        best = max(best, i - first_seen[running])
                                    else:
                                        first_seen[running] = i
                                return best
                        """,
                    },
                },
            ],
        },
        # ----------------------------------------------------------- binary search
        {
            "slug": "binary-search",
            "name": "Binary Search",
            "description": "Logarithmic search over anything with a monotonic yes/no boundary.",
            "questions": [
                {
                    "slug": "search-sorted-array",
                    "title": "Search a Sorted Array",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": ["binary-search"],
                    "statement": """
                        Given an array of distinct integers `nums` sorted in ascending order and a value
                        `target`, return the index of `target`, or `-1` if it is not present.
                        Your solution must run in O(log n).
                    """,
                    "constraints": """
                        - `1 <= nums.length <= 10^4`
                        - All values are distinct and sorted ascending.
                    """,
                    "examples": [
                        {"input": "nums = [-4, 0, 3, 8, 12], target = 8", "output": "3", "explanation": ""},
                        {"input": "nums = [-4, 0, 3, 8, 12], target = 5", "output": "-1", "explanation": ""},
                    ],
                    "approach": """
                        Keep a closed range `[lo, hi]`. Compare the middle element with the target and discard
                        the half that cannot contain it. Stop when the range is empty.
                    """,
                    "explanation": """
                        Sortedness means everything left of `mid` is smaller and everything right is larger, so
                        one comparison removes half of the candidates. Writing `mid = lo + (hi - lo) // 2`
                        avoids overflow in fixed-width languages.
                    """,
                    "time": "O(log n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def binary_search(nums: list[int], target: int) -> int:
                                lo, hi = 0, len(nums) - 1
                                while lo <= hi:
                                    mid = lo + (hi - lo) // 2
                                    if nums[mid] == target:
                                        return mid
                                    if nums[mid] < target:
                                        lo = mid + 1
                                    else:
                                        hi = mid - 1
                                return -1
                        """,
                    },
                },
                {
                    "slug": "minimum-in-rotated-array",
                    "title": "Minimum in a Rotated Sorted Array",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["binary-search"],
                    "statement": """
                        A sorted array of distinct integers was rotated at an unknown pivot (for example
                        `[1, 2, 3, 4, 5]` → `[4, 5, 1, 2, 3]`). Return the smallest element in O(log n).
                    """,
                    "constraints": """
                        - `1 <= nums.length <= 5000`
                        - All values are distinct.
                    """,
                    "examples": [
                        {"input": "nums = [4, 5, 6, 7, 0, 1, 2]", "output": "0", "explanation": ""},
                        {"input": "nums = [11, 13, 15, 17]", "output": "11", "explanation": "Not rotated (or rotated a full turn)."},
                    ],
                    "approach": """
                        Compare the middle with the **rightmost** element. If `nums[mid] > nums[hi]`, the drop
                        (and the minimum) is to the right of `mid`; otherwise the minimum is at `mid` or to its
                        left. Narrow until `lo == hi`.
                    """,
                    "explanation": """
                        The array is two ascending runs. Elements of the left run are all larger than
                        `nums[hi]`; elements of the right run are all ≤ `nums[hi]`. That gives a monotonic
                        condition to binary-search on. Keeping `hi = mid` (not `mid - 1`) never discards the
                        minimum.
                    """,
                    "time": "O(log n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def find_min_rotated(nums: list[int]) -> int:
                                lo, hi = 0, len(nums) - 1
                                while lo < hi:
                                    mid = (lo + hi) // 2
                                    if nums[mid] > nums[hi]:
                                        lo = mid + 1
                                    else:
                                        hi = mid
                                return nums[lo]
                        """,
                    },
                },
                {
                    "slug": "integer-square-root",
                    "title": "Integer Square Root",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": ["binary-search"],
                    "statement": """
                        Given a non-negative integer `x`, return the square root of `x` rounded **down** to the
                        nearest integer, without using any built-in power or square-root function.
                    """,
                    "constraints": """
                        - `0 <= x <= 2^31 - 1`
                    """,
                    "examples": [
                        {"input": "x = 8", "output": "2", "explanation": "√8 ≈ 2.83 → 2"},
                        {"input": "x = 49", "output": "7", "explanation": ""},
                    ],
                    "approach": """
                        Binary-search the answer: find the largest `m` with `m * m <= x`. The condition is true
                        for small `m` and false for large `m`, so it has a single boundary.
                    """,
                    "explanation": """
                        This is "binary search on the answer" — the array isn't stored, it's the range of
                        candidate integers `[0, x]`. Each step halves the range, so it takes ~31 steps for any
                        32-bit input.
                    """,
                    "time": "O(log x)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def int_sqrt(x: int) -> int:
                                lo, hi = 0, x
                                while lo < hi:
                                    mid = (lo + hi + 1) // 2  # round up so the loop always progresses
                                    if mid * mid <= x:
                                        lo = mid
                                    else:
                                        hi = mid - 1
                                return lo
                        """,
                    },
                },
                {
                    "slug": "first-and-last-position",
                    "title": "First and Last Position of a Value",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["binary-search"],
                    "statement": """
                        `nums` is sorted ascending and may contain duplicates. Return `[first, last]`, the first
                        and last index of `target`, or `[-1, -1]` if it's absent. Run in O(log n).
                    """,
                    "constraints": """
                        - `0 <= nums.length <= 10^5`
                    """,
                    "examples": [
                        {"input": "nums = [5, 7, 7, 8, 8, 10], target = 8", "output": "[3, 4]", "explanation": ""},
                        {"input": "nums = [5, 7, 7, 8, 8, 10], target = 6", "output": "[-1, -1]", "explanation": ""},
                    ],
                    "approach": """
                        Run two binary searches: one for the first index with `nums[i] >= target` (lower bound)
                        and one for the first index with `nums[i] > target` (upper bound). The answer is
                        `[lower, upper - 1]` if `target` is present.
                    """,
                    "explanation": """
                        A normal binary search stops at *any* match. Searching for boundaries instead always
                        converges to the edge of the run of equal values. Python's `bisect_left` /
                        `bisect_right` implement exactly these two searches.
                    """,
                    "time": "O(log n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def search_range(nums: list[int], target: int) -> list[int]:
                                def first_index_where(predicate) -> int:
                                    lo, hi = 0, len(nums)
                                    while lo < hi:
                                        mid = (lo + hi) // 2
                                        if predicate(nums[mid]):
                                            hi = mid
                                        else:
                                            lo = mid + 1
                                    return lo

                                start = first_index_where(lambda v: v >= target)
                                if start == len(nums) or nums[start] != target:
                                    return [-1, -1]
                                end = first_index_where(lambda v: v > target) - 1
                                return [start, end]
                        """,
                    },
                },
            ],
        },
        # ------------------------------------------------------------ linked lists
        {
            "slug": "linked-lists",
            "name": "Linked Lists",
            "description": "Pointer manipulation without random access.",
            "questions": [
                {
                    "slug": "reverse-linked-list",
                    "title": "Reverse a Linked List",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": ["in-place-reversal"],
                    "statement": """
                        Given the `head` of a singly linked list, reverse the list in place and return the new
                        head.
                    """,
                    "constraints": """
                        - `0 <= number of nodes <= 5000`
                        - `-5000 <= Node.val <= 5000`
                    """,
                    "examples": [
                        {"input": "head = 1 → 2 → 3 → 4", "output": "4 → 3 → 2 → 1", "explanation": ""},
                        {"input": "head = (empty)", "output": "(empty)", "explanation": ""},
                    ],
                    "approach": """
                        Walk the list with `prev` (already-reversed part) and `curr`. For each node: save
                        `curr.next`, point `curr.next` back at `prev`, then advance both pointers.
                    """,
                    "explanation": """
                        Invariant: `prev` is the head of the reversed prefix and `curr` is the head of the
                        untouched suffix. Saving `next` before re-pointing is what keeps the rest of the list
                        reachable. When `curr` becomes `None`, `prev` is the new head.
                    """,
                    "time": "O(n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            class ListNode:
                                def __init__(self, val=0, next=None):
                                    self.val = val
                                    self.next = next

                            def reverse_list(head: ListNode | None) -> ListNode | None:
                                prev, curr = None, head
                                while curr:
                                    nxt = curr.next
                                    curr.next = prev
                                    prev, curr = curr, nxt
                                return prev
                        """,
                    },
                },
                {
                    "slug": "detect-cycle",
                    "title": "Detect a Cycle",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": ["fast-slow-pointers"],
                    "statement": """
                        Given the `head` of a linked list, return `true` if some node can be reached again by
                        repeatedly following `next` (the list has a cycle), otherwise `false`.
                        Aim for O(1) extra memory.
                    """,
                    "constraints": """
                        - `0 <= number of nodes <= 10^4`
                    """,
                    "examples": [
                        {"input": "3 → 2 → 0 → -4 → (back to 2)", "output": "true", "explanation": ""},
                        {"input": "1 → 2 → (end)", "output": "false", "explanation": ""},
                    ],
                    "approach": """
                        Move a `slow` pointer one step and a `fast` pointer two steps at a time (Floyd's
                        tortoise and hare). If `fast` reaches the end there's no cycle; if they ever meet,
                        there is one.
                    """,
                    "explanation": """
                        Inside a cycle the gap between `fast` and `slow` shrinks by one node every step, so
                        `fast` must land exactly on `slow` within one lap. A hash set of visited nodes also
                        works but needs O(n) memory.
                    """,
                    "time": "O(n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def has_cycle(head) -> bool:
                                slow = fast = head
                                while fast and fast.next:
                                    slow = slow.next
                                    fast = fast.next.next
                                    if slow is fast:
                                        return True
                                return False
                        """,
                    },
                },
                {
                    "slug": "merge-two-sorted-lists",
                    "title": "Merge Two Sorted Lists",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": [],
                    "statement": """
                        Given the heads of two sorted linked lists, splice their nodes together into one sorted
                        list and return its head.
                    """,
                    "constraints": """
                        - `0 <= length of each list <= 50`
                        - Both lists are sorted in non-decreasing order.
                    """,
                    "examples": [
                        {"input": "l1 = 1 → 2 → 4, l2 = 1 → 3 → 4", "output": "1 → 1 → 2 → 3 → 4 → 4", "explanation": ""},
                        {"input": "l1 = (empty), l2 = 0", "output": "0", "explanation": ""},
                    ],
                    "approach": """
                        Use a dummy head and a `tail` pointer. Repeatedly attach the smaller of the two current
                        nodes to `tail`, advance that list, and finally attach whatever list is left over.
                    """,
                    "explanation": """
                        The dummy node removes the special case of choosing the first head. No new nodes are
                        created — existing nodes are re-linked — so extra space is O(1). This is the merge step
                        of merge sort.
                    """,
                    "time": "O(n + m)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            class ListNode:
                                def __init__(self, val=0, next=None):
                                    self.val = val
                                    self.next = next

                            def merge_lists(l1: ListNode | None, l2: ListNode | None) -> ListNode | None:
                                dummy = tail = ListNode()
                                while l1 and l2:
                                    if l1.val <= l2.val:
                                        tail.next, l1 = l1, l1.next
                                    else:
                                        tail.next, l2 = l2, l2.next
                                    tail = tail.next
                                tail.next = l1 or l2
                                return dummy.next
                        """,
                    },
                },
                {
                    "slug": "remove-nth-from-end",
                    "title": "Remove the N-th Node From the End",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["fast-slow-pointers"],
                    "statement": """
                        Given the `head` of a linked list, remove the `n`-th node counting from the end and return
                        the head. Do it in a single pass.
                    """,
                    "constraints": """
                        - `1 <= number of nodes <= 30`
                        - `1 <= n <= number of nodes`
                    """,
                    "examples": [
                        {"input": "head = 1 → 2 → 3 → 4 → 5, n = 2", "output": "1 → 2 → 3 → 5", "explanation": ""},
                        {"input": "head = 1, n = 1", "output": "(empty)", "explanation": ""},
                    ],
                    "approach": """
                        Move a `fast` pointer `n` nodes ahead of a `slow` pointer (both starting at a dummy node).
                        Then advance both until `fast` reaches the last node; `slow` now sits just before the node
                        to delete.
                    """,
                    "explanation": """
                        Keeping a fixed gap of `n` nodes means that when `fast` is at the end, `slow` is exactly
                        `n + 1` from the end. The dummy node makes deleting the real head (when `n` equals the
                        length) work without a special case.
                    """,
                    "time": "O(length)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            class ListNode:
                                def __init__(self, val=0, next=None):
                                    self.val = val
                                    self.next = next

                            def remove_nth_from_end(head: ListNode | None, n: int) -> ListNode | None:
                                dummy = ListNode(0, head)
                                fast = slow = dummy
                                for _ in range(n):
                                    fast = fast.next
                                while fast.next:
                                    fast = fast.next
                                    slow = slow.next
                                slow.next = slow.next.next
                                return dummy.next
                        """,
                    },
                },
            ],
        },
        # ---------------------------------------------------------- stack & queue
        {
            "slug": "stack-and-queue",
            "name": "Stack and Queue",
            "description": "LIFO and FIFO structures for matching and ordering problems.",
            "questions": [
                {
                    "slug": "balanced-brackets",
                    "title": "Balanced Brackets",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": ["stack"],
                    "statement": """
                        Given a string `s` containing only the characters `()[]{}`, return `true` if every
                        opening bracket is closed by the same type of bracket in the correct order.
                    """,
                    "constraints": """
                        - `1 <= s.length <= 10^4`
                    """,
                    "examples": [
                        {"input": 's = "{[()]}()"', "output": "true", "explanation": ""},
                        {"input": 's = "([)]"', "output": "false", "explanation": "The ')' closes '[' — wrong type."},
                    ],
                    "approach": """
                        Push opening brackets onto a stack. For a closing bracket, the stack's top must be the
                        matching opener — pop it, or fail. At the end the stack must be empty.
                    """,
                    "explanation": """
                        The most recently opened bracket must close first, which is exactly last-in, first-out.
                        An empty stack at a closing bracket, or leftovers at the end, both mean imbalance.
                    """,
                    "time": "O(n)",
                    "space": "O(n)",
                    "solutions": {
                        "python": """
                            def is_balanced(s: str) -> bool:
                                pairs = {")": "(", "]": "[", "}": "{"}
                                stack = []
                                for ch in s:
                                    if ch in pairs:
                                        if not stack or stack.pop() != pairs[ch]:
                                            return False
                                    else:
                                        stack.append(ch)
                                return not stack
                        """,
                    },
                },
                {
                    "slug": "next-greater-element",
                    "title": "Next Greater Element",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["monotonic-stack"],
                    "statement": """
                        For each element of `nums`, find the first element to its **right** that is strictly
                        greater. Return an array of those values, using `-1` where none exists.
                    """,
                    "constraints": """
                        - `1 <= nums.length <= 10^5`
                    """,
                    "examples": [
                        {"input": "nums = [2, 7, 3, 5, 4, 6, 8]", "output": "[7, 8, 5, 6, 6, 8, -1]", "explanation": ""},
                        {"input": "nums = [5, 4, 3]", "output": "[-1, -1, -1]", "explanation": ""},
                    ],
                    "approach": """
                        Keep a stack of indices whose answer is still unknown; their values are decreasing from
                        bottom to top. When a new value is larger than the top's value, it is that index's
                        next greater element — pop and record, repeatedly.
                    """,
                    "explanation": """
                        Each index is pushed once and popped at most once, so the total work is O(n) even though
                        there is a loop inside the loop. Indices left on the stack at the end have no greater
                        element to their right.
                    """,
                    "time": "O(n)",
                    "space": "O(n)",
                    "solutions": {
                        "python": """
                            def next_greater(nums: list[int]) -> list[int]:
                                result = [-1] * len(nums)
                                stack = []  # indices with decreasing values
                                for i, x in enumerate(nums):
                                    while stack and nums[stack[-1]] < x:
                                        result[stack.pop()] = x
                                    stack.append(i)
                                return result
                        """,
                    },
                },
                {
                    "slug": "min-stack",
                    "title": "Stack With Constant-Time Minimum",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["stack"],
                    "statement": """
                        Design a stack that supports `push(x)`, `pop()`, `top()` and `get_min()` — the smallest
                        element currently in the stack — all in O(1) time.
                    """,
                    "constraints": """
                        - `pop`, `top` and `get_min` are only called on a non-empty stack.
                        - Up to `3 * 10^4` operations.
                    """,
                    "examples": [
                        {
                            "input": "push(-2), push(0), push(-3), get_min(), pop(), top(), get_min()",
                            "output": "-3, 0, -2",
                            "explanation": "After popping -3 the minimum goes back to -2.",
                        },
                    ],
                    "approach": """
                        Store pairs `(value, minimum so far)` on a single stack. When pushing, the new minimum is
                        `min(x, current minimum)`. The top pair always carries the minimum of the whole stack.
                    """,
                    "explanation": """
                        Each entry remembers the minimum of everything at or below it, so popping automatically
                        "restores" the previous minimum — no searching needed. The cost is one extra number per
                        element.
                    """,
                    "time": "O(1) per operation",
                    "space": "O(n)",
                    "solutions": {
                        "python": """
                            class MinStack:
                                def __init__(self):
                                    self._items = []  # (value, min of stack up to here)

                                def push(self, x: int) -> None:
                                    current_min = min(x, self._items[-1][1]) if self._items else x
                                    self._items.append((x, current_min))

                                def pop(self) -> None:
                                    self._items.pop()

                                def top(self) -> int:
                                    return self._items[-1][0]

                                def get_min(self) -> int:
                                    return self._items[-1][1]
                        """,
                    },
                },
                {
                    "slug": "evaluate-postfix",
                    "title": "Evaluate a Postfix Expression",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["stack"],
                    "statement": """
                        Evaluate an arithmetic expression given in **postfix** (Reverse Polish) notation as a list
                        of tokens. Operators are `+`, `-`, `*`, `/`; division truncates toward zero. The expression
                        is always valid.
                    """,
                    "constraints": """
                        - `1 <= tokens.length <= 10^4`
                        - Every intermediate result fits in a 32-bit integer.
                    """,
                    "examples": [
                        {"input": 'tokens = ["2", "1", "+", "3", "*"]', "output": "9", "explanation": "(2 + 1) * 3"},
                        {"input": 'tokens = ["4", "13", "5", "/", "+"]', "output": "6", "explanation": "4 + (13 / 5) = 4 + 2"},
                    ],
                    "approach": """
                        Push numbers onto a stack. On an operator, pop the right operand, then the left operand,
                        apply the operator and push the result. The final stack holds the answer.
                    """,
                    "explanation": """
                        Postfix puts each operator after its operands, so the two most recent values are always
                        the ones it applies to — a stack gives exactly those. Note the operand order for `-` and
                        `/`, and use `int(a / b)` so that negative results truncate toward zero (Python's `//`
                        floors instead).
                    """,
                    "time": "O(n)",
                    "space": "O(n)",
                    "solutions": {
                        "python": """
                            def eval_postfix(tokens: list[str]) -> int:
                                stack = []
                                for tok in tokens:
                                    if tok in {"+", "-", "*", "/"}:
                                        right, left = stack.pop(), stack.pop()
                                        if tok == "+":
                                            stack.append(left + right)
                                        elif tok == "-":
                                            stack.append(left - right)
                                        elif tok == "*":
                                            stack.append(left * right)
                                        else:
                                            stack.append(int(left / right))
                                    else:
                                        stack.append(int(tok))
                                return stack[-1]
                        """,
                    },
                },
            ],
        },
        # --------------------------------------------------------- trees & graphs
        {
            "slug": "trees-and-graphs",
            "name": "Trees and Graphs",
            "description": "Traversals — breadth-first and depth-first — and what they unlock.",
            "questions": [
                {
                    "slug": "level-order-traversal",
                    "title": "Level Order Traversal",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["bfs"],
                    "statement": """
                        Given the `root` of a binary tree, return its node values level by level, from left to
                        right, as a list of lists.
                    """,
                    "constraints": """
                        - `0 <= number of nodes <= 2000`
                    """,
                    "examples": [
                        {"input": "root = [3, 9, 20, null, null, 15, 7]", "output": "[[3], [9, 20], [15, 7]]", "explanation": ""},
                        {"input": "root = []", "output": "[]", "explanation": ""},
                    ],
                    "approach": """
                        Breadth-first search with a queue. At the start of each round, the queue holds exactly
                        one level: record its size, pop that many nodes, and enqueue their children.
                    """,
                    "explanation": """
                        A queue processes nodes in the order they were discovered, so all nodes at depth d are
                        dequeued before any node at depth d + 1. Capturing the queue length before the inner
                        loop separates the levels.
                    """,
                    "time": "O(n)",
                    "space": "O(w) — w is the widest level",
                    "solutions": {
                        "python": """
                            from collections import deque

                            def level_order(root) -> list[list[int]]:
                                if root is None:
                                    return []
                                levels, queue = [], deque([root])
                                while queue:
                                    level = []
                                    for _ in range(len(queue)):
                                        node = queue.popleft()
                                        level.append(node.val)
                                        if node.left:
                                            queue.append(node.left)
                                        if node.right:
                                            queue.append(node.right)
                                    levels.append(level)
                                return levels
                        """,
                    },
                },
                {
                    "slug": "count-islands",
                    "title": "Count the Islands",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["dfs", "bfs"],
                    "statement": """
                        A grid contains `'1'` (land) and `'0'` (water). An island is a group of land cells
                        connected horizontally or vertically. Return the number of islands.
                    """,
                    "constraints": """
                        - `1 <= rows, cols <= 300`
                    """,
                    "examples": [
                        {"input": 'grid = [["1","1","0","0"], ["1","0","0","1"], ["0","0","1","1"]]', "output": "2", "explanation": "One island top-left, one bottom-right."},
                    ],
                    "approach": """
                        Scan every cell. When you find unvisited land, that's a new island: increment the count
                        and flood-fill (DFS or BFS) to mark every connected land cell as visited.
                    """,
                    "explanation": """
                        Each flood fill consumes exactly one connected component, so the number of fills equals
                        the number of islands. Every cell is visited a constant number of times. An explicit
                        stack avoids Python's recursion limit on large grids.
                    """,
                    "time": "O(rows · cols)",
                    "space": "O(rows · cols) worst case for the stack",
                    "solutions": {
                        "python": """
                            def count_islands(grid: list[list[str]]) -> int:
                                rows, cols = len(grid), len(grid[0])
                                seen = set()
                                islands = 0
                                for r in range(rows):
                                    for c in range(cols):
                                        if grid[r][c] != "1" or (r, c) in seen:
                                            continue
                                        islands += 1
                                        stack = [(r, c)]
                                        seen.add((r, c))
                                        while stack:
                                            y, x = stack.pop()
                                            for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                                                if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == "1" and (ny, nx) not in seen:
                                                    seen.add((ny, nx))
                                                    stack.append((ny, nx))
                                return islands
                        """,
                    },
                },
                {
                    "slug": "maximum-tree-depth",
                    "title": "Maximum Depth of a Binary Tree",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": ["dfs"],
                    "statement": """
                        Given the `root` of a binary tree, return its maximum depth: the number of nodes on the
                        longest path from the root down to a leaf.
                    """,
                    "constraints": """
                        - `0 <= number of nodes <= 10^4`
                    """,
                    "examples": [
                        {"input": "root = [3, 9, 20, null, null, 15, 7]", "output": "3", "explanation": ""},
                        {"input": "root = []", "output": "0", "explanation": ""},
                    ],
                    "approach": """
                        Depth of a tree = 1 + the larger of its two subtrees' depths, and an empty tree has depth
                        0. That recursive definition is the whole solution.
                    """,
                    "explanation": """
                        Every node is visited once (post-order DFS). The recursion depth equals the tree's height,
                        so a very skewed tree can hit Python's recursion limit — an iterative BFS counting levels
                        avoids that.
                    """,
                    "time": "O(n)",
                    "space": "O(h) — h is the tree height",
                    "solutions": {
                        "python": """
                            def max_depth(root) -> int:
                                if root is None:
                                    return 0
                                return 1 + max(max_depth(root.left), max_depth(root.right))
                        """,
                    },
                },
                {
                    "slug": "course-order-possible",
                    "title": "Can All Courses Be Finished?",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["bfs"],
                    "statement": """
                        There are `n` courses labelled `0 … n-1`. `prerequisites[i] = [a, b]` means you must take
                        course `b` before course `a`. Return `true` if it's possible to finish every course.
                    """,
                    "constraints": """
                        - `1 <= n <= 2000`
                        - `0 <= prerequisites.length <= 5000`
                        - All pairs are distinct.
                    """,
                    "examples": [
                        {"input": "n = 2, prerequisites = [[1, 0]]", "output": "true", "explanation": "Take 0, then 1."},
                        {"input": "n = 2, prerequisites = [[1, 0], [0, 1]]", "output": "false", "explanation": "Each needs the other — a cycle."},
                    ],
                    "approach": """
                        Model courses as a directed graph and run **Kahn's algorithm** (topological sort): start
                        with every course that has no prerequisites, "take" it, and decrement the in-degree of the
                        courses that depend on it. If you manage to take all `n` courses, there is no cycle.
                    """,
                    "explanation": """
                        A course can be taken only when all its prerequisites are done, i.e. its in-degree reaches
                        0. Courses on a cycle never reach in-degree 0, so they are never taken; counting taken
                        courses therefore detects cycles. Each node and edge is processed once.
                    """,
                    "time": "O(n + e)",
                    "space": "O(n + e)",
                    "solutions": {
                        "python": """
                            from collections import deque

                            def can_finish(n: int, prerequisites: list[list[int]]) -> bool:
                                graph = [[] for _ in range(n)]
                                indegree = [0] * n
                                for course, pre in prerequisites:
                                    graph[pre].append(course)
                                    indegree[course] += 1

                                queue = deque(c for c in range(n) if indegree[c] == 0)
                                taken = 0
                                while queue:
                                    course = queue.popleft()
                                    taken += 1
                                    for nxt in graph[course]:
                                        indegree[nxt] -= 1
                                        if indegree[nxt] == 0:
                                            queue.append(nxt)
                                return taken == n
                        """,
                    },
                },
            ],
        },
        # ---------------------------------------------------- dynamic programming
        {
            "slug": "dynamic-programming",
            "name": "Dynamic Programming",
            "description": "Overlapping subproblems, solved once and reused.",
            "questions": [
                {
                    "slug": "ways-to-climb-stairs",
                    "title": "Ways to Climb Stairs",
                    "type": "coding",
                    "difficulty": "easy",
                    "patterns": ["dynamic-programming"],
                    "statement": """
                        A staircase has `n` steps. Each move climbs either 1 or 2 steps. In how many distinct
                        ways can you reach the top?
                    """,
                    "constraints": """
                        - `1 <= n <= 45`
                    """,
                    "examples": [
                        {"input": "n = 3", "output": "3", "explanation": "1+1+1, 1+2, 2+1."},
                        {"input": "n = 5", "output": "8", "explanation": ""},
                    ],
                    "approach": """
                        The last move onto step `n` came from step `n - 1` or step `n - 2`, so
                        `ways(n) = ways(n - 1) + ways(n - 2)`. Only the previous two values are needed.
                    """,
                    "explanation": """
                        Naive recursion recomputes the same subproblems exponentially many times. Building
                        bottom-up computes each `ways(i)` once. The recurrence is the Fibonacci sequence
                        shifted by one.
                    """,
                    "time": "O(n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def climb_stairs(n: int) -> int:
                                one_back, two_back = 1, 1  # ways(1), ways(0)
                                for _ in range(2, n + 1):
                                    one_back, two_back = one_back + two_back, one_back
                                return one_back
                        """,
                    },
                },
                {
                    "slug": "fewest-coins",
                    "title": "Fewest Coins for an Amount",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["dynamic-programming"],
                    "statement": """
                        Given coin denominations `coins` (unlimited supply of each) and an `amount`, return the
                        fewest coins needed to make exactly that amount, or `-1` if it can't be made.
                    """,
                    "constraints": """
                        - `1 <= coins.length <= 12`
                        - `1 <= coins[i] <= 2^31 - 1`
                        - `0 <= amount <= 10^4`
                    """,
                    "examples": [
                        {"input": "coins = [1, 2, 5], amount = 11", "output": "3", "explanation": "5 + 5 + 1."},
                        {"input": "coins = [2], amount = 3", "output": "-1", "explanation": ""},
                        {"input": "coins = [1, 3, 4], amount = 6", "output": "2", "explanation": "3 + 3. Greedy (4 + 1 + 1) gives 3 — greedy fails here."},
                    ],
                    "approach": """
                        Let `best[a]` be the fewest coins for amount `a`, with `best[0] = 0`. For every amount
                        from 1 up, try ending with each coin `c <= a`: `best[a] = min(best[a - c] + 1)`.
                    """,
                    "explanation": """
                        Any optimal way to make `a` ends with some coin `c`, and the rest must be an optimal
                        way to make `a - c` (optimal substructure). Filling the table in increasing order
                        guarantees `best[a - c]` is final before it's used. Unreachable amounts stay infinite.
                    """,
                    "time": "O(amount · coins)",
                    "space": "O(amount)",
                    "solutions": {
                        "python": """
                            def fewest_coins(coins: list[int], amount: int) -> int:
                                INF = amount + 1
                                best = [0] + [INF] * amount
                                for a in range(1, amount + 1):
                                    for c in coins:
                                        if c <= a and best[a - c] + 1 < best[a]:
                                            best[a] = best[a - c] + 1
                                return best[amount] if best[amount] != INF else -1
                        """,
                    },
                },
                {
                    "slug": "street-robber",
                    "title": "Maximum Loot Without Adjacent Houses",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["dynamic-programming"],
                    "statement": """
                        Houses along a street hold `amounts[i]` of money. Robbing two **adjacent** houses triggers
                        an alarm. Return the maximum amount you can collect without robbing adjacent houses.
                    """,
                    "constraints": """
                        - `1 <= amounts.length <= 100`
                        - `0 <= amounts[i] <= 400`
                    """,
                    "examples": [
                        {"input": "amounts = [2, 7, 9, 3, 1]", "output": "12", "explanation": "2 + 9 + 1"},
                        {"input": "amounts = [5, 1, 1, 5]", "output": "10", "explanation": "5 + 5 (first and last)"},
                    ],
                    "approach": """
                        At each house choose: skip it (keep the best so far) or rob it (its amount + the best up to
                        two houses back). `best[i] = max(best[i-1], best[i-2] + amounts[i])`.
                    """,
                    "explanation": """
                        The best plan for the first `i` houses either uses house `i` or it doesn't — those two
                        cases cover everything, and each reuses an already-solved smaller prefix. Greedily picking
                        the largest houses fails (e.g. `[5, 1, 1, 5]` vs picking alternate houses).
                    """,
                    "time": "O(n)",
                    "space": "O(1)",
                    "solutions": {
                        "python": """
                            def max_loot(amounts: list[int]) -> int:
                                prev2 = prev1 = 0  # best up to two houses back, best up to previous house
                                for amount in amounts:
                                    prev2, prev1 = prev1, max(prev1, prev2 + amount)
                                return prev1
                        """,
                    },
                },
                {
                    "slug": "longest-common-subsequence",
                    "title": "Longest Common Subsequence",
                    "type": "coding",
                    "difficulty": "medium",
                    "patterns": ["dynamic-programming"],
                    "statement": """
                        Given strings `a` and `b`, return the length of their longest common subsequence — the
                        longest sequence of characters appearing in both in the same order, not necessarily
                        contiguously.
                    """,
                    "constraints": """
                        - `1 <= a.length, b.length <= 1000`
                        - Lowercase English letters.
                    """,
                    "examples": [
                        {"input": 'a = "abcde", b = "ace"', "output": "3", "explanation": '"ace"'},
                        {"input": 'a = "abc", b = "def"', "output": "0", "explanation": ""},
                    ],
                    "approach": """
                        Let `dp[i][j]` be the LCS length of `a[:i]` and `b[:j]`. If `a[i-1] == b[j-1]` the
                        characters extend a common subsequence: `dp[i-1][j-1] + 1`. Otherwise drop one character:
                        `max(dp[i-1][j], dp[i][j-1])`.
                    """,
                    "explanation": """
                        Every pair of prefixes is solved once in an `(n+1) × (m+1)` table, giving O(n·m). Only
                        the previous row is ever read, so the table can shrink to two rows — O(m) memory.
                    """,
                    "time": "O(n · m)",
                    "space": "O(m)",
                    "solutions": {
                        "python": """
                            def lcs_length(a: str, b: str) -> int:
                                prev = [0] * (len(b) + 1)
                                for ch_a in a:
                                    curr = [0] * (len(b) + 1)
                                    for j, ch_b in enumerate(b, start=1):
                                        if ch_a == ch_b:
                                            curr[j] = prev[j - 1] + 1
                                        else:
                                            curr[j] = max(prev[j], curr[j - 1])
                                    prev = curr
                                return prev[-1]
                        """,
                    },
                },
            ],
        },
    ],
}
