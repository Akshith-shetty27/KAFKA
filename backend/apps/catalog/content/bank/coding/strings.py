from . import P

TOPIC = "strings"

PROBLEMS = [
    P(
        "reverse-word-order", "Reverse the Order of Words", "easy", ["two-pointers"],
        statement="Given a string `s`, return its words in reverse order, separated by single spaces. `s` may have leading, trailing or repeated spaces; the result must not.",
        inputs="- `s`: a string of words separated by one or more spaces",
        output="A string with the words reversed and single-spaced.",
        constraints="- `1 <= s.length <= 10^4`\n- `s` contains letters, digits and spaces, and at least one word",
        examples=[
            ({"s": "the sky is blue"}, "blue is sky the", ""),
            ({"s": "  hello   world  "}, "world hello", "Extra spaces disappear."),
        ],
        approach="Split on whitespace (which drops empty pieces), reverse the list of words and join with a single space.",
        explanation="`split()` with no argument treats any run of spaces as one separator and ignores leading/trailing spaces, which removes all the edge cases at once.",
        time="O(n)", space="O(n)",
        code="""
        def reverse_words(s: str) -> str:
            return " ".join(reversed(s.split()))
        """,
    ),
    P(
        "longest-common-prefix", "Longest Common Prefix", "easy", [],
        statement="Return the longest string that is a prefix of **every** string in `words`. Return an empty string if there is none.",
        inputs="- `words`: a list of lowercase strings",
        output="The longest common prefix (possibly `\"\"`).",
        constraints="- `1 <= words.length <= 200`\n- `0 <= words[i].length <= 200`",
        examples=[
            ({"words": ["flower", "flow", "flight"]}, "fl", ""),
            ({"words": ["dog", "racecar", "car"]}, "", "The first letters already differ."),
        ],
        approach="Compare column by column: for position `i`, check that every word is long enough and has the same character as the first word. Stop at the first mismatch.",
        explanation="The prefix can never be longer than the shortest word, and the scan stops at the first column that disagrees, so the work is bounded by the total number of characters.",
        time="O(total characters)", space="O(1)",
        code="""
        def longest_common_prefix(words: list[str]) -> str:
            first = words[0]
            for i, ch in enumerate(first):
                if any(i >= len(w) or w[i] != ch for w in words[1:]):
                    return first[:i]
            return first
        """,
    ),
    P(
        "run-length-encoding", "Run-Length Encoding", "easy", [],
        statement="Encode a string by replacing every run of identical consecutive characters with the character followed by the run length. For example `aaab` becomes `a3b1`.",
        inputs="- `s`: a non-empty string of lowercase letters",
        output="The encoded string.",
        constraints="- `1 <= s.length <= 10^4`",
        examples=[
            ({"s": "aaabccdddd"}, "a3b1c2d4", ""),
            ({"s": "xyz"}, "x1y1z1", "Every run has length 1."),
        ],
        approach="Walk the string with a pointer `i`; move a second pointer `j` forward while `s[j] == s[i]`. Append `s[i]` and `j − i`, then continue from `j`.",
        explanation="Each character is visited once by `j`. Building a list of pieces and joining at the end avoids quadratic string concatenation.",
        time="O(n)", space="O(n)",
        code="""
        def run_length_encode(s: str) -> str:
            parts, i = [], 0
            while i < len(s):
                j = i
                while j < len(s) and s[j] == s[i]:
                    j += 1
                parts.append(f"{s[i]}{j - i}")
                i = j
            return "".join(parts)
        """,
    ),
    P(
        "roman-to-integer", "Roman Numeral to Integer", "easy", ["hash-map"],
        statement="Convert a valid Roman numeral `s` (I = 1, V = 5, X = 10, L = 50, C = 100, D = 500, M = 1000) to an integer. A smaller symbol placed before a larger one is subtracted (IV = 4, CM = 900).",
        inputs="- `s`: a valid Roman numeral",
        output="Its integer value.",
        constraints="- `1 <= s.length <= 15`\n- The value is between 1 and 3999",
        examples=[
            ({"s": "LVIII"}, 58, "L + V + III = 50 + 5 + 3."),
            ({"s": "MCMXCIV"}, 1994, "M + CM + XC + IV = 1000 + 900 + 90 + 4."),
        ],
        tests=[({"s": "IV"}, 4), ({"s": "MMMCMXCIX"}, 3999)],
        approach="Add each symbol's value, except subtract it when the next symbol is larger.",
        explanation="Subtractive pairs are exactly the places where a symbol is followed by a bigger one, so looking one symbol ahead is enough.",
        time="O(n)", space="O(1)",
        code="""
        VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

        def roman_to_int(s: str) -> int:
            total = 0
            for i, ch in enumerate(s):
                value = VALUES[ch]
                if i + 1 < len(s) and VALUES[s[i + 1]] > value:
                    total -= value
                else:
                    total += value
            return total
        """,
    ),
    P(
        "is-subsequence", "Is It a Subsequence?", "easy", ["two-pointers"],
        statement="Return `true` if `s` is a **subsequence** of `t` — that is, `s` can be formed by deleting some (or no) characters of `t` without changing the order of the rest.",
        inputs="- `s`: a string\n- `t`: a string",
        output="`true` or `false`.",
        constraints="- `0 <= s.length <= 100`\n- `0 <= t.length <= 10^4`",
        examples=[
            ({"s": "abc", "t": "ahbgdc"}, True, "a, b and c appear in t in that order."),
            ({"s": "axc", "t": "ahbgdc"}, False, "There is no x in t."),
        ],
        tests=[({"s": "", "t": "abc"}, True)],
        approach="Use one pointer in `s`. Scan `t`; whenever the current character of `t` equals `s[i]`, advance `i`. `s` is a subsequence if `i` reaches the end.",
        explanation="Matching each character of s as early as possible in t never hurts: it leaves the most room for the remaining characters.",
        time="O(len(t))", space="O(1)",
        code="""
        def is_subsequence(s: str, t: str) -> bool:
            i = 0
            for ch in t:
                if i < len(s) and s[i] == ch:
                    i += 1
            return i == len(s)
        """,
    ),
    P(
        "integer-to-roman", "Integer to Roman Numeral", "medium", ["greedy"],
        statement="Convert an integer `num` between 1 and 3999 to a Roman numeral, using the subtractive forms IV, IX, XL, XC, CD and CM.",
        inputs="- `num`: an integer from 1 to 3999",
        output="The Roman numeral as a string.",
        constraints="- `1 <= num <= 3999`",
        examples=[
            ({"num": 1994}, "MCMXCIV", "1000 + 900 + 90 + 4."),
            ({"num": 58}, "LVIII", "50 + 5 + 3."),
        ],
        tests=[({"num": 3749}, "MMMDCCXLIX"), ({"num": 4}, "IV")],
        approach="List the 13 symbol values from largest to smallest, including the subtractive pairs (900 = CM, 4 = IV, …). Greedily take the largest value that still fits, append its symbol and subtract.",
        explanation="With the subtractive pairs included in the table, the Roman system is canonical: the greedy choice always matches the standard numeral.",
        time="O(1)", space="O(1)",
        code="""
        SYMBOLS = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
                   (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]

        def int_to_roman(num: int) -> str:
            parts = []
            for value, symbol in SYMBOLS:
                count, num = divmod(num, value)
                parts.append(symbol * count)
            return "".join(parts)
        """,
    ),
    P(
        "parse-integer", "Parse an Integer From Text", "medium", [],
        statement="""
        Convert a string `s` to a 32-bit signed integer the way many languages' `atoi` does:

        1. Skip leading spaces.
        2. Read an optional `+` or `-` sign.
        3. Read digits until the first non-digit; ignore the rest.
        4. If no digits were read, the result is `0`.
        5. Clamp the result to the range `[-2^31, 2^31 - 1]`.
        """,
        inputs="- `s`: a string of letters, digits, spaces, `+`, `-` and `.`",
        output="The parsed integer.",
        constraints="- `0 <= s.length <= 200`",
        examples=[
            ({"s": "   -42"}, -42, "Spaces skipped, sign read, then 42."),
            ({"s": "4193 with words"}, 4193, "Reading stops at the space."),
        ],
        tests=[({"s": "words and 987"}, 0), ({"s": "-91283472332"}, -2147483648), ({"s": "+1"}, 1), ({"s": ""}, 0)],
        approach="Follow the rules with an index: skip spaces, read a sign, then accumulate digits as `value * 10 + digit`. Clamp at the end (Python integers don't overflow; in Java/C++ check before multiplying).",
        explanation="Handling the steps strictly in order covers all the tricky inputs: leading words give 0, trailing text is ignored, and huge numbers are clamped.",
        time="O(n)", space="O(1)",
        code="""
        def parse_int(s: str) -> int:
            i, n = 0, len(s)
            while i < n and s[i] == " ":
                i += 1
            sign = 1
            if i < n and s[i] in "+-":
                sign = -1 if s[i] == "-" else 1
                i += 1
            value = 0
            while i < n and s[i].isdigit():
                value = value * 10 + int(s[i])
                i += 1
            return max(-(2**31), min(2**31 - 1, sign * value))
        """,
    ),
    P(
        "count-and-say", "Count and Say", "medium", [],
        statement="The *count-and-say* sequence starts with `\"1\"`. Each next term describes the previous one: `\"1\"` is *one 1* → `\"11\"`, which is *two 1s* → `\"21\"`, then `\"1211\"`, and so on. Return the `n`-th term.",
        inputs="- `n`: a positive integer",
        output="The `n`-th term as a string.",
        constraints="- `1 <= n <= 30`",
        examples=[
            ({"n": 4}, "1211", "1 → 11 → 21 → 1211."),
            ({"n": 1}, "1", ""),
        ],
        tests=[({"n": 5}, "111221")],
        approach="Build the terms one by one. To describe a term, scan it in runs of equal digits and write each run's length followed by the digit.",
        explanation="It is run-length encoding written as count-then-digit, applied n − 1 times.",
        time="O(n · L) where L is the length of the longest term", space="O(L)",
        code="""
        def count_and_say(n: int) -> str:
            term = "1"
            for _ in range(n - 1):
                parts, i = [], 0
                while i < len(term):
                    j = i
                    while j < len(term) and term[j] == term[i]:
                        j += 1
                    parts.append(f"{j - i}{term[i]}")
                    i = j
                term = "".join(parts)
            return term
        """,
    ),
    P(
        "zigzag-rows", "Zigzag Rows", "medium", [],
        statement="Write the string `s` in a zigzag over `num_rows` rows (down the rows, then diagonally back up, and repeat), then read the rows left to right, top to bottom. Return the result.",
        inputs="- `s`: a string\n- `num_rows`: the number of rows",
        output="The row-by-row reading of the zigzag.",
        constraints="- `1 <= s.length <= 1000`\n- `1 <= num_rows <= 1000`",
        examples=[
            ({"s": "PAYPALISHIRING", "num_rows": 3}, "PAHNAPLSIIGYIR", "Rows: PAHN / APLSIIG / YIR."),
            ({"s": "PAYPALISHIRING", "num_rows": 4}, "PINALSIGYAHRPI", ""),
        ],
        tests=[({"s": "AB", "num_rows": 1}, "AB")],
        approach="Keep one string builder per row and a current row index that moves down and up. Append each character to its row, flipping direction at the top and bottom rows.",
        explanation="Simulating the pen is simpler than computing index formulas, and touches each character once. One row is a special case: the direction never flips.",
        time="O(n)", space="O(n)",
        code="""
        def zigzag(s: str, num_rows: int) -> str:
            if num_rows == 1:
                return s
            rows = [[] for _ in range(num_rows)]
            row, step = 0, 1
            for ch in s:
                rows[row].append(ch)
                if row == 0:
                    step = 1
                elif row == num_rows - 1:
                    step = -1
                row += step
            return "".join("".join(r) for r in rows)
        """,
    ),
    P(
        "multiply-number-strings", "Multiply Numbers Given as Strings", "medium", [],
        statement="Given two non-negative integers `a` and `b` as decimal strings, return their product as a string, **without** converting the whole inputs to integers.",
        inputs="- `a`: a string of digits\n- `b`: a string of digits",
        output="The product as a string with no leading zeros.",
        constraints="- `1 <= a.length, b.length <= 200`\n- No leading zeros except the number `0` itself",
        examples=[
            ({"a": "123", "b": "456"}, "56088", ""),
            ({"a": "2", "b": "3"}, "6", ""),
        ],
        tests=[({"a": "0", "b": "52"}, "0"), ({"a": "999", "b": "999"}, "998001")],
        approach="Long multiplication: digit `a[i]` times digit `b[j]` contributes to positions `i + j` and `i + j + 1` of a result array of length `len(a) + len(b)`. Add the product into position `i + j + 1` and carry into `i + j`.",
        explanation="Working right to left keeps each cell below 10 after its carry is pushed left. Strip leading zeros at the end, keeping one zero for a zero product.",
        time="O(m·n)", space="O(m + n)",
        code="""
        def multiply(a: str, b: str) -> str:
            result = [0] * (len(a) + len(b))
            for i in range(len(a) - 1, -1, -1):
                for j in range(len(b) - 1, -1, -1):
                    total = int(a[i]) * int(b[j]) + result[i + j + 1]
                    result[i + j + 1] = total % 10
                    result[i + j] += total // 10
            digits = "".join(map(str, result)).lstrip("0")
            return digits or "0"
        """,
    ),
    P(
        "shortest-palindrome-by-prepending", "Shortest Palindrome by Prepending", "hard", [],
        statement="You may add characters only to the **front** of string `s`. Return the shortest palindrome you can make this way.",
        inputs="- `s`: a string of lowercase letters (possibly empty)",
        output="The shortest palindrome that ends with `s`.",
        constraints="- `0 <= s.length <= 5 × 10^4`",
        examples=[
            ({"s": "aacecaaa"}, "aaacecaaa", "The prefix 'aacecaa' is already a palindrome; prepend the leftover 'a'."),
            ({"s": "abcd"}, "dcbabcd", "Only 'a' is a palindromic prefix."),
        ],
        tests=[({"s": ""}, ""), ({"s": "aba"}, "aba")],
        approach="Find the longest prefix of `s` that is a palindrome; prepend the reverse of the remaining suffix. To find it in linear time, build `s + '#' + reverse(s)` and compute the KMP prefix function: its last value is the length of that palindromic prefix.",
        explanation="A prefix of s that equals a suffix of reverse(s) is exactly a palindromic prefix. The `#` separator stops matches from running across the two halves. Checking every prefix naively would be O(n²).",
        time="O(n)", space="O(n)",
        code="""
        def shortest_palindrome(s: str) -> str:
            combined = s + "#" + s[::-1]
            fail = [0] * len(combined)
            for i in range(1, len(combined)):
                k = fail[i - 1]
                while k and combined[i] != combined[k]:
                    k = fail[k - 1]
                if combined[i] == combined[k]:
                    k += 1
                fail[i] = k
            keep = fail[-1] if s else 0
            return s[keep:][::-1] + s
        """,
    ),
]
