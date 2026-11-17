"""
Logical reasoning templates: number series, coding–decoding, direction sense
and blood relations.

Answers are produced by the same rule/simulation that builds the question
(series rules, ciphers, a walk on a grid, a real family tree), so the
correct option is right by construction; distractors come from near-miss
rules.
"""

import random
from collections import deque
from string import ascii_uppercase as ABC

from .common import Item, Template, need

# ============================================================== NUMBER SERIES


def _series_item(title, terms, answer, rule, wrong, key, ask="next"):
    shown = ", ".join(str(t) for t in terms)
    if ask == "next":
        statement = f"Find the next number in the series: **{shown}, ?**"
    else:
        statement = f"Find the missing number in the series: **{shown}**"
    return Item(title, statement, str(answer), [str(w) for w in wrong], rule, key=key)


def _near(answer, rng, *extra):
    return list(extra) + [answer + d for d in rng.sample([-6, -4, -3, -2, -1, 1, 2, 3, 4, 6, 10], 5) if answer + d != answer]


def ns_arithmetic(rng):
    a, d = rng.randrange(2, 60), rng.choice([3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 15, -3, -4, -6, -7])
    terms = [a + d * i for i in range(6)]
    need(min(terms) > 0)
    nxt = terms[-1] + d
    return _series_item(f"{terms[0]}, {terms[1]}, {terms[2]}, … (step {d:+})", terms, nxt,
                        f"Each term {'adds' if d > 0 else 'subtracts'} {abs(d)}: {terms[-1]} {'+' if d > 0 else '−'} {abs(d)} = **{nxt}**.",
                        _near(nxt, rng, terms[-1] - d), key=(a, d))


def ns_geometric(rng):
    a, r = rng.choice([1, 2, 3, 4, 5, 6, 7]), rng.choice([2, 3, 4])
    terms = [a * r**i for i in range(5)]
    nxt = terms[-1] * r
    return _series_item(f"{terms[0]}, {terms[1]}, {terms[2]}, … (×{r})", terms, nxt,
                        f"Each term is multiplied by {r}: {terms[-1]} × {r} = **{nxt}**.",
                        _near(nxt, rng, terms[-1] + (terms[-1] - terms[-2]), nxt + r), key=(a, r))


def ns_powers(rng):
    kind = rng.choice(["sq", "sq+1", "sq-1", "cube", "cube+1"])
    k = rng.randrange(1, 9)
    f = {"sq": lambda n: n * n, "sq+1": lambda n: n * n + 1, "sq-1": lambda n: n * n - 1, "cube": lambda n: n**3, "cube+1": lambda n: n**3 + 1}[kind]
    terms = [f(n) for n in range(k, k + 5)]
    need(terms[0] > 0)
    nxt = f(k + 5)
    desc = {"sq": "perfect squares", "sq+1": "squares plus one", "sq-1": "squares minus one", "cube": "perfect cubes", "cube+1": "cubes plus one"}[kind]
    form = {"sq": "n²", "sq+1": "n² + 1", "sq-1": "n² − 1", "cube": "n³", "cube+1": "n³ + 1"}[kind]
    return _series_item(f"{terms[0]}, {terms[1]}, {terms[2]}, … ({desc})", terms, nxt,
                        f"The terms are {desc} ({form} for n = {k}, {k + 1}, …). Next: n = {k + 5} → **{nxt}**.",
                        _near(nxt, rng, terms[-1] + 2 * (terms[-1] - terms[-2]) - (terms[-2] - terms[-3])), key=(kind, k))


def ns_growing_diff(rng):
    a, d0, step = rng.randrange(1, 40), rng.randrange(1, 6), rng.choice([1, 2, 3])
    terms, d = [a], d0
    for _ in range(5):
        terms.append(terms[-1] + d)
        d += step
    nxt = terms[-1] + d
    diffs = ", ".join(str(terms[i + 1] - terms[i]) for i in range(5))
    return _series_item(f"{terms[0]}, {terms[1]}, {terms[2]}, … (differences +{step})", terms, nxt,
                        f"Differences: {diffs} — each grows by {step}. Next difference {d}: {terms[-1]} + {d} = **{nxt}**.",
                        _near(nxt, rng, terms[-1] + d - step), key=(a, d0, step))


def ns_linear_recurrence(rng):
    m, c = rng.choice([2, 3]), rng.choice([-2, -1, 1, 2, 3])
    a = rng.randrange(1, 8)
    terms = [a]
    for _ in range(4):
        terms.append(terms[-1] * m + c)
    need(all(t > 0 for t in terms))
    nxt = terms[-1] * m + c
    return _series_item(f"{terms[0]}, {terms[1]}, {terms[2]}, … (×{m} {'+' if c > 0 else '−'} {abs(c)})", terms, nxt,
                        f"Each term = previous × {m} {'+' if c > 0 else '−'} {abs(c)}. {terms[-1]} × {m} {'+' if c > 0 else '−'} {abs(c)} = **{nxt}**.",
                        _near(nxt, rng, terms[-1] * m, terms[-1] * m - c), key=(a, m, c))


