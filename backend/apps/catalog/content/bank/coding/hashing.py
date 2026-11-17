from . import P

TOPIC = "hashing"

BOARD = [
    ["5", "3", ".", ".", "7", ".", ".", ".", "."],
    ["6", ".", ".", "1", "9", "5", ".", ".", "."],
    [".", "9", "8", ".", ".", ".", ".", "6", "."],
    ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
    ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
    ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
    [".", "6", ".", ".", ".", ".", "2", "8", "."],
    [".", ".", ".", "4", "1", "9", ".", ".", "5"],
    [".", ".", ".", ".", "8", ".", ".", "7", "9"],
]
BAD_BOARD = [["8"] + BOARD[0][1:]] + BOARD[1:]

PROBLEMS = [
    P(
        "any-duplicates", "Any Duplicates?", "easy", ["hash-map"],
        statement="Return `true` if any value appears at least twice in `nums`, and `false` if every element is distinct.",
        inputs="- `nums`: a list of integers",
        output="`true` or `false`.",
        constraints="- `1 <= nums.length <= 10^5`",
        examples=[
            ({"nums": [1, 2, 3, 1]}, True, ""),
            ({"nums": [1, 2, 3, 4]}, False, ""),
        ],
        approach="Add elements to a set; if an element is already in the set, you found a duplicate.",
        explanation="Set membership is O(1) on average, so one pass suffices — versus O(n²) for comparing all pairs or O(n log n) for sorting.",
        time="O(n)", space="O(n)",
        code="""
        def contains_duplicate(nums: list[int]) -> bool:
            seen = set()
            for x in nums:
                if x in seen:
                    return True
                seen.add(x)
            return False
        """,
    ),
    P(
        "letters-from-magazine", "Letters From a Magazine", "easy", ["hash-map"],
        statement="Return `true` if `note` can be written using letters cut out of `magazine` (each magazine letter can be used once).",
        inputs="- `note`: a lowercase string\n- `magazine`: a lowercase string",
        output="`true` or `false`.",
        constraints="- `1 <= note.length, magazine.length <= 10^5`",
        examples=[
            ({"note": "aa", "magazine": "ab"}, False, "Only one 'a' is available."),
            ({"note": "aa", "magazine": "aab"}, True, ""),
        ],
        approach="Count the magazine's letters, then for each letter of the note decrement its count; if a count would go negative, the note can't be written.",
        explanation="Only letter counts matter, not positions, so a frequency table answers the question in linear time.",
        time="O(m + n)", space="O(26)",
        code="""
        from collections import Counter

        def can_construct(note: str, magazine: str) -> bool:
            available = Counter(magazine)
            for ch in note:
                if available[ch] == 0:
                    return False
                available[ch] -= 1
            return True
        """,
    ),
    P(
        "common-values", "Values in Both Arrays", "easy", ["hash-map"],
        statement="Return the distinct values that appear in **both** `a` and `b`, in any order.",
        inputs="- `a`, `b`: lists of integers",
        output="A list of the common values, each once.",
        constraints="- `1 <= a.length, b.length <= 1000`",
        examples=[
            ({"a": [1, 2, 2, 1], "b": [2, 2]}, [2], ""),
            ({"a": [4, 9, 5], "b": [9, 4, 9, 8, 4]}, [4, 9], "[9, 4] is also accepted."),
        ],
        compare="unordered",
        approach="Put `a` into a set, then collect values of `b` found in that set (into another set, so each appears once).",
        explanation="Set lookups replace the nested loop of comparing every pair.",
        time="O(m + n)", space="O(m)",
        code="""
        def intersection(a: list[int], b: list[int]) -> list[int]:
            first = set(a)
            return list({x for x in b if x in first})
        """,
    ),
    P(
        "same-letter-pattern", "Same Letter Pattern", "easy", ["hash-map"],
        statement="Two strings are **isomorphic** if the letters of `s` can be replaced to get `t`, where each letter maps to exactly one letter and no two letters map to the same one. Return `true` if `s` and `t` are isomorphic.",
        inputs="- `s`, `t`: strings of equal length",
        output="`true` or `false`.",
        constraints="- `1 <= s.length <= 5 × 10^4`",
        examples=[
            ({"s": "egg", "t": "add"}, True, "e → a, g → d."),
            ({"s": "foo", "t": "bar"}, False, "o would need to map to both a and r."),
        ],
        tests=[({"s": "paper", "t": "title"}, True), ({"s": "badc", "t": "baba"}, False)],
        approach="Keep two maps, `s → t` and `t → s`. For each pair of characters, check both maps agree (or record the pair if new).",
        explanation="One map alone catches a letter mapping to two letters; the reverse map catches two letters mapping to the same one (the `badc`/`baba` case).",
        time="O(n)", space="O(alphabet)",
        code="""
        def is_isomorphic(s: str, t: str) -> bool:
            forward, backward = {}, {}
            for a, b in zip(s, t):
                if forward.setdefault(a, b) != b or backward.setdefault(b, a) != a:
                    return False
            return True
        """,
    ),
    P(
        "words-follow-pattern", "Do the Words Follow the Pattern?", "easy", ["hash-map"],
        statement="Return `true` if the space-separated words in `s` follow `pattern`: each pattern letter corresponds to exactly one word and each word to exactly one letter.",
        inputs="- `pattern`: a string of lowercase letters\n- `s`: words separated by single spaces",
        output="`true` or `false`.",
        constraints="- `1 <= pattern.length <= 300`\n- `1 <= s.length <= 3000`",
        examples=[
            ({"pattern": "abba", "s": "dog cat cat dog"}, True, ""),
            ({"pattern": "abba", "s": "dog cat cat fish"}, False, ""),
        ],
        tests=[({"pattern": "aaaa", "s": "dog cat cat dog"}, False), ({"pattern": "ab", "s": "dog dog"}, False), ({"pattern": "a", "s": "dog cat"}, False)],
        approach="Split `s` into words; the counts must match. Then use the same two-map check as for isomorphic strings, with letters on one side and words on the other.",
        explanation="A bijection needs both directions to be consistent; checking lengths first handles patterns and sentences of different lengths.",
        time="O(n)", space="O(n)",
        code="""
        def word_pattern(pattern: str, s: str) -> bool:
            words = s.split()
            if len(words) != len(pattern):
                return False
            to_word, to_letter = {}, {}
            for letter, word in zip(pattern, words):
                if to_word.setdefault(letter, word) != word or to_letter.setdefault(word, letter) != letter:
                    return False
            return True
        """,
    ),
    P(
        "happy-number", "Is It a Happy Number?", "easy", ["hash-map"],
        statement="Repeatedly replace a positive integer `n` by the sum of the squares of its digits. `n` is **happy** if this reaches 1; otherwise it loops forever. Return `true` if `n` is happy.",
        inputs="- `n`: a positive integer",
        output="`true` or `false`.",
        constraints="- `1 <= n <= 2^31 - 1`",
        examples=[
            ({"n": 19}, True, "1² + 9² = 82 → 68 → 100 → 1."),
            ({"n": 2}, False, "2 → 4 → 16 → 37 → … → 4 (a cycle)."),
        ],
        approach="Follow the sequence while remembering every number seen in a set. Reaching 1 means happy; seeing a number again means a cycle.",
        explanation="The values quickly drop below a few hundred, so the sequence must eventually repeat; the set detects that. (Fast/slow pointers detect the cycle with O(1) memory.)",
        time="O(log n) per step, few steps", space="O(steps)",
        code="""
        def is_happy(n: int) -> bool:
            seen = set()
            while n != 1 and n not in seen:
                seen.add(n)
                n = sum(int(d) ** 2 for d in str(n))
            return n == 1
        """,
    ),
    P(
        "top-k-frequent", "The k Most Frequent Values", "medium", ["hash-map"],
        statement="Return the `k` most frequent values in `nums`, in any order. The answer is unique.",
        inputs="- `nums`: a list of integers\n- `k`: how many values to return",
        output="A list of `k` values.",
        constraints="- `1 <= nums.length <= 10^5`\n- `1 <= k <= number of distinct values`",
        examples=[
            ({"nums": [1, 1, 1, 2, 2, 3], "k": 2}, [1, 2], ""),
            ({"nums": [1], "k": 1}, [1], ""),
        ],
        compare="unordered",
        approach="Count frequencies with a hash map, then bucket the values by frequency (index = count). Walk the buckets from the highest count down until `k` values are collected.",
        explanation="Frequencies are at most n, so bucket sort replaces a comparison sort and gives linear time. A size-k heap (O(n log k)) is a good alternative.",
        time="O(n)", space="O(n)",
        code="""
        from collections import Counter

        def top_k_frequent(nums: list[int], k: int) -> list[int]:
            buckets = [[] for _ in range(len(nums) + 1)]
            for value, count in Counter(nums).items():
                buckets[count].append(value)
            result = []
            for count in range(len(buckets) - 1, 0, -1):
                for value in buckets[count]:
                    result.append(value)
                    if len(result) == k:
                        return result
            return result
        """,
    ),
    P(
        "longest-consecutive-run", "Longest Run of Consecutive Values", "medium", ["hash-map"],
        statement="Return the length of the longest sequence of consecutive integers (like 4, 5, 6, 7) whose values all appear in `nums`, in O(n) time. The values can be anywhere in the array.",
        inputs="- `nums`: an unsorted list of integers (possibly empty)",
        output="The length of the longest consecutive run.",
        constraints="- `0 <= nums.length <= 10^5`",
        examples=[
            ({"nums": [100, 4, 200, 1, 3, 2]}, 4, "1, 2, 3, 4."),
            ({"nums": [0, 3, 7, 2, 5, 8, 4, 6, 0, 1]}, 9, "0 through 8."),
        ],
        tests=[({"nums": []}, 0)],
        approach="Put all values in a set. Only start counting from values that begin a run (`x − 1` is not in the set), then extend `x + 1, x + 2, …` while present.",
        explanation="Each run is walked once, from its start, so the total work over all runs is O(n) despite the inner loop.",
        time="O(n)", space="O(n)",
        code="""
        def longest_consecutive(nums: list[int]) -> int:
            values, best = set(nums), 0
            for x in values:
                if x - 1 not in values:
                    length = 1
                    while x + length in values:
                        length += 1
                    best = max(best, length)
            return best
        """,
    ),
    P(
        "valid-sudoku-board", "Is the Sudoku Board Valid So Far?", "medium", ["hash-map"],
        statement="A partially filled 9 × 9 Sudoku `board` uses digits `\"1\"`–`\"9\"` and `\".\"` for empty cells. Return `true` if no digit repeats within any row, column or 3 × 3 box. (The board doesn't have to be solvable.)",
        inputs="- `board`: a 9 × 9 list of one-character strings",
        output="`true` or `false`.",
        constraints="- `board` is 9 × 9",
        examples=[
            ({"board": BOARD}, True, ""),
            ({"board": BAD_BOARD}, False, "Two 8s in the first column (and the top-left box)."),
        ],
        approach="Scan every filled cell once and record it in three sets: one for its row, one for its column and one for its box (`(r // 3, c // 3)`). A repeat in any set means the board is invalid.",
        explanation="Using the box coordinates as a key handles all nine boxes with one formula.",
        time="O(81)", space="O(81)",
        code="""
        def is_valid_sudoku(board: list[list[str]]) -> bool:
            seen = set()
            for r in range(9):
                for c in range(9):
                    d = board[r][c]
                    if d == ".":
                        continue
                    keys = {("row", r, d), ("col", c, d), ("box", r // 3, c // 3, d)}
                    if keys & seen:
                        return False
                    seen |= keys
            return True
        """,
    ),
    P(
        "four-lists-zero-sum", "Four Lists Summing to Zero", "medium", ["hash-map"],
        statement="Given four integer lists `a`, `b`, `c`, `d` of the same length `n`, count the index tuples `(i, j, k, l)` with `a[i] + b[j] + c[k] + d[l] == 0`.",
        inputs="- `a`, `b`, `c`, `d`: lists of `n` integers",
        output="The number of zero-sum tuples.",
        constraints="- `1 <= n <= 200`",
        examples=[
            ({"a": [1, 2], "b": [-2, -1], "c": [-1, 2], "d": [0, 2]}, 2, "(0, 0, 0, 1) and (1, 1, 0, 0)."),
            ({"a": [0], "b": [0], "c": [0], "d": [0]}, 1, ""),
        ],
        approach="Meet in the middle: count every sum `a[i] + b[j]` in a hash map, then for every `c[k] + d[l]` add the count of its negation.",
        explanation="Splitting four loops into two pairs of two loops turns O(n⁴) into O(n²).",
        time="O(n²)", space="O(n²)",
        code="""
        from collections import Counter

        def four_sum_count(a: list[int], b: list[int], c: list[int], d: list[int]) -> int:
            first = Counter(x + y for x in a for y in b)
            return sum(first[-(x + y)] for x in c for y in d)
        """,
    ),
    P(
        "sort-by-frequency", "Sort Characters by Frequency", "medium", ["hash-map", "sorting"],
        statement="Sort the characters of `s` by **decreasing frequency**. Characters with the same frequency are ordered by character code (e.g. `A` before `a`). Return the result.",
        inputs="- `s`: a string of letters and digits",
        output="The rearranged string.",
        constraints="- `1 <= s.length <= 5 × 10^5`",
        examples=[
            ({"s": "tree"}, "eert", "e appears twice; r and t once (r < t)."),
            ({"s": "Aabb"}, "bbAa", "Uppercase A sorts before lowercase a."),
        ],
        tests=[({"s": "cccaaa"}, "aaaccc")],
        approach="Count the characters, sort the distinct characters by `(−count, character)`, and write each one `count` times.",
        explanation="Only the distinct characters are sorted, so the sort is small; the output is built in one pass.",
        time="O(n + k log k) for k distinct characters", space="O(n)",
        code="""
        from collections import Counter

        def frequency_sort(s: str) -> str:
            counts = Counter(s)
            order = sorted(counts, key=lambda ch: (-counts[ch], ch))
            return "".join(ch * counts[ch] for ch in order)
        """,
    ),
    P(
        "pairs-with-difference", "Unique Pairs With Difference k", "medium", ["hash-map"],
        statement="Return the number of **unique** pairs of values `(x, y)` in `nums`, with `x <= y`, such that `y − x == k`. Pairs are counted by value, not by position.",
        inputs="- `nums`: a list of integers\n- `k`: a non-negative integer",
        output="The number of unique pairs.",
        constraints="- `1 <= nums.length <= 10^4`\n- `0 <= k <= 10^7`",
        examples=[
            ({"nums": [3, 1, 4, 1, 5], "k": 2}, 2, "(1, 3) and (3, 5)."),
            ({"nums": [1, 3, 1, 5, 4], "k": 0}, 1, "(1, 1)."),
        ],
        tests=[({"nums": [1, 2, 3, 4, 5], "k": 1}, 4)],
        approach="Count each value. For `k > 0`, count the distinct values `x` with `x + k` also present. For `k = 0`, count values that occur at least twice.",
        explanation="Working over distinct values makes each pair counted once regardless of duplicates.",
        time="O(n)", space="O(n)",
        code="""
        from collections import Counter

        def find_pairs(nums: list[int], k: int) -> int:
            counts = Counter(nums)
            if k == 0:
                return sum(1 for c in counts.values() if c > 1)
            return sum(1 for x in counts if x + k in counts)
        """,
    ),
    P(
        "lru-cache", "Least Recently Used Cache", "hard", ["hash-map"],
        statement="Design `LRUCache(capacity)` with `get(key)` (the value, or `-1` if absent) and `put(key, value)` (insert or update). When inserting into a full cache, evict the **least recently used** key first. Both operations must be O(1). Using a key with `get` or `put` makes it the most recently used.",
        inputs="- `LRUCache(capacity)`, then calls to `get` and `put`",
        output="The values returned by `get`, in order.",
        constraints="- `1 <= capacity <= 3000`\n- Up to `2 × 10^5` calls",
        examples=[
            ({"calls": [("LRUCache", 2), ("put", 1, 1), ("put", 2, 2), ("get", 1), ("put", 3, 3), ("get", 2), ("put", 4, 4), ("get", 1), ("get", 3), ("get", 4)]},
             [1, -1, -1, 3, 4], "put(3) evicts key 2; put(4) evicts key 1."),
            ({"calls": [("LRUCache", 1), ("put", 2, 1), ("get", 2), ("put", 3, 2), ("get", 2), ("get", 3)]}, [1, -1, 2], ""),
        ],
        approach="Combine a hash map (key → node) with a doubly linked list ordered by recency. `get` moves the node to the front; `put` adds/moves to the front and removes the tail node when over capacity. In Python, `OrderedDict` provides exactly this pair.",
        explanation="The hash map gives O(1) lookup; the linked list gives O(1) reordering and eviction. `move_to_end` and `popitem(last=False)` are both O(1).",
        time="O(1) per operation", space="O(capacity)",
        code="""
        from collections import OrderedDict

        class LRUCache:
            def __init__(self, capacity: int):
                self.capacity = capacity
                self.items = OrderedDict()

            def get(self, key: int) -> int:
                if key not in self.items:
                    return -1
                self.items.move_to_end(key)
                return self.items[key]

            def put(self, key: int, value: int) -> None:
                self.items[key] = value
                self.items.move_to_end(key)
                if len(self.items) > self.capacity:
                    self.items.popitem(last=False)
        """,
    ),
    P(
        "most-points-on-a-line", "Most Points on One Line", "hard", ["hash-map"],
        statement="Given distinct `points` `[x, y]` on a plane, return the maximum number of them that lie on one straight line.",
        inputs="- `points`: a list of distinct `[x, y]` pairs",
        output="The largest number of collinear points.",
        constraints="- `1 <= points.length <= 300`\n- `-10^4 <= x, y <= 10^4`",
        examples=[
            ({"points": [[1, 1], [2, 2], [3, 3]]}, 3, ""),
            ({"points": [[1, 1], [3, 2], [5, 3], [4, 1], [2, 3], [1, 4]]}, 4, "(1, 4), (2, 3), (3, 2), (4, 1)."),
        ],
        tests=[({"points": [[0, 0]]}, 1)],
        approach="For each point, count the other points by the slope between them, stored exactly as a reduced fraction `(dy, dx)` with a normalised sign. The most common slope plus the point itself is the best line through that point.",
        explanation="Floating-point slopes can make equal slopes look different; reducing by the gcd and fixing the sign gives one exact key per direction (vertical lines become `(1, 0)`).",
        time="O(n²)", space="O(n)",
        code="""
        from collections import Counter
        from math import gcd

        def max_points(points: list[list[int]]) -> int:
            best = 1
            for i, (x1, y1) in enumerate(points):
                slopes = Counter()
                for x2, y2 in points[i + 1:]:
                    dx, dy = x2 - x1, y2 - y1
                    g = gcd(dx, dy)
                    dx, dy = dx // g, dy // g
                    if dx < 0 or (dx == 0 and dy < 0):
                        dx, dy = -dx, -dy
                    slopes[(dy, dx)] += 1
                if slopes:
                    best = max(best, max(slopes.values()) + 1)
            return best
        """,
    ),
    P(
        "concatenated-word-windows", "Windows Made of All the Words", "hard", ["hash-map", "sliding-window"],
        statement="`words` all have the same length. Return every start index in `s` of a substring that is a concatenation of **all** the words, each used exactly once, in any order. Return the indices in increasing order.",
        inputs="- `s`: a lowercase string\n- `words`: a list of equal-length lowercase words (may contain duplicates)",
        output="A list of start indices.",
        constraints="- `1 <= s.length <= 10^4`\n- `1 <= words.length <= 5000`\n- `1 <= words[i].length <= 30`",
        examples=[
            ({"s": "barfoothefoobarman", "words": ["foo", "bar"]}, [0, 9], "'barfoo' at 0 and 'foobar' at 9."),
            ({"s": "wordgoodgoodgoodbestword", "words": ["word", "good", "best", "word"]}, [], "'word' is needed twice."),
        ],
        tests=[({"s": "barfoofoobarthefoobarman", "words": ["bar", "foo", "the"]}, [6, 9, 12])],
        approach="Let `w` be the word length. For each offset `0 … w−1`, slide a window over `s` in steps of `w`, keeping counts of the words inside. If a word is unknown, reset; if a word is over-used, shrink from the left. Record the start whenever the window holds exactly `len(words)` words.",
        explanation="Each offset partitions `s` into word-sized chunks, and each chunk enters and leaves the window once, so the work is O(n) per offset.",
        time="O(n · w)", space="O(number of words)",
        code="""
        from collections import Counter

        def find_substring(s: str, words: list[str]) -> list[int]:
            w, total = len(words[0]), len(words)
            need = Counter(words)
            found = []
            for offset in range(w):
                left, have, used = offset, Counter(), 0
                for right in range(offset, len(s) - w + 1, w):
                    word = s[right:right + w]
                    if word not in need:
                        left, have, used = right + w, Counter(), 0
                        continue
                    have[word] += 1
                    used += 1
                    while have[word] > need[word]:
                        have[s[left:left + w]] -= 1
                        left += w
                        used -= 1
                    if used == total:
                        found.append(left)
            return sorted(found)
        """,
    ),
]
