from . import P

TOPIC = "sliding-window"

PROBLEMS = [
    P(
        "windows-meeting-average", "Windows Meeting an Average", "easy", ["sliding-window"],
        statement="Count the subarrays of length exactly `k` in `arr` whose average is **at least** `threshold`.",
        inputs="- `arr`: a list of positive integers\n- `k`: window length\n- `threshold`: the minimum average",
        output="The number of qualifying windows.",
        constraints="- `1 <= k <= arr.length <= 10^5`\n- `1 <= arr[i] <= 10^4`",
        examples=[
            ({"arr": [2, 2, 2, 2, 5, 5, 5, 8], "k": 3, "threshold": 4}, 3, "[2, 5, 5], [5, 5, 5] and [5, 5, 8]."),
            ({"arr": [11, 13, 17, 23, 29, 31, 7, 5, 2, 3], "k": 3, "threshold": 5}, 6, ""),
        ],
        approach="Average ≥ threshold is the same as sum ≥ `k × threshold`. Keep the sum of the current window: add the element entering on the right, subtract the one leaving on the left.",
        explanation="Each window's sum is updated in O(1) from the previous one, and comparing sums avoids division and floating-point issues.",
        time="O(n)", space="O(1)",
        code="""
        def count_windows(arr: list[int], k: int, threshold: int) -> int:
            need = k * threshold
            window = sum(arr[:k])
            count = int(window >= need)
            for i in range(k, len(arr)):
                window += arr[i] - arr[i - k]
                count += window >= need
            return count
        """,
    ),
    P(
        "most-vowels-in-window", "Most Vowels in a Window", "easy", ["sliding-window"],
        statement="Return the maximum number of vowels (`a e i o u`) in any substring of `s` of length `k`.",
        inputs="- `s`: a lowercase string\n- `k`: the window length",
        output="The largest vowel count of any length-`k` substring.",
        constraints="- `1 <= k <= s.length <= 10^5`",
        examples=[
            ({"s": "abciiidef", "k": 3}, 3, "'iii' has three vowels."),
            ({"s": "aeiou", "k": 2}, 2, ""),
        ],
        tests=[({"s": "rhythms", "k": 4}, 0)],
        approach="Count vowels in the first window, then slide: add one if the entering character is a vowel, subtract one if the leaving character is.",
        explanation="The window count changes by at most one per step, so every window is evaluated in constant time.",
        time="O(n)", space="O(1)",
        code="""
        def max_vowels(s: str, k: int) -> int:
            vowels = set("aeiou")
            count = sum(ch in vowels for ch in s[:k])
            best = count
            for i in range(k, len(s)):
                count += (s[i] in vowels) - (s[i - k] in vowels)
                best = max(best, count)
            return best
        """,
    ),
    P(
        "nearby-duplicate", "Duplicate Within Distance k", "easy", ["sliding-window", "hash-map"],
        statement="Return `true` if there are two indices `i != j` with `nums[i] == nums[j]` and `|i - j| <= k`.",
        inputs="- `nums`: a list of integers\n- `k`: the maximum index distance",
        output="`true` or `false`.",
        constraints="- `1 <= nums.length <= 10^5`\n- `0 <= k <= 10^5`",
        examples=[
            ({"nums": [1, 2, 3, 1], "k": 3}, True, "The two 1s are 3 apart."),
            ({"nums": [1, 2, 3, 1, 2, 3], "k": 2}, False, "Equal values are always 3 apart."),
        ],
        approach="Keep a set of the last `k` values. Before adding `nums[i]`, check whether it is already in the set; then add it and drop `nums[i − k]` once the window is too long.",
        explanation="The set always holds exactly the values within distance k behind the current index, so a hit means a close duplicate.",
        time="O(n)", space="O(k)",
        code="""
        def contains_nearby_duplicate(nums: list[int], k: int) -> bool:
            window = set()
            for i, x in enumerate(nums):
                if x in window:
                    return True
                window.add(x)
                if len(window) > k:
                    window.remove(nums[i - k])
            return False
        """,
    ),
    P(
        "closest-k-scores", "Closest Group of k Scores", "easy", ["sliding-window", "sorting"],
        statement="Pick any `k` scores from `nums` so that the difference between the highest and lowest picked score is as small as possible. Return that difference.",
        inputs="- `nums`: a list of scores\n- `k`: how many to pick",
        output="The minimum possible (max − min) over all groups of `k`.",
        constraints="- `1 <= k <= nums.length <= 1000`",
        examples=[
            ({"nums": [9, 4, 1, 7], "k": 2}, 2, "Pick 9 and 7."),
            ({"nums": [90], "k": 1}, 0, ""),
        ],
        approach="Sort the scores. The best group is always `k` consecutive scores in sorted order; slide a window of length `k` and take the smallest `nums[i + k − 1] − nums[i]`.",
        explanation="If a group skips a score lying between its min and max, swapping that score in can't increase the spread — so only contiguous sorted windows need checking.",
        time="O(n log n)", space="O(1) besides sorting",
        code="""
        def minimum_difference(nums: list[int], k: int) -> int:
            nums = sorted(nums)
            return min(nums[i + k - 1] - nums[i] for i in range(len(nums) - k + 1))
        """,
    ),
    P(
        "longest-repeat-after-replacements", "Longest Repeat After k Replacements", "medium", ["sliding-window", "hash-map"],
        statement="You may change at most `k` characters of the uppercase string `s` to any other uppercase letter. Return the length of the longest substring containing a single repeated letter you can obtain.",
        inputs="- `s`: an uppercase string\n- `k`: the number of replacements allowed",
        output="The length of the longest achievable block of one letter.",
        constraints="- `1 <= s.length <= 10^5`\n- `0 <= k <= s.length`",
        examples=[
            ({"s": "ABAB", "k": 2}, 4, "Replace both As (or both Bs)."),
            ({"s": "AABABBA", "k": 1}, 4, "Change the middle A to get BBBB."),
        ],
        approach="Grow a window to the right while counting letters in it. A window is fixable if `length − (count of its most frequent letter) <= k`. When it isn't, move the left edge one step.",
        explanation="The window never shrinks below the best length found, so it only needs to slide (not shrink repeatedly). Keeping the historical maximum frequency is safe: a smaller value could never produce a longer answer.",
        time="O(n)", space="O(26)",
        code="""
        from collections import Counter

        def character_replacement(s: str, k: int) -> int:
            counts = Counter()
            left = top = best = 0
            for right, ch in enumerate(s):
                counts[ch] += 1
                top = max(top, counts[ch])
                if right - left + 1 - top > k:
                    counts[s[left]] -= 1
                    left += 1
                best = max(best, right - left + 1)
            return best
        """,
    ),
    P(
        "contains-a-permutation", "Contains a Permutation", "medium", ["sliding-window", "hash-map"],
        statement="Return `true` if `s2` contains a permutation of `s1` as a substring — i.e. some window of `s2` uses exactly the letters of `s1`.",
        inputs="- `s1`: a lowercase string\n- `s2`: a lowercase string",
        output="`true` or `false`.",
        constraints="- `1 <= s1.length, s2.length <= 10^4`",
        examples=[
            ({"s1": "ab", "s2": "eidbaooo"}, True, "'ba' is a permutation of 'ab'."),
            ({"s1": "ab", "s2": "eidboaoo"}, False, ""),
        ],
        approach="Slide a window of length `len(s1)` over `s2` while keeping letter counts for the window. Compare the window's counts with `s1`'s counts after each step.",
        explanation="A permutation has the same letter counts. Updating the counts as the window slides costs O(1) per step; comparing two 26-letter tables is constant time.",
        time="O(n)", space="O(26)",
        code="""
        def check_inclusion(s1: str, s2: str) -> bool:
            if len(s1) > len(s2):
                return False
            need, have = [0] * 26, [0] * 26
            for ch in s1:
                need[ord(ch) - 97] += 1
            for i, ch in enumerate(s2):
                have[ord(ch) - 97] += 1
                if i >= len(s1):
                    have[ord(s2[i - len(s1)]) - 97] -= 1
                if have == need:
                    return True
            return False
        """,
    ),
    P(
        "anagram-start-positions", "Where Do the Anagrams Start?", "medium", ["sliding-window", "hash-map"],
        statement="Return all start indices of substrings of `s` that are anagrams of `p`, in increasing order.",
        inputs="- `s`: a lowercase string\n- `p`: a lowercase string",
        output="A list of start indices.",
        constraints="- `1 <= s.length, p.length <= 3 × 10^4`",
        examples=[
            ({"s": "cbaebabacd", "p": "abc"}, [0, 6], "'cba' at 0 and 'bac' at 6."),
            ({"s": "abab", "p": "ab"}, [0, 1, 2], "Overlapping windows count."),
        ],
        approach="Same sliding window as the permutation check, but record every start index where the window's letter counts equal `p`'s.",
        explanation="Each window differs from the previous one by one character in and one out, so counts are maintained in O(1) per step.",
        time="O(n)", space="O(26)",
        code="""
        def find_anagrams(s: str, p: str) -> list[int]:
            need, have, out = [0] * 26, [0] * 26, []
            for ch in p:
                need[ord(ch) - 97] += 1
            for i, ch in enumerate(s):
                have[ord(ch) - 97] += 1
                if i >= len(p):
                    have[ord(s[i - len(p)]) - 97] -= 1
                if i >= len(p) - 1 and have == need:
                    out.append(i - len(p) + 1)
            return out
        """,
    ),
    P(
        "longest-ones-with-flips", "Longest Ones With k Flips", "medium", ["sliding-window"],
        statement="Given a binary array `nums` and an integer `k`, return the length of the longest run of 1s you can make by flipping at most `k` zeros to ones.",
        inputs="- `nums`: a list of 0s and 1s\n- `k`: the number of flips allowed",
        output="The maximum run length.",
        constraints="- `1 <= nums.length <= 10^5`\n- `0 <= k <= nums.length`",
        examples=[
            ({"nums": [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], "k": 2}, 6, "Flip the zeros at positions 5 and 10."),
            ({"nums": [0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1], "k": 3}, 10, ""),
        ],
        approach="Find the longest window containing at most `k` zeros. Extend the right edge; while the window holds more than `k` zeros, move the left edge forward.",
        explanation="Any window with ≤ k zeros can be turned into all 1s. Both edges only move forward, so the total work is linear.",
        time="O(n)", space="O(1)",
        code="""
        def longest_ones(nums: list[int], k: int) -> int:
            left = zeros = best = 0
            for right, x in enumerate(nums):
                zeros += x == 0
                while zeros > k:
                    zeros -= nums[left] == 0
                    left += 1
                best = max(best, right - left + 1)
            return best
        """,
    ),
    P(
        "two-fruit-baskets", "Two Baskets of Fruit", "medium", ["sliding-window", "hash-map"],
        statement="Trees stand in a row; `fruits[i]` is the type of fruit on tree `i`. You have two baskets, each holding one type (unlimited amount). Starting at any tree, pick one fruit from every tree moving right, and stop when a fruit fits neither basket. Return the most fruit you can pick.",
        inputs="- `fruits`: a list of fruit types (integers)",
        output="The maximum number of fruits collected.",
        constraints="- `1 <= fruits.length <= 10^5`",
        examples=[
            ({"fruits": [1, 2, 1]}, 3, "All three trees."),
            ({"fruits": [1, 2, 3, 2, 2]}, 4, "Start at the second tree: 2, 3, 2, 2."),
        ],
        tests=[({"fruits": [0, 1, 2, 2]}, 3)],
        approach="This is the longest subarray with at most two distinct values. Keep counts of the types in the window; when a third type appears, shrink from the left until only two remain.",
        explanation="The constraint \"at most two distinct values\" only gets easier as the window shrinks, which is exactly what makes the two-pointer window valid.",
        time="O(n)", space="O(1) (at most three keys)",
        code="""
        from collections import defaultdict

        def total_fruit(fruits: list[int]) -> int:
            counts = defaultdict(int)
            left = best = 0
            for right, f in enumerate(fruits):
                counts[f] += 1
                while len(counts) > 2:
                    counts[fruits[left]] -= 1
                    if counts[fruits[left]] == 0:
                        del counts[fruits[left]]
                    left += 1
                best = max(best, right - left + 1)
            return best
        """,
    ),
    P(
        "products-below-k", "Subarrays With Product Below k", "medium", ["sliding-window"],
        statement="Count the contiguous subarrays of `nums` (positive integers) whose product is **strictly less than** `k`.",
        inputs="- `nums`: a list of positive integers\n- `k`: the bound",
        output="The number of qualifying subarrays.",
        constraints="- `1 <= nums.length <= 3 × 10^4`\n- `1 <= nums[i] <= 1000`\n- `0 <= k <= 10^6`",
        examples=[
            ({"nums": [10, 5, 2, 6], "k": 100}, 8, "[10], [5], [2], [6], [10, 5], [5, 2], [2, 6], [5, 2, 6]."),
            ({"nums": [1, 2, 3], "k": 0}, 0, "No product is below 0."),
        ],
        approach="Keep the product of the window `nums[left … right]`. After adding `nums[right]`, divide out elements from the left until the product is below `k`. Every window ending at `right` and starting at or after `left` qualifies: that's `right − left + 1` subarrays.",
        explanation="All values are positive, so shrinking always lowers the product. Counting by right end ensures every subarray is counted exactly once.",
        time="O(n)", space="O(1)",
        code="""
        def num_subarrays_below(nums: list[int], k: int) -> int:
            if k <= 1:
                return 0
            product, left, count = 1, 0, 0
            for right, x in enumerate(nums):
                product *= x
                while product >= k:
                    product //= nums[left]
                    left += 1
                count += right - left + 1
            return count
        """,
    ),
    P(
        "window-maximums", "Maximum of Every Window", "hard", ["sliding-window"],
        statement="A window of size `k` slides over `nums` from left to right, one step at a time. Return the maximum of each window.",
        inputs="- `nums`: a list of integers\n- `k`: the window size",
        output="A list of `n − k + 1` window maximums.",
        constraints="- `1 <= k <= nums.length <= 10^5`\n- `-10^4 <= nums[i] <= 10^4`",
        examples=[
            ({"nums": [1, 3, -1, -3, 5, 3, 6, 7], "k": 3}, [3, 3, 5, 5, 6, 7], ""),
            ({"nums": [1], "k": 1}, [1], ""),
        ],
        tests=[({"nums": [9, 8, 7, 6], "k": 2}, [9, 8, 7])],
        approach="Keep a deque of indices whose values are decreasing. For each new element, pop smaller values from the back (they can never be a maximum again), push the index, drop the front if it left the window, and read the maximum at the front.",
        explanation="Every index enters and leaves the deque once, so the whole scan is linear — much better than O(n·k) for recomputing each window.",
        time="O(n)", space="O(k)",
        code="""
        from collections import deque

        def max_sliding_window(nums: list[int], k: int) -> list[int]:
            dq, out = deque(), []
            for i, x in enumerate(nums):
                while dq and nums[dq[-1]] <= x:
                    dq.pop()
                dq.append(i)
                if dq[0] <= i - k:
                    dq.popleft()
                if i >= k - 1:
                    out.append(nums[dq[0]])
            return out
        """,
    ),
]