def ns_alternating(rng):
    a, d1 = rng.randrange(1, 30), rng.choice([2, 3, 4, 5, 7])
    b, d2 = rng.randrange(30, 90), rng.choice([-2, -3, -4, -5, 6])
    s1 = [a + d1 * i for i in range(4)]
    s2 = [b + d2 * i for i in range(4)]
    terms = [x for pair in zip(s1, s2) for x in pair][:7]
    nxt = s2[3]
    need(min(terms) > 0 and nxt > 0)
    return _series_item(f"Two interleaved series: {terms[0]}, {terms[1]}, {terms[2]}, …", terms, nxt,
                        f"Odd positions: {', '.join(map(str, s1))} (step {d1:+}); even positions: {', '.join(map(str, s2[:3]))} (step {d2:+}). The 8th term is on the even track: {s2[2]} {'+' if d2 > 0 else '−'} {abs(d2)} = **{nxt}**.",
                        _near(nxt, rng, s1[3] + d1, s1[3]), key=(a, d1, b, d2))


def ns_pronic(rng):
    kind = rng.choice(["n(n+1)", "n³-n", "n²+n+1", "n(n+2)"])
    f = {"n(n+1)": lambda n: n * (n + 1), "n³-n": lambda n: n**3 - n, "n²+n+1": lambda n: n * n + n + 1, "n(n+2)": lambda n: n * (n + 2)}[kind]
    k = rng.randrange(1, 7)
    terms = [f(n) for n in range(k, k + 5)]
    need(terms[0] > 0)
    nxt = f(k + 5)
    return _series_item(f"{terms[0]}, {terms[1]}, {terms[2]}, … ({kind})", terms, nxt,
                        f"Terms follow {kind} for n = {k}, {k + 1}, … . For n = {k + 5}: **{nxt}**.",
                        _near(nxt, rng, terms[-1] + (terms[-1] - terms[-2])), key=(kind, k))


def ns_missing(rng):
    a, m, c = rng.randrange(1, 9), rng.choice([2, 3]), rng.choice([0, 1, 2, -1])
    terms = [a]
    for _ in range(5):
        terms.append(terms[-1] * m + c)
    need(all(t > 0 for t in terms))
    gap = rng.randrange(2, 5)
    answer = terms[gap]
    shown = [("?" if i == gap else t) for i, t in enumerate(terms)]
    rule = f"×{m}" + (f" {'+' if c > 0 else '−'} {abs(c)}" if c else "")
    return _series_item(f"Missing term: {shown[0]}, {shown[1]}, … ({rule})", shown, answer,
                        f"Each term = previous {rule}. The gap: {terms[gap - 1]} {rule} = **{answer}** (check: {answer} {rule} = {terms[gap + 1]}).",
                        _near(answer, rng, (terms[gap - 1] + terms[gap + 1]) // 2), key=(a, m, c, gap), ask="missing")


def ns_square_diffs(rng):
    a = rng.randrange(1, 30)
    kind = rng.choice(["squares", "primes", "cubes"])
    seq = {"squares": [1, 4, 9, 16, 25, 36], "primes": [2, 3, 5, 7, 11, 13], "cubes": [1, 8, 27, 64, 125, 216]}[kind]
    terms = [a]
    for d in seq[:5]:
        terms.append(terms[-1] + d)
    nxt = terms[-1] + seq[5]
    return _series_item(f"{terms[0]}, {terms[1]}, {terms[2]}, … (differences are {kind})", terms, nxt,
                        f"Differences: {', '.join(map(str, seq[:5]))} — the {kind}. Next difference {seq[5]}: {terms[-1]} + {seq[5]} = **{nxt}**.",
                        _near(nxt, rng, terms[-1] + seq[4] + (seq[4] - seq[3])), key=(a, kind))


def ns_multiplier_steps(rng):
    a = rng.randrange(1, 6)
    mode = rng.choice(["×1,×2,×3", "×k+k", "×2,+3 alternate"])
    terms = [a]
    if mode == "×1,×2,×3":
        for k in range(1, 6):
            terms.append(terms[-1] * k)
        nxt = terms[-1] * 6
        rule = f"multiply by 1, 2, 3, 4, 5 in turn; next ×6: {terms[-1]} × 6 = **{nxt}**"
    elif mode == "×k+k":
        for k in range(1, 5):
            terms.append(terms[-1] * k + k)
        nxt = terms[-1] * 5 + 5
        rule = f"term × k + k for k = 1, 2, 3, 4; next k = 5: {terms[-1]} × 5 + 5 = **{nxt}**"
    else:
        for i in range(5):
            terms.append(terms[-1] * 2 if i % 2 == 0 else terms[-1] + 3)
        nxt = terms[-1] * 2 if len(terms) % 2 == 1 else terms[-1] + 3
        rule = f"the operations alternate ×2, +3; next is {'×2' if len(terms) % 2 == 1 else '+3'}: **{nxt}**"
    return _series_item(f"{terms[0]}, {terms[1]}, {terms[2]}, … ({mode})", terms, nxt, f"The rule: {rule}.",
                        _near(nxt, rng, terms[-1] * 2, terms[-1] + (terms[-1] - terms[-2])), key=(a, mode))


def ns_fibonacci(rng):
    a, b = rng.randrange(1, 9), rng.randrange(1, 9)
    terms = [a, b]
    for _ in range(5):
        terms.append(terms[-1] + terms[-2])
    nxt = terms[-1] + terms[-2]
    return _series_item(f"{a}, {b}, {terms[2]}, … (sum of previous two)", terms, nxt,
                        f"Each term is the sum of the two before it: {terms[-2]} + {terms[-1]} = **{nxt}**.",
                        _near(nxt, rng, terms[-1] + (terms[-1] - terms[-2])), key=(a, b))


def ns_wrong_term(rng):
    gen = rng.choice(["arith", "geo", "square", "diff"])
    if gen == "arith":
        a, d = rng.randrange(2, 40), rng.choice([3, 4, 6, 7, 9, 11])
        terms = [a + d * i for i in range(7)]
        rule = f"an arithmetic series with step {d}"
    elif gen == "geo":
        a, r = rng.choice([1, 2, 3, 5]), 2
        terms = [a * r**i for i in range(7)]
        rule = "each term doubling"
    elif gen == "square":
        k = rng.randrange(2, 8)
        terms = [n * n + 1 for n in range(k, k + 7)]
        rule = "n² + 1"
    else:
        a = rng.randrange(1, 20)
        terms = [a]
        for d in range(1, 7):
            terms.append(terms[-1] + 2 * d)
        rule = "differences 2, 4, 6, 8, …"
    i = rng.randrange(2, 6)
    right = terms[i]
    bad = right + rng.choice([-3, -2, -1, 1, 2, 3])
    need(bad > 0 and bad not in terms)
    shown = terms[:i] + [bad] + terms[i + 1 :]
    others = rng.sample([t for j, t in enumerate(shown) if j != i], 3)
    return Item(
        f"Odd one out: {', '.join(map(str, shown[:3]))}, … ({rule})",
        f"One number in this series is wrong. Find it: **{', '.join(map(str, shown))}**",
        str(bad), [str(o) for o in others],
        f"The series follows {rule}. Position {i + 1} should be {right}, but it shows **{bad}**.",
        key=(gen, tuple(terms), i),
    )


NUMBER_SERIES = [
    Template("arithmetic", "easy", ns_arithmetic),
    Template("geometric", "easy", ns_geometric),
    Template("powers", "easy", ns_powers),
    Template("growing", "easy", ns_growing_diff),
    Template("recurrence", "medium", ns_linear_recurrence),
    Template("alternating", "medium", ns_alternating),
    Template("polynomial", "medium", ns_pronic),
    Template("missing", "medium", ns_missing),
    Template("special-diffs", "medium", ns_square_diffs),
    Template("multipliers", "hard", ns_multiplier_steps),
    Template("fibonacci", "hard", ns_fibonacci),
    Template("wrong-term", "hard", ns_wrong_term),
]

# ============================================================== CODING–DECODING

WORDS = [
    "BRAIN", "CLOUD", "DREAM", "EARTH", "FLAME", "GRAPE", "HOUSE", "LIGHT", "MONEY", "NIGHT", "OCEAN", "PLANT",
    "QUEST", "RIVER", "SMILE", "TIGER", "WATER", "ZEBRA", "CHAIR", "TABLE", "PAPER", "STONE", "SUGAR", "TRAIN",
    "BREAD", "GLASS", "HEART", "MUSIC", "PRIDE", "STORM", "SPACE", "BLADE", "CROWN", "FROST", "MAGIC", "NURSE",
    "LEMON", "MOUSE", "PIANO", "ROBIN", "SHEEP", "TOWER", "WHEAT", "YOUTH", "FIELD", "CANDLE", "MARKET", "SCHOOL",
    "BRIDGE", "GARDEN", "PENCIL", "WINDOW", "FOREST", "SILVER", "PLANET", "ORANGE", "FAMILY", "DOCTOR", "BUTTER",
]


def shift(ch, k):
    return ABC[(ABC.index(ch) + k) % 26]


def encode(word, f):
    return "".join(f(i, ch) for i, ch in enumerate(word))


def _code_item(title, given, given_code, word, f, rule, rng, key, near_rules=()):
    code = encode(word, f)
    wrong = []
    for g in near_rules:
        wrong.append(encode(word, g))
    for _ in range(6):  # single-letter slips
        i = rng.randrange(len(code))
        wrong.append(code[:i] + shift(code[i], rng.choice([-1, 1])) + code[i + 1 :])
    return Item(title, f"In a certain code, **{given}** is written as **{given_code}**. How is **{word}** written in that code?",
                code, wrong, rule + f"\n\nApplying it to {word}: **{code}**.", key=key)


def cd_shift(rng):
    k = rng.choice([1, 2, 3, 4, -1, -2])
    given, word = rng.sample(WORDS, 2)
    f = lambda i, ch: shift(ch, k)
    return _code_item(f"Shift by {k:+}: {given} → {encode(given, f)}", given, encode(given, f), word, f,
                      f"Each letter moves {abs(k)} place{'s' if abs(k) > 1 else ''} {'forward' if k > 0 else 'back'} in the alphabet ({given[0]} → {shift(given[0], k)}).",
                      rng, (k, given, word), [lambda i, ch: shift(ch, -k), lambda i, ch: shift(ch, k + (1 if k > 0 else -1))])


def cd_reverse(rng):
    given, word = rng.sample([w for w in WORDS if len(w) == 5], 2)
    f = lambda i, ch, w=None: ch
    code_given, code = given[::-1], word[::-1]
    wrong = [word[1:][::-1] + word[0], word[::-1][1:] + word[-1], code[:2] + code[3] + code[2] + code[4:], word]
    return Item(f"Reversed: {given} → {code_given}", f"If **{given}** is written as **{code_given}**, how is **{word}** written in the same code?",
                code, wrong, f"The letters are simply written in reverse order. {word} reversed is **{code}**.", key=(given, word))


def cd_value_sum(rng):
    word = rng.choice([w for w in WORDS if len(w) <= 5])
    total = sum(ABC.index(c) + 1 for c in word)
    wrong = [total + d for d in (-2, -1, 1, 2, 3, 5)]
    rng.shuffle(wrong)
    return Item(f"Letter values of {word}", f"If A = 1, B = 2, …, Z = 26, what is the value of **{word}** (the sum of its letters)?",
                str(total), [str(w) for w in wrong],
                f"{' + '.join(f'{c}({ABC.index(c) + 1})' for c in word)} = **{total}**.", key=(word,))


def cd_opposite(rng):
    given, word = rng.sample(WORDS, 2)
    f = lambda i, ch: ABC[25 - ABC.index(ch)]
    return _code_item(f"Opposite letters: {given} → {encode(given, f)}", given, encode(given, f), word, f,
                      "Each letter is replaced by its mirror in the alphabet (A ↔ Z, B ↔ Y, …): the pair's positions add up to 27.",
                      rng, (given, word), [lambda i, ch: ABC[24 - ABC.index(ch)] if ABC.index(ch) < 25 else "A", lambda i, ch: shift(ch, 1)])


def cd_increasing(rng):
    start = rng.choice([1, 2])
    given, word = rng.sample(WORDS, 2)
    f = lambda i, ch: shift(ch, start + i)
    return _code_item(f"Growing shift +{start}, +{start + 1}, …: {given} → {encode(given, f)}", given, encode(given, f), word, f,
                      f"The 1st letter moves {start} place forward, the 2nd {start + 1}, the 3rd {start + 2}, and so on.",
                      rng, (start, given, word), [lambda i, ch: shift(ch, start), lambda i, ch: shift(ch, start + i + 1)])


def cd_alternate(rng):
    k = rng.choice([1, 2])
    given, word = rng.sample(WORDS, 2)
    f = lambda i, ch: shift(ch, k if i % 2 == 0 else -k)
    return _code_item(f"Alternate +{k}/−{k}: {given} → {encode(given, f)}", given, encode(given, f), word, f,
                      f"Letters in odd positions move {k} forward; letters in even positions move {k} back.",
                      rng, (k, given, word), [lambda i, ch: shift(ch, -k if i % 2 == 0 else k), lambda i, ch: shift(ch, k)])


def cd_reverse_shift(rng):
    k = rng.choice([1, 2])
    given, word = rng.sample(WORDS, 2)

    def apply(w):
        return "".join(shift(ch, k) for ch in w[::-1])

    code_given, code = apply(given), apply(word)
    wrong = ["".join(shift(ch, k) for ch in word), "".join(shift(ch, -k) for ch in word[::-1]), "".join(shift(ch, k + 1) for ch in word[::-1])]
    return Item(f"Reverse, then shift +{k}: {given} → {code_given}", f"In a certain code, **{given}** is written as **{code_given}**. How is **{word}** written in that code?",
                code, wrong, f"Write the word backwards, then move every letter {k} place{'s' if k > 1 else ''} forward. {word} → {word[::-1]} → **{code}**.",
                key=(k, given, word))


def cd_positions(rng):
    given, word = rng.sample([w for w in WORDS if len(w) <= 5], 2)
    code_given = "".join(str(ABC.index(c) + 1) for c in given)
    code = "".join(str(ABC.index(c) + 1) for c in word)
    wrong = ["".join(str(26 - ABC.index(c)) for c in word), "".join(str(ABC.index(c) + 2) for c in word), "".join(str(ABC.index(c) + 1) for c in word[::-1])]
    need(code not in wrong)
    return Item(f"Positions as digits: {given} → {code_given}", f"If **{given}** is coded as **{code_given}**, how is **{word}** coded?",
                code, wrong, f"Each letter is replaced by its position in the alphabet ({given[0]} = {ABC.index(given[0]) + 1}). {word}: **{code}**.",
                key=(given, word))


SUBSTITUTION_SETS = [
    (["sky", "sea", "water", "air", "cloud", "rain"], [("What do fish live in?", "sea"), ("What do we drink?", "water"), ("What do we breathe?", "air"), ("Where do birds fly?", "sky")]),
    (["red", "blue", "green", "yellow", "white", "black"], [("What is the colour of grass?", "green"), ("What is the colour of a clear sky?", "blue"), ("What is the colour of milk?", "white"), ("What is the colour of blood?", "red")]),
    (["pen", "book", "table", "chair", "bag", "box"], [("What do we write with?", "pen"), ("What do we sit on?", "chair"), ("What do we read?", "book")]),
    (["cow", "dog", "cat", "horse", "goat", "lion"], [("Which animal gives us milk most commonly?", "cow"), ("Which animal is called the king of the jungle?", "lion"), ("Which animal barks?", "dog")]),
]


def cd_substitution(rng):
    words, questions = rng.choice(SUBSTITUTION_SETS)
    names = words[:]
    rng.shuffle(names)
    chain = names[:]  # chain[i] is called chain[i+1]
    called = {chain[i]: chain[i + 1] for i in range(len(chain) - 1)}
    question, real = rng.choice([(q, w) for q, w in questions if w in called])
    answer = called[real]
    statement = ", ".join(f"'{a}' is called '{b}'" for a, b in called.items())
    wrong = [real] + [w for w in words if w not in (answer, real)]
    return Item(f"Name swaps: {question}", f"In a certain language, {statement}. {question}", f"{answer.capitalize()}",
                [w.capitalize() for w in wrong],
                f"The real answer is '{real}', but in this language '{real}' is called **'{answer}'** — so the answer is the code word, not the real one.",
                key=(tuple(chain), question))


VOCAB_WORDS = ["good", "bad", "you", "are", "very", "they", "and", "work", "hard", "play", "we", "smart", "always", "eat", "fruits", "sweet"]


def cd_common_words(rng):
    codes = ["pit", "dar", "na", "tok", "sa", "lu", "mi", "ka", "re", "zo", "fe", "ju"]
    for _ in range(50):
        words = rng.sample(VOCAB_WORDS, 6)
        code_of = dict(zip(words, rng.sample(codes, 6)))
        target, w2, w3, w4, w5, w6 = words
        s1, s2, s3 = [target, w2, w3], [target, w4, w5], [w3, w4, w6]
        # target is the only word common to sentences 1 and 2
        if set(s1) & set(s2) == {target}:
            break
    sentences = []
    for s in (s1, s2, s3):
        coded = [code_of[w] for w in s]
        rng.shuffle(coded)
        sentences.append(f"'{' '.join(coded)}' means '{' '.join(s)}'")
    answer = code_of[target]
    wrong = [code_of[w] for w in (w2, w3, w4, w5)]
    return Item(f"Code language: the code for '{target}'",
                f"In a code language, {sentences[0]}; {sentences[1]}; and {sentences[2]}. What is the code for **'{target}'**?",
                answer, wrong,
                f"'{target}' appears in the first two sentences and nothing else is common to both. The only code common to their coded forms is **'{answer}'**.",
                key=tuple(words))


CODING_DECODING = [
    Template("shift", "easy", cd_shift),
    Template("reverse", "easy", cd_reverse),
    Template("value", "easy", cd_value_sum),
    Template("positions", "easy", cd_positions),
    Template("opposite", "medium", cd_opposite),
    Template("growing-shift", "medium", cd_increasing),
    Template("alternate", "medium", cd_alternate),
    Template("reverse-shift", "medium", cd_reverse_shift),
    Template("substitution", "hard", cd_substitution),
    Template("common-words", "hard", cd_common_words),
]

# ============================================================== DIRECTION SENSE

DIRS = ["North", "North-East", "East", "South-East", "South", "South-West", "West", "North-West"]
VEC = {"North": (0, 1), "East": (1, 0), "South": (0, -1), "West": (-1, 0)}
PEOPLE = ["Ravi", "Meera", "Arjun", "Sana", "Kiran", "Priya", "Rahul", "Anita", "Vikram", "Lata", "Imran", "Deepa"]


def turn(direction, steps):  # steps of 45°, positive = clockwise
    return DIRS[(DIRS.index(direction) + steps) % 8]


def direction_of(dx, dy):
    ns = "North" if dy > 0 else "South" if dy < 0 else ""
    ew = "East" if dx > 0 else "West" if dx < 0 else ""
    return f"{ns}-{ew}" if ns and ew else ns or ew


def ds_facing(rng):
    start = rng.choice(["North", "East", "South", "West"])
    moves = [rng.choice([("right", 2), ("left", -2), ("about", 4)]) for _ in range(rng.choice([2, 3]))]
    facing = start
    for _, s in moves:
        facing = turn(facing, s)
    words = {"right": "turns right", "left": "turns left", "about": "turns around"}
    name = rng.choice(PEOPLE)
    seq = ", then ".join(words[m] for m, _ in moves)
    wrong = [turn(facing, 4), turn(facing, 2), turn(facing, -2), start]
    return Item(f"Facing {start}: {seq}", f"{name} is facing {start}. {name.split()[0]} {seq}. Which direction is {name} facing now?",
                facing, wrong, f"Track it step by step: {start}" + "".join(f" → {turn(start, sum(s for _, s in moves[: i + 1]))}" for i in range(len(moves))) + f". Final: **{facing}**.",
                key=(start, tuple(moves)))


def ds_degrees(rng):
    start = rng.choice(DIRS)
    a, b = rng.choice([45, 90, 135, 180]), rng.choice([45, 90, 135, 225, 270])
    cw_first = rng.random() < 0.5
    net = (a if cw_first else -a) + (-b if cw_first else b)
    need(net % 360 != 0)
    facing = turn(start, net // 45)
    wrong = [turn(start, -net // 45), turn(facing, 2), turn(facing, -2), turn(facing, 4)]
    first, second = ("clockwise", "anticlockwise") if cw_first else ("anticlockwise", "clockwise")
    return Item(f"From {start}: {a}° {first}, then {b}° {second}",
                f"A compass needle points {start}. It turns {a}° {first} and then {b}° {second}. Where does it point now?",
                facing, wrong,
                f"Net turn = {a}° {first} − {b}° {second} → {abs(net)}° {'clockwise' if net > 0 else 'anticlockwise' if net < 0 else ''}. From {start} that is **{facing}**.",
                key=(start, a, b, cw_first))


TRIPLES = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (9, 12, 15), (8, 15, 17), (12, 16, 20), (7, 24, 25)]


def ds_two_legs(rng):
    a, b, c = rng.choice(TRIPLES)
    if rng.random() < 0.5:
        a, b = b, a
    d1 = rng.choice(["North", "East", "South", "West"])
    d2 = turn(d1, rng.choice([2, -2]))
    name = rng.choice(PEOPLE)
    wrong = [f"{a + b} km", f"{abs(a - b)} km", f"{c + 1} km", f"{c - 2} km"]
    return Item(f"{a} km {d1}, then {b} km {d2}", f"{name} walks {a} km {d1} and then {b} km {d2}. How far is {name} from the starting point (in a straight line)?",
                f"{c} km", wrong, f"The two legs are at right angles, so the distance is √({a}² + {b}²) = √{a * a + b * b} = **{c} km**.",
                key=(a, b, d1, d2))


def _walk(rng, legs):
    facing = rng.choice(["North", "East", "South", "West"])
    x = y = 0
    parts = []
    for i in range(legs):
        dist = rng.randrange(2, 13)
        if i:
            t = rng.choice(["right", "left"])
            facing = turn(facing, 2 if t == "right" else -2)
            parts.append(f"turns {t} and walks {dist} km")
        else:
            parts.append(f"walks {dist} km {facing}")
        dx, dy = VEC[facing]
        x, y = x + dx * dist, y + dy * dist
    return parts, x, y, facing


def ds_walk_direction(rng):
    parts, x, y, facing = _walk(rng, rng.choice([3, 4]))
    need((x, y) != (0, 0))
    name = rng.choice(PEOPLE)
    answer = direction_of(x, y)
    wrong = [direction_of(-x, -y), direction_of(y, -x) if (y, -x) != (x, y) else "North", direction_of(-y, x), "Cannot be determined"]
    return Item(f"Walk: {'; '.join(parts)} (direction)", f"{name} {', then '.join(parts)}. In which direction is {name} now from the starting point?",
                answer, wrong,
                f"Put the start at (0, 0) with East = +x and North = +y and add up the legs: the walk ends at ({x}, {y}). "
                + " and ".join(t for t in (f"{abs(x)} km {'East' if x > 0 else 'West'}" if x else "", f"{abs(y)} km {'North' if y > 0 else 'South'}" if y else "") if t)
                + f" of the start, i.e. **{answer}**.",
                key=tuple(parts))


def ds_walk_distance(rng):
    parts, x, y, facing = _walk(rng, rng.choice([3, 4]))
    dist2 = x * x + y * y
    root = round(dist2**0.5)
    need(root * root == dist2 and root > 0)
    name = rng.choice(PEOPLE)
    wrong = [f"{abs(x) + abs(y)} km" if abs(x) + abs(y) != root else f"{root + 2} km", f"{root + 1} km", f"{root + 3} km", f"{abs(root - 2)} km" if root > 2 else f"{root + 4} km"]
    return Item(f"Walk: {'; '.join(parts)} (distance)", f"{name} {', then '.join(parts)}. How far is {name} from the starting point?",
                f"{root} km", wrong,
                f"With the start at (0, 0), East = +x and North = +y, the walk ends at ({x}, {y}). Distance = √({abs(x)}² + {abs(y)}²) = **{root} km**.",
                key=tuple(parts))


SHADOW = {  # (time, shadow side) -> facing
    ("morning", "left"): "North", ("morning", "right"): "South", ("morning", "behind"): "East", ("morning", "in front"): "West",
    ("evening", "left"): "South", ("evening", "right"): "North", ("evening", "behind"): "West", ("evening", "in front"): "East",
}


def ds_shadow(rng):
    (time, side), facing = rng.choice(list(SHADOW.items()))
    name = rng.choice(PEOPLE)
    sun = "East" if time == "morning" else "West"
    shadow = "West" if time == "morning" else "East"
    wrong = [d for d in ["North", "South", "East", "West"] if d != facing]
    where = {"left": f"to {name}'s left", "right": f"to {name}'s right", "behind": f"directly behind {name}", "in front": f"straight ahead of {name}"}[side]
    return Item(f"{time.capitalize()} shadow falling {side}", f"One {time}, {name} stood in an open field. {name}'s own shadow fell {where}. Which direction was {name} facing?",
                facing, wrong,
                f"In the {time} the sun is in the {sun}, so shadows point {shadow}. The shadow falls {where}, so {name} must be facing **{facing}**.",
                key=(time, side))


def ds_points(rng):
    names = rng.sample(["P", "Q", "R", "S", "T"], 4)
    pos = {names[0]: (0, 0)}
    clauses = []
    x = y = 0
    last = names[0]
    for n in names[1:]:
        d = rng.choice(["North", "East", "South", "West"])
        k = rng.randrange(2, 10)
        dx, dy = VEC[d]
        x, y = x + dx * k, y + dy * k
        pos[n] = (x, y)
        clauses.append(f"{n} is {k} km {d} of {last}")
        last = n
    a, b = names[-1], names[0]
    dx, dy = pos[a][0] - pos[b][0], pos[a][1] - pos[b][1]
    need((dx, dy) != (0, 0))
    answer = direction_of(dx, dy)
    wrong = [direction_of(-dx, -dy), direction_of(dy, -dx), direction_of(-dy, dx), "Cannot be determined"]
    return Item(f"Points: {'; '.join(clauses)}", f"{'. '.join(clauses)}. In which direction is {a} from {b}?", answer, wrong,
                f"Place {b} at (0, 0) (East = +x, North = +y). Following the statements, {a} ends up at ({dx}, {dy}), i.e. **{answer}** of {b}.",
                key=tuple(clauses))


DIRECTION_SENSE = [
    Template("facing", "easy", ds_facing),
    Template("two-legs", "easy", ds_two_legs),
    Template("degrees", "easy", ds_degrees),
    Template("walk-direction", "medium", ds_walk_direction),
    Template("shadow", "medium", ds_shadow),
    Template("walk-distance", "medium", ds_walk_distance),
    Template("points", "hard", ds_points),
    Template("degrees-hard", "hard", lambda rng: _hard_degrees(rng)),
    Template("walk-hard", "hard", lambda rng: _hard_walk(rng)),
]


def _hard_degrees(rng):
    item = ds_degrees(rng)
    need(item.answer in ("North-East", "South-East", "South-West", "North-West") or "135" in item.title or "225" in item.title)
    return item


def _hard_walk(rng):
    parts, x, y, facing = _walk(rng, 5)
    need((x, y) != (0, 0))
    name = rng.choice(PEOPLE)
    answer = f"{direction_of(x, y)}, facing {facing}"
    wrong = [f"{direction_of(-x, -y)}, facing {facing}", f"{direction_of(x, y)}, facing {turn(facing, 4)}", f"{direction_of(y, -x)}, facing {facing}", f"{direction_of(x, y)}, facing {turn(facing, 2)}"]
    return Item(f"Five-leg walk: {'; '.join(parts)}", f"{name} {', then '.join(parts)}. Where is {name} relative to the start, and which way is {name} facing?",
                answer, wrong,
                f"Track position and facing together (East = +x, North = +y). The walk ends at ({x}, {y}) — **{direction_of(x, y)}** of the start — and the last leg was walked facing **{facing}**.",
                key=tuple(parts))


# ============================================================== BLOOD RELATIONS

MALE = ["Aman", "Rohit", "Karan", "Vijay", "Suresh", "Mohan", "Rakesh", "Nikhil", "Arun", "Deepak", "Sameer", "Tarun", "Harish", "Gopal", "Manoj"]
FEMALE = ["Anita", "Pooja", "Kavya", "Sunita", "Rekha", "Neha", "Meena", "Divya", "Lata", "Ritu", "Sneha", "Gita", "Asha", "Uma", "Jaya"]


class Person:
    def __init__(self, name, male):
        self.name, self.male = name, male
        self.parents, self.children, self.spouse = [], [], None


def build_family(rng):
    males, females = MALE[:], FEMALE[:]
    rng.shuffle(males)
    rng.shuffle(females)
    new = lambda male: Person(males.pop() if male else females.pop(), male)
    people = []

    def couple(person):
        spouse = new(not person.male)
        person.spouse, spouse.spouse = spouse, person
        people.append(spouse)
        return spouse

    g1 = new(True)
    people.append(g1)
    g2 = couple(g1)
    for _ in range(rng.choice([2, 3])):
        child = new(rng.random() < 0.5)
        people.append(child)
        for p in (g1, g2):
            p.children.append(child)
            child.parents.append(p)
        if rng.random() < 0.8:
            spouse = couple(child)
            for _ in range(rng.choice([1, 2])):
                kid = new(rng.random() < 0.5)
                people.append(kid)
                for p in (child, spouse):
                    p.children.append(kid)
                    kid.parents.append(p)
    return people


def siblings(p):
    return {c for parent in p.parents for c in parent.children if c is not p}


def relation(x, y):
    """The word for what x is to y (None if it isn't a standard single word)."""
    m = x.male
    pick = lambda male_word, female_word: male_word if m else female_word
    if x.spouse is y:
        return pick("Husband", "Wife")
    if x in y.parents:
        return pick("Father", "Mother")
    if y in x.parents:
        return pick("Son", "Daughter")
    if x in siblings(y):
        return pick("Brother", "Sister")
    if any(x in p.parents for p in y.parents):
        return pick("Grandfather", "Grandmother")
    if any(y in p.parents for p in x.parents):
        return pick("Grandson", "Granddaughter")
    for p in y.parents:
        if x in siblings(p) or (x.spouse and x.spouse in siblings(p)):
            return pick("Uncle", "Aunt")
    for p in x.parents:
        if y in siblings(p) or (y.spouse and y.spouse in siblings(p)):
            return pick("Nephew", "Niece")
    for p in y.parents:
        for s in siblings(p):
            if x in s.children:
                return "Cousin"
    if y.spouse and x in y.spouse.parents:
        return pick("Father-in-law", "Mother-in-law")
    if x.spouse and x.spouse in y.children:
        return pick("Son-in-law", "Daughter-in-law")
    if (y.spouse and x in siblings(y.spouse)) or (x.spouse and x.spouse in siblings(y)):
        return pick("Brother-in-law", "Sister-in-law")
    return None


def edge_phrase(a, b):
    """'A is the <word> of B' for directly linked a, b (or None)."""
    word = relation(a, b)
    return word.lower() if word in ("Husband", "Wife", "Father", "Mother", "Son", "Daughter", "Brother", "Sister") else None


def neighbours(p):
    out = list(p.parents) + list(p.children) + list(siblings(p))
    if p.spouse:
        out.append(p.spouse)
    return out


def shortest_path(a, b):
    prev, queue = {a: None}, deque([a])
    while queue:
        cur = queue.popleft()
        if cur is b:
            break
        for n in neighbours(cur):
            if n not in prev:
                prev[n] = cur
                queue.append(n)
    if b not in prev:
        return None
    path, cur = [], b
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    return path[::-1]


ALL_RELATIONS = {
    True: ["Father", "Son", "Brother", "Grandfather", "Grandson", "Uncle", "Nephew", "Cousin", "Husband", "Father-in-law", "Son-in-law", "Brother-in-law"],
    False: ["Mother", "Daughter", "Sister", "Grandmother", "Granddaughter", "Aunt", "Niece", "Cousin", "Wife", "Mother-in-law", "Daughter-in-law", "Sister-in-law"],
}
COUNTERPART = dict(zip(ALL_RELATIONS[True], ALL_RELATIONS[False])) | dict(zip(ALL_RELATIONS[False], ALL_RELATIONS[True]))


def _relation_pair(rng, length):
    people = build_family(rng)
    pairs = []
    for x in people:
        for y in people:
            if x is y:
                continue
            path = shortest_path(x, y)
            if path and len(path) - 1 == length and relation(x, y) and all(edge_phrase(path[i], path[i + 1]) for i in range(length)):
                pairs.append((x, y, path))
    need(pairs)
    return rng.choice(pairs)


def _distractors(rng, x, answer):
    pool = [r for r in ALL_RELATIONS[x.male] if r != answer]
    rng.shuffle(pool)
    extra = [COUNTERPART.get(answer, "Cousin")] if COUNTERPART.get(answer) != answer else []
    return extra + pool


def br_chain(rng, length):
    x, y, path = _relation_pair(rng, length)
    statements = [f"{path[i].name} is the {edge_phrase(path[i], path[i + 1])} of {path[i + 1].name}" for i in range(length)]
    answer = relation(x, y)
    return Item(f"{' → '.join(p.name for p in path)}", f"{'. '.join(statements)}. How is {x.name} related to {y.name}?",
                answer, _distractors(rng, x, answer),
                "Follow the chain one link at a time:\n\n" + "\n".join(f"- {s}." for s in statements) + f"\n\nSo {x.name} is {y.name}'s **{answer.lower()}**.",
                key=tuple(p.name for p in path) + (answer,))


SYMBOLS = ["+", "−", "×", "÷", "#", "@", "$", "%"]


def br_coded(rng):
    x, y, path = _relation_pair(rng, 3)
    words = [edge_phrase(path[i], path[i + 1]) for i in range(3)]
    unique = sorted(set(words))
    syms = rng.sample(SYMBOLS, len(unique))
    sym_of = dict(zip(unique, syms))
    legend = "; ".join(f"**P {sym_of[w]} Q** means P is the {w} of Q" for w in unique)
    expr = f"{path[0].name} {sym_of[words[0]]} {path[1].name} {sym_of[words[1]]} {path[2].name} {sym_of[words[2]]} {path[3].name}"
    answer = relation(x, y)
    return Item(f"Coded relations: {expr}", f"{legend}. If **{expr}**, how is {x.name} related to {y.name}?", answer, _distractors(rng, x, answer),
                f"Decode each symbol: " + "; ".join(f"{path[i].name} is the {words[i]} of {path[i + 1].name}" for i in range(3)) + f". So {x.name} is {y.name}'s **{answer.lower()}**.",
                key=tuple(p.name for p in path) + (answer,))


POSSESSIVE = {"Father": "father", "Mother": "mother", "Son": "son", "Daughter": "daughter", "Brother": "brother", "Sister": "sister", "Husband": "husband", "Wife": "wife"}


def br_pointing(rng):
    speaker, target, path = _relation_pair(rng, rng.choice([2, 3]))
    # chain from the speaker: my <r1>'s <r2>... where r_i is what path[i] is to path[i-1]
    links = [relation(path[i], path[i - 1]) for i in range(1, len(path))]
    need(all(link in POSSESSIVE for link in links))
    # avoid chains like "my father's son" that could be the speaker
    for a, b in zip(links, links[1:]):
        need(not (a in ("Father", "Mother") and b in ("Son", "Daughter")))
        need(not (a in ("Son", "Daughter") and b in ("Father", "Mother")))
        need(not (a in ("Brother", "Sister") and b in ("Brother", "Sister", "Father", "Mother")))
        need(not (a in ("Husband", "Wife") and b in ("Husband", "Wife", "Son", "Daughter")))
        need(not (a in ("Father", "Mother") and b in ("Husband", "Wife")))
    answer = relation(target, speaker)
    need(answer is not None)
    pron = "He" if target.male else "She"
    phrase = "my " + "'s ".join(POSSESSIVE[l] for l in links[:-1])
    statement = (f"Pointing to a photograph, {speaker.name} says: \"{pron} is the {POSSESSIVE[links[-1]]} of {phrase}.\" How is the person in the photograph related to {speaker.name}?")
    return Item(f"Pointing to a photo: the {POSSESSIVE[links[-1]]} of {phrase}", statement, answer, _distractors(rng, target, answer),
                f"Work outward from {speaker.name}: "
                + " → ".join(f"{speaker.name}'s " + "'s ".join(POSSESSIVE[l] for l in links[: i + 1]) + f" ({path[i + 1].name})" for i in range(len(links)))
                + f". That person is {speaker.name}'s **{answer.lower()}**.",
                key=(tuple(links), target.male))


BLOOD_RELATIONS = [
    Template("chain-two", "easy", lambda rng: br_chain(rng, 2)),
    Template("chain-three", "medium", lambda rng: br_chain(rng, 3)),
    Template("photo", "medium", br_pointing),
    Template("chain-four", "hard", lambda rng: br_chain(rng, 4)),
    Template("coded", "hard", br_coded),
]

TOPICS = {
    "number-series": ("ns", NUMBER_SERIES),
    "coding-decoding": ("cd", CODING_DECODING),
    "direction-sense": ("ds", DIRECTION_SENSE),
    "blood-relations": ("br", BLOOD_RELATIONS),
}
