"""
Quantitative aptitude templates: percentages, profit & loss, time & work,
speed/time/distance, averages, ratio & proportion, interest.

Every template computes its answer with `Fraction` (no floating point), and
most re-derive it a second way (`assert` — a mismatch is a bug in the
template, so generation stops). Numbers are chosen so answers are whole or
have at most two decimals, the way placement papers are written.
"""

from fractions import Fraction as F

from .common import Item, Retry, Template, is_nice, need, nice_neighbours, num, pct, rupees

# ============================================================== PERCENTAGES


def pct_of_number(rng):
    p = rng.choice([12, 15, 16, 18, 24, 25, 35, 36, 45, 48, 55, 64, 75, 84])
    n = rng.randrange(40, 2000, 20)
    part = F(p, 100) * n
    need(is_nice(part, 0))
    statement = f"If {p}% of a number is {num(part)}, what is the number?"
    wrong = [num(part * p / 100), num(part * 100 / (100 - p)) if is_nice(part * 100 / (100 - p)) else num(n + 20), num(n - 20), num(n + 40)]
    return Item(
        f"{p}% of a number is {num(part)}", statement, num(n), wrong,
        f"""
        Let the number be N. Then {p}/100 × N = {num(part)}, so N = {num(part)} × 100 / {p} = **{num(n)}**.
        """,
        key=(p, n),
    )


def pct_successive(rng):
    a = rng.choice([10, 15, 20, 25, 30, 40, 50])
    b = rng.choice([10, 15, 20, 25, 30, 40, 50])
    up_first = rng.random() < 0.5
    x, y = (a, -b) if up_first else (-a, b)
    net = F(x + y) + F(x * y, 100)
    need(is_nice(net) and net != 0)
    words = lambda v: f"increased by {abs(v)}%" if v > 0 else f"decreased by {abs(v)}%"
    result = f"{pct(abs(net))} {'increase' if net > 0 else 'decrease'}"
    simple = F(x + y)
    wrong = [
        "No change" if simple == 0 else f"{pct(abs(simple))} {'increase' if simple > 0 else 'decrease'}",
        f"{pct(abs(net))} {'decrease' if net > 0 else 'increase'}",
        f"{pct(abs(net) + 1)} {'increase' if net > 0 else 'decrease'}",
        f"{pct(abs(F(x * y, 100)))} {'increase' if net > 0 else 'decrease'}",
    ]
    check = (100 + F(x)) * (100 + F(y)) / 100 - 100
    assert check == net
    return Item(
        f"{'Up' if x > 0 else 'Down'} {abs(x)}%, then {'up' if y > 0 else 'down'} {abs(y)}%",
        f"A price is first {words(x)} and then {words(y)}. What is the net percentage change?",
        result, wrong,
        f"""
        Take 100. After the first change: {num(100 + x)}. The second change applies to that new value:
        {num(100 + x)} × {num(100 + y)}/100 = {num((100 + F(x)) * (100 + y) / 100)}.
        Net change = **{result}**.

        Shortcut for successive changes x% and y%: x + y + xy/100 = {x} + ({y}) + ({x}×{y})/100 = {num(net)}.
        """,
        key=(x, y),
    )


MORE_LESS = [(25, 20), (100, 50), (150, 60), (300, 75), (400, 80), (50, F(100, 3)), (20, F(50, 3)), (60, F(75, 2))]


def pct_more_less(rng):
    more, less = rng.choice(MORE_LESS)
    need(is_nice(more) and is_nice(less))
    a, b = rng.sample(["Asha", "Ravi", "Meena", "Kiran", "Farhan", "Divya", "Joseph", "Neha"], 2)
    thing = rng.choice(["salary", "monthly income", "score", "savings"])
    if rng.random() < 0.5:
        statement = f"{a}'s {thing} is {pct(more)} more than {b}'s. By what percentage is {b}'s {thing} less than {a}'s?"
        answer, given = pct(less), pct(more)
        expl = f"Let {b} = 100, so {a} = {num(100 + more)}. The gap {num(more)} is measured on {a}'s value: {num(more)} / {num(100 + more)} × 100 = **{answer}**."
        key = ("more", more)
    else:
        statement = f"{b}'s {thing} is {pct(less)} less than {a}'s. By what percentage is {a}'s {thing} more than {b}'s?"
        answer, given = pct(more), pct(less)
        expl = f"Let {a} = 100, so {b} = {num(100 - less)}. The gap {num(less)} is measured on {b}'s value: {num(less)} / {num(100 - less)} × 100 = **{answer}**."
        key = ("less", less)
    wrong = [given, pct(F(more + less, 2)), pct(abs(more - less)) if more != less else "10%", pct(more + 5), pct(less + 5)]
    return Item(f"{given} {'more' if key[0] == 'more' else 'less'}: the reverse comparison ({thing})", statement, answer, wrong,
                expl + "\n\nThe base changes, so the two percentages are not equal.", key=key)


def pct_growth(rng):
    base = rng.choice([8000, 10000, 12000, 15000, 20000, 25000, 40000, 50000])
    r1, r2 = rng.choice([5, 10, 15, 20, 25]), rng.choice([5, 10, 15, 20, -10, -5])
    final = F(base) * (100 + r1) / 100 * (100 + r2) / 100
    need(is_nice(final, 0))
    thing, short = rng.choice([("population of a town", "Town population"), ("number of members of a club", "Club membership"), ("value of a machine", "Machine value")])
    change = lambda r: f"increases by {r}%" if r > 0 else f"decreases by {-r}%"
    wrong = [num(base * (100 + r1 + r2) / F(100)), num(final + base // 100), num(final - base // 100), num(final + base // 50)]
    return Item(
        f"{short} of {num(base)} over two years ({r1:+}%, {r2:+}%)",
        f"The {thing} is {num(base)}. In the first year it {change(r1)}; in the second year it {change(r2)}. What is it after two years?",
        num(final), wrong,
        f"""
        Successive changes multiply: {num(base)} × {num(100 + r1)}/100 × {num(100 + r2)}/100 = **{num(final)}**.
        Adding the rates ({r1} + {r2} = {r1 + r2}%) and applying once gives {num(base * (100 + r1 + r2) / F(100))} — the classic trap.
        """,
        key=(base, r1, r2, thing),
    )


def pct_pass_marks(rng):
    p = rng.choice([30, 33, 35, 36, 40, 45])
    total = rng.choice([200, 300, 400, 500, 600, 700, 800, 900, 1000])
    pass_marks = F(p * total, 100)
    need(is_nice(pass_marks, 0))
    fail_by = rng.randrange(5, int(pass_marks) // 2)
    got = pass_marks - fail_by
    wrong = [num(got * 100 / p) if is_nice(got * 100 / p, 0) else num(total + 100), num(total - 100), num(total + 100), num(total + 200)]
    return Item(
        f"Failing by {fail_by} marks with {num(got)}",
        f"A student needs {p}% of the maximum marks to pass. She scores {num(got)} marks and fails by {fail_by} marks. What are the maximum marks?",
        num(total), wrong,
        f"""
        Pass marks = {num(got)} + {fail_by} = {num(pass_marks)}. These are {p}% of the maximum:
        maximum = {num(pass_marks)} × 100 / {p} = **{num(total)}**.
        """,
        key=(p, total, fail_by),
    )


PRICE_CHANGE = [(25, 20, "rises"), (100, 50, "rises"), (150, 60, "rises"), (300, 75, "rises"),
                (20, 25, "falls"), (50, 100, "falls"), (60, 150, "falls"), (75, 300, "falls")]


def pct_consumption(rng):
    r, answer, direction = rng.choice(PRICE_CHANGE)
    item = rng.choice(["sugar", "petrol", "rice", "cooking oil", "milk"])
    if direction == "rises":
        statement = f"The price of {item} rises by {r}%. By what percentage must a family reduce its consumption so that its spending on {item} stays the same?"
        expl = f"Spending = price × quantity. Price becomes {num(F(100 + r, 100))}×, so quantity must become 100/{100 + r} of its value — a reduction of {r}/{100 + r} × 100 = **{answer}%**."
        check = F(r, 100 + r) * 100
    else:
        statement = f"The price of {item} falls by {r}%. By what percentage can a family increase its consumption without changing its spending on {item}?"
        expl = f"Price becomes {num(F(100 - r, 100))}×, so quantity can become 100/{100 - r} of its value — an increase of {r}/{100 - r} × 100 = **{answer}%**."
        check = F(r, 100 - r) * 100
    assert check == answer
    wrong = [pct(r), pct(answer + 5), pct(abs(answer - 5)), pct(F(r, 2))]
    return Item(f"Price {direction} {r}%: adjusting {item} consumption", statement, pct(answer), wrong, expl, key=(r, direction, item))


def pct_election(rng):
    p = rng.choice([52, 54, 55, 56, 58, 60, 62, 65])
    total = rng.randrange(5000, 60000, 500)
    margin = F(2 * p - 100, 100) * total
    need(is_nice(margin, 0))
    wrong = [num(margin * 100 / p) if is_nice(margin * 100 / p, 0) else num(total + 1000), num(total + 2000), num(total - 1000), num(total * 2)]
    return Item(
        f"Won with {p}% by {num(margin)} votes",
        f"In an election between two candidates, the winner gets {p}% of the votes cast and wins by {num(margin)} votes. How many votes were cast in all? (All votes were valid.)",
        num(total), wrong,
        f"""
        The loser gets {100 - p}%, so the margin is {p}% − {100 - p}% = {2 * p - 100}% of the votes.
        {2 * p - 100}% of V = {num(margin)} → V = {num(margin)} × 100 / {2 * p - 100} = **{num(total)}**.
        """,
        key=(p, total),
    )


def pct_salary_spending(rng):
    a = rng.choice([20, 25, 30, 40, 50])
    b = rng.choice([10, 20, 25, 30, 40])
    c = rng.choice([10, 20, 25, 50])
    salary = rng.randrange(10000, 120000, 1000)
    after_a = salary * F(100 - a, 100)
    after_b = after_a * F(100 - b, 100)
    saved = after_b * F(100 - c, 100)
    need(all(is_nice(v, 0) for v in (after_a, after_b, saved)))
    wrong = [num(saved * 100 / (100 - a - b - c)) if 100 - a - b - c > 0 and is_nice(saved * 100 / (100 - a - b - c), 0) else num(salary + 5000),
             num(salary + 2000), num(salary - 2000), num(salary + 10000)]
    return Item(
        f"Saving {rupees(saved)} after three expenses",
        f"Ramesh spends {a}% of his salary on rent, {b}% of the remainder on food and {c}% of what is then left on travel. He saves the rest, which is {rupees(saved)}. What is his salary?",
        rupees(salary), [f"₹{w}" for w in wrong],
        f"""
        Work backwards with the fraction left at each step:
        salary × {num(F(100 - a, 100))} × {num(F(100 - b, 100))} × {num(F(100 - c, 100))} = {num(saved)}.
        Salary = {num(saved)} / {num(F(100 - a, 100) * F(100 - b, 100) * F(100 - c, 100))} = **{rupees(salary)}**.
        Each percentage applies to what is *left*, so you can't just add {a} + {b} + {c}.
        """,
        key=(a, b, c, salary),
    )


def pct_two_candidates_marks(rng):
    p1 = rng.choice([25, 28, 30, 32])
    p2 = rng.choice([40, 42, 45, 48, 50])
    total = rng.choice([300, 400, 500, 600, 800, 1000])
    pass_mark = rng.randrange(int(total * p1 / 100) + 5, int(total * p2 / 100) - 4)
    a_score = F(p1 * total, 100)
    b_score = F(p2 * total, 100)
    need(is_nice(a_score, 0) and is_nice(b_score, 0))
    fail_by = pass_mark - a_score
    above = b_score - pass_mark
    need(fail_by > 0 and above > 0)
    wrong = [num(total + 100), num(total - 100), num(total + 200), num((fail_by + above) * 100 / p2) if is_nice((fail_by + above) * 100 / p2, 0) else num(total + 300)]
    return Item(
        f"{p1}% fails by {num(fail_by)}, {p2}% passes by {num(above)}",
        f"In an exam, a candidate who scores {p1}% of the maximum marks fails by {num(fail_by)} marks, while another who scores {p2}% gets {num(above)} marks more than the pass mark. What are the maximum marks?",
        num(total), wrong,
        f"""
        The gap between the two scores is {num(fail_by)} + {num(above)} = {num(fail_by + above)} marks,
        which equals {p2}% − {p1}% = {p2 - p1}% of the maximum.
        Maximum = {num(fail_by + above)} × 100 / {p2 - p1} = **{num(total)}**. (Pass mark = {pass_mark}.)
        """,
        key=(p1, p2, total, pass_mark),
    )


def pct_invalid_votes(rng):
    invalid = rng.choice([10, 15, 20, 25])
    p = rng.choice([55, 56, 60, 62, 65, 70])
    total = rng.randrange(4000, 40000, 400)
    valid = total * F(100 - invalid, 100)
    margin = valid * F(2 * p - 100, 100)
    need(is_nice(valid, 0) and is_nice(margin, 0))
    naive = margin * 100 / (2 * p - 100)
    wrong = [num(naive), num(total + 1000), num(total - 800), num(total + 2000)]
    return Item(
        f"{invalid}% invalid votes, winner by {num(margin)}",
        f"In an election between two candidates, {invalid}% of the votes cast were invalid. The winner got {p}% of the valid votes and won by {num(margin)} votes. How many votes were cast?",
        num(total), wrong,
        f"""
        Margin = {p}% − {100 - p}% = {2 * p - 100}% of the valid votes, so valid votes = {num(margin)} × 100 / {2 * p - 100} = {num(valid)}.
        These are {100 - invalid}% of all votes cast: total = {num(valid)} × 100 / {100 - invalid} = **{num(total)}**.
        """,
        key=(invalid, p, total),
    )


def pct_three_changes(rng):
    rates = [rng.choice([10, 20, 25, 50]), -rng.choice([10, 20, 25, 50]), rng.choice([10, 20, 25, 50])]
    rng.shuffle(rates)
    factor = F(1)
    for r in rates:
        factor *= F(100 + r, 100)
    net = (factor - 1) * 100
    need(is_nice(net) and net != 0)
    describe = ", then ".join(f"{'raised' if r > 0 else 'cut'} by {abs(r)}%" for r in rates)
    result = f"{pct(abs(net))} {'increase' if net > 0 else 'decrease'}"
    wrong = [f"{pct(abs(sum(rates)))} {'increase' if sum(rates) > 0 else 'decrease'}" if sum(rates) else "No change",
             f"{pct(abs(net))} {'decrease' if net > 0 else 'increase'}", f"{pct(abs(net) + 2)} {'increase' if net > 0 else 'decrease'}",
             f"{pct(abs(net) + 5)} {'increase' if net > 0 else 'decrease'}"]
    return Item(
        "Three successive price changes: " + ", ".join(f"{r:+}%" for r in rates),
        f"The price of a laptop is {describe}. What is the overall percentage change?",
        result, wrong,
        f"""
        Multiply the factors: {' × '.join(num(F(100 + r, 100)) for r in rates)} = {num(factor, 4)}.
        So the price changes by {num(factor, 4)} − 1 = {num(net / 100, 4)} → **{result}**.
        """,
        key=tuple(rates),
    )


PERCENTAGES = [
    Template("of-number", "easy", pct_of_number),
    Template("successive", "easy", pct_successive),
    Template("more-less", "easy", pct_more_less),
    Template("growth", "easy", pct_growth),
    Template("pass-marks", "medium", pct_pass_marks),
    Template("consumption", "medium", pct_consumption),
    Template("election", "medium", pct_election),
    Template("spending", "medium", pct_salary_spending),
    Template("two-candidates", "hard", pct_two_candidates_marks),
    Template("invalid-votes", "hard", pct_invalid_votes),
    Template("three-changes", "hard", pct_three_changes),
]

# ============================================================== PROFIT AND LOSS


def pl_percent(rng):
    cp = rng.randrange(200, 5000, 50)
    r = rng.choice([-25, -20, -15, -12, -10, -8, -5, 4, 5, 8, 10, 12, 15, 16, 20, 25, 30, 40])
    sp = cp * F(100 + r, 100)
    need(is_nice(sp, 0))
    label = f"{pct(abs(r))} {'profit' if r > 0 else 'loss'}"
    on_sp = abs(sp - cp) / sp * 100
    wrong = [f"{pct(abs(r))} {'loss' if r > 0 else 'profit'}", f"{pct(on_sp)} {'profit' if r > 0 else 'loss'}" if is_nice(on_sp) else f"{pct(abs(r) + 2)} {'profit' if r > 0 else 'loss'}",
             f"{pct(abs(r) + 5)} {'profit' if r > 0 else 'loss'}", f"{pct(abs(r) - 2)} {'profit' if r > 0 else 'loss'}"]
    return Item(
        f"Bought for {rupees(cp)}, sold for {rupees(sp)}",
        f"An article bought for {rupees(cp)} is sold for {rupees(sp)}. What is the profit or loss percentage?",
        label, wrong,
        f"""
        {'Profit' if r > 0 else 'Loss'} = |{num(sp)} − {num(cp)}| = {rupees(abs(sp - cp))}. Profit and loss percentages are always on the **cost price**:
        {num(abs(sp - cp))} / {num(cp)} × 100 = **{label}**.
        """,
        key=(cp, r),
    )


def pl_find_sp(rng):
    cp = rng.randrange(400, 6000, 100)
    r = rng.choice([5, 8, 10, 12, 15, 20, 25, 30, -5, -10, -15, -20])
    sp = cp * F(100 + r, 100)
    need(is_nice(sp, 0))
    wrong = [rupees(cp * F(100 - r, 100)), rupees(cp + r * 10), rupees(cp * 100 / F(100 - r)) if is_nice(cp * 100 / F(100 - r), 0) else rupees(sp + 50), rupees(sp + 100)]
    return Item(
        f"Selling price for a {abs(r)}% {'gain' if r > 0 else 'loss'} on {rupees(cp)}",
        f"A trader buys a phone for {rupees(cp)}. At what price must he sell it to make a {abs(r)}% {'profit' if r > 0 else 'loss'}?",
        rupees(sp), wrong,
        f"SP = CP × (100 {'+' if r > 0 else '−'} {abs(r)})/100 = {num(cp)} × {num(100 + r)}/100 = **{rupees(sp)}**.",
        key=(cp, r),
    )


def pl_find_cp(rng):
    cp = rng.randrange(300, 5000, 50)
    r = rng.choice([10, 20, 25, -10, -20, -25, 15, -15, 12, -4, 5, -5])
    sp = cp * F(100 + r, 100)
    need(is_nice(sp, 0))
    naive = sp * F(100 - r, 100)
    wrong = [rupees(naive) if is_nice(naive) else rupees(cp + 30), rupees(cp + 50), rupees(cp - 50), rupees(sp)]
    return Item(
        f"Cost price from {rupees(sp)} at {abs(r)}% {'profit' if r > 0 else 'loss'}",
        f"By selling a watch for {rupees(sp)}, a shopkeeper makes a {abs(r)}% {'profit' if r > 0 else 'loss'}. What did the watch cost him?",
        rupees(cp), wrong,
        f"""
        SP = CP × {num(100 + r)}/100, so CP = SP × 100/{num(100 + r)} = {num(sp)} × 100/{num(100 + r)} = **{rupees(cp)}**.
        (Taking {abs(r)}% of the *selling* price gives {rupees(naive) if is_nice(naive) else 'a wrong value'} — percentages are on cost.)
        """,
        key=(cp, r),
    )


def pl_discount(rng):
    mp = rng.randrange(500, 9000, 100)
    d = rng.choice([5, 10, 12, 15, 20, 25, 30, 35, 40])
    sp = mp * F(100 - d, 100)
    need(is_nice(sp, 0))
    wrong = [rupees(mp * F(d, 100)), rupees(mp * 100 / F(100 + d)) if is_nice(mp * 100 / F(100 + d), 0) else rupees(sp + 100), rupees(sp - 50), rupees(sp + 50)]
    return Item(
        f"{d}% off a marked price of {rupees(mp)}",
        f"A jacket is marked at {rupees(mp)} and sold at a {d}% discount. What is the selling price?",
        rupees(sp), wrong,
        f"Discount is on the marked price: {num(mp)} × {d}/100 = {rupees(mp * F(d, 100))}. Selling price = {num(mp)} − {num(mp * F(d, 100))} = **{rupees(sp)}**.",
        key=(mp, d),
    )


def pl_markup_discount(rng):
    m = rng.choice([20, 25, 30, 40, 50, 60, 75, 80, 100])
    d = rng.choice([10, 12, 15, 20, 25, 30])
    net = (F(100 + m) * F(100 - d) / 100) - 100
    need(is_nice(net) and net != 0)
    label = f"{pct(abs(net))} {'profit' if net > 0 else 'loss'}"
    wrong = [f"{pct(abs(m - d))} {'profit' if m > d else 'loss'}" if m != d else "No profit, no loss",
             f"{pct(abs(net) + 2)} {'profit' if net > 0 else 'loss'}", f"{pct(abs(net) - 2)} {'profit' if net > 0 else 'loss'}" if abs(net) > 2 else "1% loss",
             f"{pct(abs(net) + 5)} {'profit' if net > 0 else 'loss'}"]
    return Item(
        f"Marked {m}% above cost, {d}% discount",
        f"A shopkeeper marks his goods {m}% above the cost price and then allows a discount of {d}% on the marked price. What is his profit or loss percentage?",
        label, wrong,
        f"""
        Take CP = 100. Marked price = {100 + m}. After a {d}% discount: {100 + m} × {100 - d}/100 = {num(F(100 + m) * F(100 - d) / 100)}.
        Result on a cost of 100: **{label}**. (Subtracting {m} − {d} ignores that the discount is taken on the larger marked price.)
        """,
        key=(m, d),
    )


def pl_successive_discounts(rng):
    d1, d2 = rng.choice([10, 15, 20, 25, 30]), rng.choice([5, 10, 15, 20])
    single = 100 - F(100 - d1) * F(100 - d2) / 100
    need(is_nice(single))
    wrong = [pct(d1 + d2), pct(single + 1), pct(single - 1), pct(F(d1 * d2, 100))]
    return Item(
        f"Discounts of {d1}% and {d2}% in a row",
        f"A store offers successive discounts of {d1}% and {d2}%. What single discount is equivalent to these two?",
        pct(single), wrong,
        f"""
        After both discounts a ₹100 item costs 100 × {num(F(100 - d1, 100))} × {num(F(100 - d2, 100))} = {num(F(100 - d1) * F(100 - d2) / 100)}.
        Single equivalent discount = 100 − {num(F(100 - d1) * F(100 - d2) / 100)} = **{pct(single)}**  (formula: d1 + d2 − d1·d2/100).
        """,
        key=(d1, d2),
    )


def pl_same_sp(rng):
    x = rng.choice([5, 10, 12, 15, 20, 25, 30])
    sp = rng.randrange(500, 5000, 10)
    cp1, cp2 = sp * F(100, 100 + x), sp * F(100, 100 - x)
    need(is_nice(cp1) and is_nice(cp2))
    loss = F(x * x, 100)
    total_check = (2 * sp - cp1 - cp2) / (cp1 + cp2) * 100
    assert total_check == -loss
    wrong = ["No profit, no loss", f"{pct(loss)} gain", f"{pct(2 * loss)} loss", f"{pct(x)} loss"]
    return Item(
        f"Two items at {rupees(sp)}: {x}% gain and {x}% loss",
        f"Two cycles are sold for {rupees(sp)} each. On one the seller gains {x}% and on the other he loses {x}%. What is his overall gain or loss percentage?",
        f"{pct(loss)} loss", wrong,
        f"""
        Costs: {num(sp)} × 100/{100 + x} = {num(cp1)} and {num(sp)} × 100/{100 - x} = {num(cp2)}; total cost {num(cp1 + cp2)} vs revenue {num(2 * sp)}.
        Equal selling prices with equal gain% and loss% always give a loss of x²/100 = {x}²/100 = **{pct(loss)}**.
        """,
        key=(x, sp),
    )


def pl_loss_to_gain(rng):
    cp = rng.randrange(200, 4000, 20)
    loss = rng.choice([5, 10, 12, 15, 20, 25])
    gain = rng.choice([5, 10, 15, 20, 25, 30])
    sp1, sp2 = cp * F(100 - loss, 100), cp * F(100 + gain, 100)
    need(is_nice(sp1, 0) and is_nice(sp2, 0))
    wrong = [rupees(sp1 * F(100 + loss + gain, 100)) if is_nice(sp1 * F(100 + loss + gain, 100)) else rupees(sp2 + 40), rupees(sp2 + 20), rupees(sp2 - 20), rupees(sp1 + cp * F(gain, 100))]
    return Item(
        f"From {loss}% loss at {rupees(sp1)} to {gain}% gain",
        f"By selling a table for {rupees(sp1)}, a carpenter loses {loss}%. At what price should he sell it to gain {gain}%?",
        rupees(sp2), wrong,
        f"CP = {num(sp1)} × 100/{100 - loss} = {rupees(cp)}. For a {gain}% gain, SP = {num(cp)} × {100 + gain}/100 = **{rupees(sp2)}**.",
        key=(cp, loss, gain),
    )


def pl_articles_ratio(rng):
    n_buy, n_sell = rng.choice([(10, 8), (12, 10), (15, 12), (20, 16), (6, 5), (10, 9), (8, 6), (25, 20), (12, 9)])
    price = rng.choice([10, 12, 15, 20, 25, 30, 50])
    # buys n_buy for ₹price, sells n_sell for ₹price
    cp_each, sp_each = F(price, n_buy), F(price, n_sell)
    gain = (sp_each - cp_each) / cp_each * 100
    need(is_nice(gain))
    wrong = [pct(F(n_buy - n_sell, n_buy) * 100), pct(gain + 5), pct(abs(gain - 5)), pct(n_buy - n_sell)]
    return Item(
        f"Buy {n_buy} for ₹{price}, sell {n_sell} for ₹{price}",
        f"A vendor buys bananas at {n_buy} for ₹{price} and sells them at {n_sell} for ₹{price}. What is his profit percentage?",
        pct(gain), wrong,
        f"""
        CP of one = {price}/{n_buy}, SP of one = {price}/{n_sell}. Profit % = (SP − CP)/CP × 100 = ({n_buy} − {n_sell})/{n_sell} × 100 = **{pct(gain)}**.
        (Dividing by {n_buy} instead of {n_sell} measures the profit on the selling price — a common slip.)
        """,
        key=(n_buy, n_sell, price),
    )


def pl_two_gains_difference(rng):
    g1, g2 = sorted(rng.sample([4, 5, 6, 8, 10, 12, 15, 18, 20], 2))
    cp = rng.randrange(200, 6000, 50)
    diff = cp * F(g2 - g1, 100)
    need(is_nice(diff, 0))
    wrong = [rupees(diff * 100 / g2) if is_nice(diff * 100 / g2, 0) else rupees(cp + 200), rupees(cp + 100), rupees(cp - 100), rupees(cp * 2)]
    return Item(
        f"Selling at {g1}% vs {g2}% gain differs by {rupees(diff)}",
        f"If an article is sold at a {g2}% gain instead of a {g1}% gain, the seller gets {rupees(diff)} more. What is the cost price?",
        rupees(cp), wrong,
        f"The difference of {g2}% − {g1}% = {g2 - g1}% of CP is {rupees(diff)}, so CP = {num(diff)} × 100/{g2 - g1} = **{rupees(cp)}**.",
        key=(g1, g2, cp),
    )


def pl_markup_needed(rng):
    d = rng.choice([10, 20, 25, 40, 50])
    p = rng.choice([8, 10, 12, 20, 26, 35, 50])
    m = F(100 + p) * 100 / (100 - d) - 100
    need(is_nice(m) and m > 0)
    wrong = [pct(p + d), pct(m + 5), pct(abs(m - 5)), pct(F(p + d) * 100 / 100 + 10)]
    return Item(
        f"Mark-up for {p}% profit after a {d}% discount",
        f"A trader wants a {p}% profit even after giving a {d}% discount. By what percentage above the cost price should he mark his goods?",
        pct(m), wrong,
        f"""
        Take CP = 100, so the required SP = {100 + p}. That is {100 - d}% of the marked price: MP = {100 + p} × 100/{100 - d} = {num(100 + m)}.
        Mark-up = **{pct(m)}** above cost. (Adding {p} + {d} = {p + d}% falls short because the discount is taken on the larger marked price.)
        """,
        key=(d, p),
    )


PROFIT_LOSS = [
    Template("percent", "easy", pl_percent),
    Template("find-sp", "easy", pl_find_sp),
    Template("find-cp", "easy", pl_find_cp),
    Template("discount", "easy", pl_discount),
    Template("markup-discount", "medium", pl_markup_discount),
    Template("successive-discounts", "medium", pl_successive_discounts),
    Template("same-sp", "medium", pl_same_sp),
    Template("loss-to-gain", "medium", pl_loss_to_gain),
    Template("articles", "hard", pl_articles_ratio),
    Template("two-gains", "hard", pl_two_gains_difference),
    Template("markup-needed", "hard", pl_markup_needed),
]

# ============================================================== TIME AND WORK

NAMES = ["A", "B", "C"]


def days(x) -> str:
    return f"{num(x)} days"


def tw_together(rng):
    a, b = rng.sample([4, 5, 6, 8, 9, 10, 12, 14, 15, 18, 20, 21, 24, 28, 30, 36, 40, 45, 60], 2)
    t = F(a * b, a + b)
    need(is_nice(t, 1))
    wrong = [days(F(a + b, 2)), days(t + 1), days(abs(a - b)) if a != b else days(t + 2), days(t + 2)]
    return Item(
        f"{a}-day and {b}-day workers together",
        f"A can finish a piece of work in {a} days and B can finish it in {b} days. How many days will they take working together?",
        days(t), wrong,
        f"""
        In one day A does 1/{a} and B does 1/{b} of the work; together 1/{a} + 1/{b} = {F(1, a) + F(1, b)} of it.
        Time = 1 ÷ {F(1, a) + F(1, b)} = **{days(t)}**  (shortcut: ab/(a + b) = {a * b}/{a + b}).
        """,
        key=tuple(sorted((a, b))),
    )


def tw_find_one(rng):
    a, t = rng.choice([4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 30, 36]), rng.choice([2, 3, 4, 5, 6, 8, 9, 10, 12])
    need(a > t)
    b = F(a * t, a - t)
    need(is_nice(b, 0))
    wrong = [days(a - t), days(b + 2), days(b - 2) if b > 3 else days(b + 3), days(a + t)]
    return Item(
        f"Together in {t} days, A alone in {a}: B alone?",
        f"A and B together can complete a task in {t} days. A alone can complete it in {a} days. In how many days can B alone complete it?",
        days(b), wrong,
        f"B's daily work = 1/{t} − 1/{a} = {F(1, t) - F(1, a)}, so B alone takes **{days(b)}**.",
        key=(a, t),
    )


def tw_men_days(rng):
    m1, d1 = rng.choice([6, 8, 10, 12, 15, 16, 18, 20, 24, 25, 30]), rng.choice([6, 8, 10, 12, 15, 16, 18, 20, 24])
    m2 = rng.choice([4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 30, 36, 40])
    need(m1 != m2)
    d2 = F(m1 * d1, m2)
    need(is_nice(d2, 0))
    wrong = [days(F(m2 * d1, m1)) if is_nice(F(m2 * d1, m1)) else days(d2 + 3), days(d2 + 2), days(abs(d2 - 2)), days(d1 + m1 - m2) if d1 + m1 - m2 > 0 else days(d2 + 4)]
    return Item(
        f"{m1} workers in {d1} days → {m2} workers",
        f"{m1} workers can build a wall in {d1} days. How many days will {m2} workers take to build the same wall, working at the same rate?",
        days(d2), wrong,
        f"Total work = {m1} × {d1} = {m1 * d1} worker-days. With {m2} workers: {m1 * d1} / {m2} = **{days(d2)}**.",
        key=(m1, d1, m2),
    )


def tw_leaves(rng):
    a, b = rng.sample([10, 12, 15, 18, 20, 24, 30, 36, 40, 45], 2)
    k = rng.choice([2, 3, 4, 5, 6])
    done = k * (F(1, a) + F(1, b))
    need(done < 1)
    rest = (1 - done) * b
    total = k + rest
    need(is_nice(total, 1))
    wrong = [days(rest), days(total + 1), days(total - 1), days(F(a * b, a + b) + k) if is_nice(F(a * b, a + b)) else days(total + 2)]
    return Item(
        f"A ({a} d) and B ({b} d) together for {k} days, then B alone",
        f"A can do a job in {a} days and B in {b} days. They work together for {k} days, after which A leaves. In how many days, in total, is the job finished?",
        days(total), wrong,
        f"""
        In {k} days together they finish {k} × (1/{a} + 1/{b}) = {done} of the job. Remaining {1 - done} is done by B alone in {1 - done} × {b} = {num(rest)} days.
        Total = {k} + {num(rest)} = **{days(total)}**.
        """,
        key=(a, b, k),
    )


def tw_pipes(rng):
    fill, drain = rng.sample([3, 4, 5, 6, 8, 9, 10, 12, 15, 18, 20, 24], 2)
    need(fill < drain)
    t = F(fill * drain, drain - fill)
    need(is_nice(t, 1))
    wrong = [f"{num(F(fill * drain, fill + drain))} hours" if is_nice(F(fill * drain, fill + drain)) else f"{num(t + 3)} hours",
             f"{num(drain - fill)} hours", f"{num(t + 2)} hours", f"{num(t - 1)} hours"]
    return Item(
        f"Fill in {fill} h, empty in {drain} h",
        f"Pipe A fills a tank in {fill} hours and pipe B empties the full tank in {drain} hours. If both are opened together on an empty tank, how long will it take to fill?",
        f"{num(t)} hours", wrong,
        f"Net filling per hour = 1/{fill} − 1/{drain} = {F(1, fill) - F(1, drain)}. Time = 1 ÷ {F(1, fill) - F(1, drain)} = **{num(t)} hours**.",
        key=(fill, drain),
    )


def tw_three(rng):
    a, b, c = rng.sample([6, 8, 9, 10, 12, 15, 18, 20, 24, 30, 36, 40, 45, 60], 3)
    t = 1 / (F(1, a) + F(1, b) + F(1, c))
    need(is_nice(t, 1))
    wrong = [days(F(a + b + c, 3)), days(t + 1), days(t + 2), days(abs(t - 1)) if t > 1 else days(t + 3)]
    return Item(
        f"Three workers: {a}, {b} and {c} days",
        f"A, B and C can finish a job alone in {a}, {b} and {c} days respectively. How long will they take working together?",
        days(t), wrong,
        f"Together per day: 1/{a} + 1/{b} + 1/{c} = {F(1, a) + F(1, b) + F(1, c)}. Time = **{days(t)}**.",
        key=tuple(sorted((a, b, c))),
    )


def tw_efficiency(rng):
    k = rng.choice([2, 3, 4, F(3, 2), F(5, 2)])
    t = rng.choice([6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 24])
    # A is k times as efficient as B; together t days. A alone = t (k+1)/k
    a_alone = F(t) * (k + 1) / k
    need(is_nice(a_alone, 0))
    times = {2: "twice", 3: "three times", 4: "four times", F(3, 2): "one and a half times", F(5, 2): "two and a half times"}[k]
    wrong = [days(t * (k + 1)), days(F(t, 2)), days(a_alone + 3), days(a_alone - 2)]
    return Item(
        f"A is {times} as efficient; together in {t} days",
        f"A is {times} as efficient as B. Working together they finish a job in {t} days. How long would A alone take?",
        days(a_alone), wrong,
        f"""
        Let B do 1 unit a day, so A does {num(k)}; together {num(k + 1)} units a day. Work = {num(k + 1)} × {t} = {num((k + 1) * t)} units.
        A alone: {num((k + 1) * t)} / {num(k)} = **{days(a_alone)}**.
        """,
        key=(k, t),
    )


def tw_men_hours(rng):
    m1, d1, h1 = rng.choice([10, 12, 15, 16, 18, 20, 24]), rng.choice([6, 8, 9, 10, 12, 15]), rng.choice([6, 8, 9, 10])
    m2, h2 = rng.choice([8, 9, 10, 12, 15, 16, 18, 20, 24, 30]), rng.choice([6, 8, 9, 10, 12])
    work = rng.choice([1, 2, 3])
    d2 = F(m1 * d1 * h1 * work, m2 * h2)
    need(is_nice(d2, 0) and (m1, h1) != (m2, h2))
    task = {1: "a road 1 km long", 2: "a road 2 km long", 3: "a road 3 km long"}
    wrong = [days(F(m1 * d1 * h1, m2 * h2)) if work != 1 and is_nice(F(m1 * d1 * h1, m2 * h2)) else days(d2 + 2), days(d2 + 3), days(abs(d2 - 2)), days(d2 * 2)]
    return Item(
        f"{m1} men × {h1} h/day lay 1 km in {d1} days; {m2} men × {h2} h/day lay {work} km",
        f"{m1} men working {h1} hours a day can lay a road 1 km long in {d1} days. How many days will {m2} men working {h2} hours a day take to lay {task[work]}?",
        days(d2), wrong,
        f"""
        Work is proportional to men × days × hours: {m1} × {d1} × {h1} man-hours lay 1 km.
        {work} km needs {m1 * d1 * h1 * work} man-hours; per day the new team gives {m2} × {h2} = {m2 * h2}. Days = {m1 * d1 * h1 * work}/{m2 * h2} = **{days(d2)}**.
        """,
        key=(m1, d1, h1, m2, h2, work),
    )


def tw_alternate(rng):
    a, b = rng.sample([4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20], 2)
    # A works on day 1, B on day 2, ... simulate
    left, day = F(1), 0
    while left > 0:
        rate = F(1, a) if day % 2 == 0 else F(1, b)
        day += 1
        if rate >= left:
            total = day - 1 + left / rate
            break
        left -= rate
    need(is_nice(total, 1))
    wrong = [days(F(2 * a * b, a + b)) if is_nice(F(2 * a * b, a + b)) else days(total + 1), days(total + 1), days(abs(total - 1)), days(F(a * b, a + b)) if is_nice(F(a * b, a + b)) else days(total + 2)]
    return Item(
        f"Working on alternate days: {a} days and {b} days",
        f"A can finish a job in {a} days and B in {b} days. They work on alternate days, with A working on the first day. In how many days will the job be finished?",
        days(total), wrong,
        f"""
        Two days (A then B) complete 1/{a} + 1/{b} = {F(1, a) + F(1, b)} of the job. Count whole pairs of days, then finish the remainder with whoever works next.
        Simulating day by day, the work is completed after **{days(total)}**.
        """,
        key=tuple((a, b)),
    )


def tw_leak(rng):
    a, b = rng.sample([4, 5, 6, 8, 10, 12, 15, 20], 2)
    leak = rng.choice([6, 8, 10, 12, 15, 20, 24, 30, 40, 60])
    rate = F(1, a) + F(1, b) - F(1, leak)
    need(rate > 0)
    t = 1 / rate
    need(is_nice(t, 1))
    wrong = [f"{num(1 / (F(1, a) + F(1, b)))} hours" if is_nice(1 / (F(1, a) + F(1, b))) else f"{num(t + 2)} hours", f"{num(t + 1)} hours", f"{num(t + 3)} hours", f"{num(abs(t - 1))} hours"]
    return Item(
        f"Two filling pipes ({a} h, {b} h) and a leak ({leak} h)",
        f"Pipes A and B can fill a tank in {a} and {b} hours respectively. A leak at the bottom can empty the full tank in {leak} hours. If all three are working, how long will the empty tank take to fill?",
        f"{num(t)} hours", wrong,
        f"Net per hour = 1/{a} + 1/{b} − 1/{leak} = {rate}. Time = 1 ÷ {rate} = **{num(t)} hours**.",
        key=(tuple(sorted((a, b))), leak),
    )


def tw_wages(rng):
    a, b = rng.sample([6, 8, 9, 10, 12, 15, 18, 20, 24, 30], 2)
    wage = rng.randrange(1200, 12000, 100)
    share_a = wage * F(1, a) / (F(1, a) + F(1, b))
    need(is_nice(share_a, 0))
    wrong = [rupees(wage * F(a, a + b)), rupees(F(wage, 2)), rupees(share_a + 100), rupees(abs(share_a - 100))]
    return Item(
        f"Sharing {rupees(wage)} between {a}-day and {b}-day workers",
        f"A can do a job in {a} days and B in {b} days. They do it together and are paid {rupees(wage)} in all. What is A's fair share?",
        rupees(share_a), wrong,
        f"""
        Wages are shared in the ratio of work done, i.e. of daily rates 1/{a} : 1/{b} = {b} : {a}.
        A's share = {wage} × {b}/{a + b} = **{rupees(share_a)}**. (Sharing in the ratio {a} : {b} rewards the slower worker.)
        """,
        key=(a, b, wage),
    )


TIME_WORK = [
    Template("together", "easy", tw_together),
    Template("find-one", "easy", tw_find_one),
    Template("men-days", "easy", tw_men_days),
    Template("pipes", "easy", tw_pipes),
    Template("leaves", "medium", tw_leaves),
    Template("three", "medium", tw_three),
    Template("efficiency", "medium", tw_efficiency),
    Template("wages", "medium", tw_wages),
    Template("man-hours", "hard", tw_men_hours),
    Template("alternate", "hard", tw_alternate),
    Template("leak", "hard", tw_leak),
]

# ============================================================== SPEED, TIME AND DISTANCE


def kmh(x) -> str:
    return f"{num(x)} km/h"


def std_convert(rng):
    if rng.random() < 0.5:
        v = rng.choice(range(18, 199, 18))
        ms = F(v) * 5 / 18
        wrong = [f"{num(F(v) * 18 / 5)} m/s", f"{num(ms + 5)} m/s", f"{num(ms - 2)} m/s", f"{num(F(v, 3))} m/s" if is_nice(F(v, 3)) else f"{num(ms + 3)} m/s"]
        return Item(f"{v} km/h in m/s", f"A car travels at {v} km/h. What is its speed in metres per second?", f"{num(ms)} m/s", wrong,
                    f"1 km/h = 1000 m / 3600 s = 5/18 m/s. So {v} × 5/18 = **{num(ms)} m/s**.", key=("kmh", v))
    v = rng.choice(range(5, 61, 5))
    k = F(v) * 18 / 5
    need(is_nice(k))
    wrong = [kmh(F(v) * 5 / 18) if is_nice(F(v) * 5 / 18) else kmh(k + 9), kmh(k + 9), kmh(k - F(18, 5)) if is_nice(k - F(18, 5)) else kmh(k + 18), kmh(v * 3)]
    return Item(f"{v} m/s in km/h", f"A cheetah runs at {v} m/s. What is its speed in km/h?", kmh(k), wrong,
                f"Multiply by 18/5 to go from m/s to km/h: {v} × 18/5 = **{kmh(k)}**.", key=("ms", v))


def std_pole(rng):
    v = rng.choice([36, 45, 54, 60, 72, 90, 108, 126, 144])
    t = rng.choice([6, 8, 9, 10, 12, 15, 16, 18, 20])
    length = F(v) * 5 / 18 * t
    need(is_nice(length, 0))
    wrong = [f"{num(v * t)} m", f"{num(length + 20)} m", f"{num(length - 20)} m", f"{num(length * 2)} m"]
    return Item(f"Train at {v} km/h passes a pole in {t} s", f"A train running at {v} km/h passes a signal pole in {t} seconds. How long is the train?",
                f"{num(length)} m", wrong,
                f"Passing a pole, the train covers its own length. Speed = {v} × 5/18 = {num(F(v) * 5 / 18)} m/s; length = {num(F(v) * 5 / 18)} × {t} = **{num(length)} m**.",
                key=(v, t))


def std_platform(rng):
    v = rng.choice([36, 45, 54, 72, 90, 108])
    train, platform = rng.choice([100, 120, 150, 180, 200, 240, 250, 300]), rng.choice([150, 180, 200, 250, 300, 350, 400, 450])
    t = F(train + platform) / (F(v) * 5 / 18)
    need(is_nice(t))
    wrong = [f"{num(F(platform) / (F(v) * 5 / 18))} s" if is_nice(F(platform) / (F(v) * 5 / 18)) else f"{num(t + 5)} s",
             f"{num(F(train) / (F(v) * 5 / 18))} s" if is_nice(F(train) / (F(v) * 5 / 18)) else f"{num(t - 4)} s", f"{num(t + 6)} s", f"{num(t + 10)} s"]
    return Item(f"{train} m train, {platform} m platform at {v} km/h",
                f"A {train} m long train runs at {v} km/h. How long does it take to cross a {platform} m long platform completely?",
                f"{num(t)} s", wrong,
                f"It must cover its own length plus the platform: {train} + {platform} = {train + platform} m at {num(F(v) * 5 / 18)} m/s → **{num(t)} s**.",
                key=(v, train, platform))


def std_simple(rng):
    v = rng.choice([30, 36, 40, 45, 48, 50, 54, 60, 64, 72, 75, 80])
    t1 = rng.choice([F(3, 2), 2, F(5, 2), 3, 4, 5])
    d2 = rng.choice([90, 120, 150, 180, 200, 240, 300, 360])
    t2 = F(d2, v)
    need(is_nice(t2) and is_nice(v * t1, 0))
    hours = lambda x: f"{num(x)} hours" if x != 1 else "1 hour"
    wrong = [hours(t2 + F(1, 2)), hours(t2 + 1), hours(abs(t2 - F(1, 2))), hours(F(d2, v * t1))]
    return Item(f"{num(v * t1)} km in {num(t1)} h; how long for {d2} km?",
                f"A bus covers {num(v * t1)} km in {num(t1)} hours. At the same speed, how long will it take to cover {d2} km?",
                hours(t2), wrong,
                f"Speed = {num(v * t1)} / {num(t1)} = {v} km/h. Time for {d2} km = {d2}/{v} = **{hours(t2)}**.",
                key=(v, t1, d2))


def std_average(rng):
    x, y = rng.sample([20, 24, 30, 36, 40, 45, 48, 50, 60, 72, 80, 90, 120], 2)
    avg = F(2 * x * y, x + y)
    need(is_nice(avg))
    wrong = [kmh(F(x + y, 2)), kmh(avg + 2), kmh(avg - 2), kmh(F(x + y, 2) + 3)]
    return Item(f"Round trip at {x} and {y} km/h",
                f"A cyclist goes from home to college at {x} km/h and returns along the same route at {y} km/h. What is the average speed for the whole journey?",
                kmh(avg), wrong,
                f"""
                Average speed = total distance / total time — not the average of the speeds. For equal distances it is 2xy/(x + y) = 2 × {x} × {y}/{x + y} = **{kmh(avg)}**.
                """,
                key=tuple(sorted((x, y))))


def std_two_trains(rng):
    l1, l2 = rng.choice([100, 120, 150, 180, 200]), rng.choice([100, 130, 150, 180, 220, 250])
    v1, v2 = rng.sample([36, 40, 45, 50, 54, 60, 72, 90], 2)
    same = rng.random() < 0.5
    rel = F(abs(v1 - v2) if same else v1 + v2) * 5 / 18
    need(rel > 0 and is_nice(rel))
    t = F(l1 + l2) / rel
    need(is_nice(t))
    other = F(l1 + l2) / (F(v1 + v2 if same else abs(v1 - v2)) * 5 / 18) if v1 != v2 else None
    wrong = [f"{num(other)} s" if other and is_nice(other) else f"{num(t + 4)} s", f"{num(t + 2)} s", f"{num(abs(t - 3))} s", f"{num(t * 2)} s"]
    return Item(
        f"Trains of {l1} m and {l2} m, {v1} and {v2} km/h, {'same' if same else 'opposite'} direction",
        f"Two trains {l1} m and {l2} m long run on parallel tracks in {'the same direction' if same else 'opposite directions'} at {v1} km/h and {v2} km/h. How long do they take to cross each other completely?",
        f"{num(t)} s", wrong,
        f"""
        Relative speed = {f'{max(v1, v2)} − {min(v1, v2)}' if same else f'{v1} + {v2}'} = {num(rel * 18 / 5)} km/h = {num(rel)} m/s.
        Distance to clear = {l1} + {l2} = {l1 + l2} m, so time = {l1 + l2}/{num(rel)} = **{num(t)} s**.
        """,
        key=(l1, l2, tuple(sorted((v1, v2))), same),
    )


def std_boat(rng):
    boat, stream = rng.choice([8, 9, 10, 12, 15, 16, 18, 20]), rng.choice([2, 3, 4, 5])
    need(boat > stream)
    down, up = boat + stream, boat - stream
    from math import lcm

    d = lcm(down, up) * rng.choice([1, 2, 3])
    need(d <= 120)
    t_down, t_up = F(d, down), F(d, up)
    ask_stream = rng.random() < 0.5
    answer = kmh(stream if ask_stream else boat)
    wrong = [kmh(boat if ask_stream else stream), kmh((stream if ask_stream else boat) + 1), kmh((stream if ask_stream else boat) + 2), kmh(F(down, 2))]
    return Item(
        f"{d} km downstream in {num(t_down)} h, upstream in {num(t_up)} h ({'stream' if ask_stream else 'boat'})",
        f"A boat goes {d} km downstream in {num(t_down)} hours and the same distance upstream in {num(t_up)} hours. What is the speed of the {'stream' if ask_stream else 'boat in still water'}?",
        answer, wrong,
        f"""
        Downstream speed = {d}/{num(t_down)} = {down} km/h; upstream = {d}/{num(t_up)} = {up} km/h.
        Boat speed = ({down} + {up})/2 = {boat} km/h; stream speed = ({down} − {up})/2 = {stream} km/h. Answer: **{answer}**.
        """,
        key=(boat, stream, d, ask_stream),
    )


def std_late_early(rng):
    v1, v2 = rng.choice([(3, 4), (4, 5), (5, 6), (4, 6), (6, 8), (10, 12), (12, 15), (20, 25), (30, 40)])
    late, early = rng.choice([5, 6, 10, 12, 15]), rng.choice([5, 6, 10, 12, 15])
    d = F(late + early, 60) * v1 * v2 / (v2 - v1)
    need(is_nice(d))
    wrong = [f"{num(d + 1)} km", f"{num(d * 2)} km", f"{num(abs(d - 1))} km", f"{num(F(late + early, 60) * (v1 + v2))} km" if is_nice(F(late + early, 60) * (v1 + v2)) else f"{num(d + 2)} km"]
    return Item(
        f"{v1} km/h late by {late} min, {v2} km/h early by {early} min",
        f"Walking at {v1} km/h, Sana reaches her office {late} minutes late. Walking at {v2} km/h, she reaches {early} minutes early. How far is the office?",
        f"{num(d)} km", wrong,
        f"""
        The two journey times differ by {late} + {early} = {late + early} minutes = {num(F(late + early, 60))} h.
        d/{v1} − d/{v2} = {num(F(late + early, 60))} → d = {num(F(late + early, 60))} × {v1} × {v2}/({v2} − {v1}) = **{num(d)} km**.
        """,
        key=(v1, v2, late, early),
    )


def std_meeting(rng):
    d = rng.choice([100, 120, 150, 180, 200, 240, 280, 300, 360])
    va, vb = rng.sample([20, 25, 30, 36, 40, 45, 50, 60], 2)
    head = rng.choice([0, 1])  # hours A starts earlier
    remaining = d - va * head
    need(remaining > 0)
    t = F(remaining, va + vb)
    need(is_nice(t))
    dist_a = va * (head + t)
    need(is_nice(dist_a))
    wrong = [f"{num(F(d * va, va + vb))} km" if is_nice(F(d * va, va + vb)) and head else f"{num(dist_a + 10)} km", f"{num(d - dist_a)} km", f"{num(dist_a + 10)} km", f"{num(abs(dist_a - 10))} km"]
    start = "at the same time" if not head else "A starts at 8 a.m. and B at 9 a.m."
    return Item(
        f"Meeting point on a {d} km road ({va} and {vb} km/h{', A starts an hour earlier' if head else ''})",
        f"Towns P and Q are {d} km apart. A leaves P for Q at {va} km/h and B leaves Q for P at {vb} km/h; {start}. How far from P do they meet?",
        f"{num(dist_a)} km", wrong,
        f"""
        {'' if not head else f'By 9 a.m. A has covered {va} km, leaving {remaining} km. '}They close the gap at {va} + {vb} = {va + vb} km/h, so they meet {num(t)} h after {'starting' if not head else '9 a.m.'}.
        A has then travelled {va} × {num(head + t)} = **{num(dist_a)} km** from P.
        """,
        key=(d, va, vb, head),
    )


def std_boat_round_trip(rng):
    boat, stream = rng.choice([(9, 3), (10, 2), (12, 4), (15, 3), (15, 5), (18, 6), (20, 4), (8, 2), (11, 1)])
    d = rng.choice([24, 30, 36, 40, 45, 48, 60, 72, 80, 90])
    t = F(d, boat + stream) + F(d, boat - stream)
    need(is_nice(t))
    hours = lambda x: f"{num(x)} hours"
    wrong = [hours(F(2 * d, boat)), hours(t + 1), hours(abs(t - 1)), hours(t + 2)]
    return Item(
        f"Round trip of {d} km each way, boat {boat} km/h, stream {stream} km/h",
        f"A motorboat's speed in still water is {boat} km/h and the river flows at {stream} km/h. How long does it take to go {d} km downstream and come back?",
        hours(t), wrong,
        f"Downstream {boat + stream} km/h: {d}/{boat + stream} = {num(F(d, boat + stream))} h. Upstream {boat - stream} km/h: {d}/{boat - stream} = {num(F(d, boat - stream))} h. Total **{hours(t)}** (not 2 × {d}/{boat} — the current doesn't cancel out).",
        key=(boat, stream, d),
    )


def std_train_man(rng):
    v_train = rng.choice([45, 54, 63, 72, 81, 90])
    v_man = rng.choice([3, 4, 5, 6, 9])
    same = rng.random() < 0.6
    t = rng.choice([8, 9, 10, 12, 15, 18, 20])
    rel = F(v_train - v_man if same else v_train + v_man) * 5 / 18
    need(is_nice(rel))
    length = rel * t
    need(is_nice(length, 0))
    other = F(v_train + v_man if same else v_train - v_man) * 5 / 18 * t
    wrong = [f"{num(other)} m" if is_nice(other) else f"{num(length + 25)} m", f"{num(F(v_train) * 5 / 18 * t)} m" if is_nice(F(v_train) * 5 / 18 * t) else f"{num(length - 20)} m", f"{num(length + 20)} m", f"{num(length - 25)} m"]
    return Item(
        f"Train at {v_train} km/h passes a man walking {'with' if same else 'towards'} it at {v_man} km/h in {t} s",
        f"A train running at {v_train} km/h passes a man walking at {v_man} km/h {'in the same direction as the train' if same else 'towards the train'} in {t} seconds. How long is the train?",
        f"{num(length)} m", wrong,
        f"Relative speed = {v_train} {'−' if same else '+'} {v_man} = {num(rel * 18 / 5)} km/h = {num(rel)} m/s. Length = {num(rel)} × {t} = **{num(length)} m**.",
        key=(v_train, v_man, same, t),
    )


SPEED = [
    Template("convert", "easy", std_convert),
    Template("pole", "easy", std_pole),
    Template("platform", "easy", std_platform),
    Template("bus", "easy", std_simple),
    Template("average", "medium", std_average),
    Template("two-trains", "medium", std_two_trains),
    Template("boat", "medium", std_boat),
    Template("late-early", "medium", std_late_early),
    Template("meeting", "hard", std_meeting),
    Template("round-trip", "hard", std_boat_round_trip),
    Template("train-man", "hard", std_train_man),
]

# ============================================================== AVERAGES


def avg_list(rng):
    n = rng.choice([5, 6, 7, 8])
    values = rng.sample(range(11, 99), n)
    total = sum(values)
    need(total % n == 0)
    mean = F(total, n)
    wrong = [num(mean + 1), num(mean - 1), num(F(total, n + 1)) if is_nice(F(total, n + 1)) else num(mean + 2), num(F(min(values) + max(values), 2)) if F(min(values) + max(values), 2) != mean else num(mean + 3)]
    return Item(f"Average of {', '.join(map(str, values))}", f"Find the average of {', '.join(map(str, values))}.", num(mean), wrong,
                f"Sum = {total}; there are {n} numbers, so the average is {total}/{n} = **{num(mean)}**.", key=tuple(sorted(values)))


def avg_removed(rng):
    n, a = rng.choice([5, 6, 7, 8, 9, 10, 12]), rng.randrange(15, 60)
    b = rng.randrange(a - 6, a + 6)
    need(b != a)
    removed = n * a - (n - 1) * b
    need(removed > 0)
    wrong = [num(abs(a - b) * n), num(removed + n), num(abs(removed - n)), num(a + b)]
    return Item(f"Removing one of {n} numbers: average {a} → {b}",
                f"The average of {n} numbers is {a}. When one number is removed, the average of the remaining numbers becomes {b}. What number was removed?",
                num(removed), wrong,
                f"Total before = {n} × {a} = {n * a}. Total after = {n - 1} × {b} = {(n - 1) * b}. Removed number = {n * a} − {(n - 1) * b} = **{removed}**.",
                key=(n, a, b))


def avg_joins(rng):
    n, a = rng.choice([10, 12, 15, 20, 24, 30]), rng.randrange(12, 40)
    inc = rng.choice([1, F(1, 2), 2, 3])
    new = (n + 1) * (a + inc) - n * a
    need(is_nice(new, 0))
    wrong = [num(a + inc), num(new - n * inc) if new - n * inc > 0 else num(new + 5), num(new + inc * 2), num(a + n)]
    return Item(f"Teacher joins {n} students: average {a} rises by {num(inc)}",
                f"The average age of {n} students is {a} years. When the teacher's age is included, the average rises by {num(inc)} year{'s' if inc != 1 else ''}. How old is the teacher?",
                f"{num(new)} years", [f"{w} years" for w in wrong],
                f"New total = {n + 1} × {num(a + inc)} = {num((n + 1) * (a + inc))}. Old total = {n} × {a} = {n * a}. Teacher = {num((n + 1) * (a + inc))} − {n * a} = **{num(new)} years**.",
                key=(n, a, inc))


def avg_consecutive(rng):
    kind = rng.choice(["odd", "even", "whole"])
    n = rng.choice([5, 7, 9, 6, 8])
    first = rng.randrange(5, 80)
    step = 1 if kind == "whole" else 2
    if kind == "odd" and first % 2 == 0:
        first += 1
    if kind == "even" and first % 2 == 1:
        first += 1
    values = [first + step * i for i in range(n)]
    mean = F(sum(values), n)
    ask_largest = rng.random() < 0.5
    answer = values[-1] if ask_largest else values[0]
    wrong = [num(values[-2] if ask_largest else values[1]), num(answer + step), num(mean + n) if is_nice(mean) else num(answer + 2 * step), num(answer - 2 * step)]
    label = {"odd": "consecutive odd numbers", "even": "consecutive even numbers", "whole": "consecutive whole numbers"}[kind]
    return Item(
        f"{n} {label} averaging {num(mean)}",
        f"The average of {n} {label} is {num(mean)}. What is the {'largest' if ask_largest else 'smallest'} of them?",
        num(answer), wrong,
        f"""
        Consecutive numbers are evenly spaced, so the average sits in the middle. With {n} numbers {step} apart,
        the {'largest' if ask_largest else 'smallest'} is {num(mean)} {'+' if ask_largest else '−'} {num(F(n - 1, 2) * step)} = **{num(answer)}**.
        """,
        key=(kind, n, first, ask_largest),
    )


def avg_batting(rng):
    n, a = rng.choice([10, 12, 15, 16, 18, 20, 24]), rng.randrange(25, 60)
    rise = rng.choice([1, 2, 3, 4])
    needed = (n + 1) * (a + rise) - n * a
    wrong = [num(a + rise), num(needed - rise), num(needed + rise), num(a + n * rise)]
    return Item(f"Raising a batting average from {a} to {a + rise} after {n} innings",
                f"A batter's average after {n} innings is {a}. How many runs must they score in the next innings to raise the average to {a + rise}?",
                num(needed), wrong,
                f"Runs needed after {n + 1} innings: {n + 1} × {a + rise} = {(n + 1) * (a + rise)}. Runs so far: {n} × {a} = {n * a}. Next innings = **{needed}**.",
                key=(n, a, rise))


def avg_combined(rng):
    n1, n2 = rng.choice([20, 25, 30, 40, 50]), rng.choice([20, 30, 40, 50, 60])
    a1, a2 = rng.randrange(40, 80), rng.randrange(40, 80)
    mean = F(n1 * a1 + n2 * a2, n1 + n2)
    need(is_nice(mean) and a1 != a2)
    wrong = [num(F(a1 + a2, 2)) if F(a1 + a2, 2) != mean else num(mean + 1), num(mean + 1), num(mean - 1), num(mean + 2)]
    return Item(f"Combined average of sections ({n1} @ {a1}, {n2} @ {a2})",
                f"Section A has {n1} students with an average score of {a1}; section B has {n2} students averaging {a2}. What is the average score of all {n1 + n2} students?",
                num(mean), wrong,
                f"Combined total = {n1} × {a1} + {n2} × {a2} = {n1 * a1 + n2 * a2}. Average = {n1 * a1 + n2 * a2}/{n1 + n2} = **{num(mean)}** — weighted, not ({a1} + {a2})/2.",
                key=(n1, a1, n2, a2))


def avg_replacement(rng):
    n = rng.choice([6, 8, 10, 12, 15, 20])
    old = rng.randrange(45, 75)
    inc = rng.choice([F(1, 2), 1, F(3, 2), 2, F(5, 2), 3])
    new = old + n * inc
    need(is_nice(new, 0))
    wrong = [f"{num(old + inc)} kg", f"{num(new + inc)} kg", f"{num(old + (n - 1) * inc)} kg", f"{num(new + 5)} kg"]
    return Item(f"Replacing a {old} kg member raises the average of {n} by {num(inc)} kg",
                f"The average weight of {n} people increases by {num(inc)} kg when one of them, who weighs {old} kg, is replaced by a new person. What is the new person's weight?",
                f"{num(new)} kg", wrong,
                f"The total rises by {n} × {num(inc)} = {num(n * inc)} kg, all due to the newcomer: {old} + {num(n * inc)} = **{num(new)} kg**.",
                key=(n, old, inc))


def avg_first_multiples(rng):
    k, n = rng.choice([3, 4, 5, 6, 7, 8, 9, 11, 12]), rng.choice([8, 10, 12, 15, 20, 25])
    mean = F(k * (n + 1), 2)
    need(is_nice(mean))
    wrong = [num(F(k * n, 2)), num(mean + k), num(k * n), num(mean - 1)]
    return Item(f"Average of the first {n} multiples of {k}",
                f"What is the average of the first {n} multiples of {k}?",
                num(mean), wrong,
                f"The multiples {k}, {2 * k}, …, {k * n} are evenly spaced, so the average is (first + last)/2 = ({k} + {k * n})/2 = **{num(mean)}**.",
                key=(k, n))


def avg_misread(rng):
    n = rng.choice([10, 12, 15, 20, 25, 30, 40, 50])
    wrong_avg = rng.randrange(30, 80)
    actual, read = rng.randrange(20, 99), rng.randrange(20, 99)
    need(actual != read)
    correct = F(n * wrong_avg - read + actual, n)
    need(is_nice(correct))
    wrong = [num(wrong_avg + F(read - actual, n)) if is_nice(wrong_avg + F(read - actual, n)) and wrong_avg + F(read - actual, n) != correct else num(correct + 1),
             num(correct + 1), num(abs(correct - 2)), num(wrong_avg + actual - read) if wrong_avg + actual - read > 0 else num(correct + 3)]
    return Item(f"Average of {n} numbers: {actual} misread as {read}",
                f"The average of {n} numbers was calculated as {wrong_avg}. It was later found that the number {actual} had been read as {read}. What is the correct average?",
                num(correct), wrong,
                f"Wrong total = {n} × {wrong_avg} = {n * wrong_avg}. Correct total = {n * wrong_avg} − {read} + {actual} = {n * wrong_avg - read + actual}. Correct average = **{num(correct)}**.",
                key=(n, wrong_avg, actual, read))


def avg_three(rng):
    a, b, c = rng.randrange(20, 90), rng.randrange(20, 90), rng.randrange(20, 90)
    s_all, s_ab, s_bc = F(a + b + c, 3), F(a + b, 2), F(b + c, 2)
    need(all(is_nice(x) for x in (s_all, s_ab, s_bc)))
    wrong = [num(a), num(c), num(b + 2), num(abs(b - 3))]
    return Item(f"Average of A, B, C is {num(s_all)}; A, B is {num(s_ab)}; B, C is {num(s_bc)}",
                f"The average weight of A, B and C is {num(s_all)} kg. The average of A and B is {num(s_ab)} kg and that of B and C is {num(s_bc)} kg. What is B's weight (in kg)?",
                num(b), wrong,
                f"A + B + C = {num(3 * s_all)}; A + B = {num(2 * s_ab)}; B + C = {num(2 * s_bc)}. Adding the last two counts B twice: B = {num(2 * s_ab)} + {num(2 * s_bc)} − {num(3 * s_all)} = **{b}**.",
                key=(a, b, c))


def avg_excluding(rng):
    n = rng.choice([11, 15, 20, 25, 30])
    a = rng.randrange(30, 70)
    k = rng.choice([2, 3, 4, 5])
    b = rng.randrange(a - 8, a + 8)
    excluded_total = n * a - (n - k) * b
    need(excluded_total > 0 and excluded_total % k == 0 and b != a)
    each = excluded_total // k
    wrong = [num(excluded_total), num(each + k), num(abs(each - k)), num(a + b)]
    return Item(f"Excluding {k} of {n} values changes the average from {a} to {b}",
                f"The average of {n} results is {a}. If {k} results, all equal, are left out, the average of the rest is {b}. What is the value of each excluded result?",
                num(each), wrong,
                f"Total of all = {n} × {a} = {n * a}. Total of the rest = {n - k} × {b} = {(n - k) * b}. Excluded total = {excluded_total}, so each = {excluded_total}/{k} = **{each}**.",
                key=(n, a, k, b))


AVERAGES = [
    Template("list", "easy", avg_list),
    Template("removed", "easy", avg_removed),
    Template("joins", "easy", avg_joins),
    Template("multiples", "easy", avg_first_multiples),
    Template("consecutive", "medium", avg_consecutive),
    Template("batting", "medium", avg_batting),
    Template("combined", "medium", avg_combined),
    Template("replacement", "medium", avg_replacement),
    Template("misread", "hard", avg_misread),
    Template("three", "hard", avg_three),
    Template("excluding", "hard", avg_excluding),
]

# ============================================================== RATIO AND PROPORTION


def rp_share(rng):
    a, b = rng.choice([(2, 3), (3, 4), (3, 5), (4, 5), (5, 7), (2, 5), (7, 8), (5, 6), (4, 7)])
    total = (a + b) * rng.randrange(50, 1500, 10)
    ask_a = rng.random() < 0.5
    share = F(total * (a if ask_a else b), a + b)
    other = total - share
    who = "A" if ask_a else "B"
    wrong = [rupees(other), rupees(F(total, 2)), rupees(share + (a + b) * 10), rupees(abs(share - (a + b) * 10))]
    return Item(f"Dividing {rupees(total)} in the ratio {a} : {b} ({who}'s share)",
                f"{rupees(total)} is divided between A and B in the ratio {a} : {b}. What is {who}'s share?",
                rupees(share), wrong,
                f"Total parts = {a} + {b} = {a + b}; one part = {num(total)}/{a + b} = {num(F(total, a + b))}. {who}'s share = {a if ask_a else b} × {num(F(total, a + b))} = **{rupees(share)}**.",
                key=(a, b, total, ask_a))


def rp_proportional(rng):
    if rng.random() < 0.5:
        a, b, c = rng.randrange(2, 20), rng.randrange(3, 40), rng.randrange(3, 40)
        d = F(b * c, a)
        need(is_nice(d, 0))
        wrong = [num(F(a * c, b)) if is_nice(F(a * c, b)) else num(d + 3), num(d + 2), num(abs(d - 3)), num(a + b + c)]
        return Item(f"Fourth proportional to {a}, {b} and {c}", f"Find the fourth proportional to {a}, {b} and {c}.", num(d), wrong,
                    f"a : b = c : d → d = b × c / a = {b} × {c}/{a} = **{num(d)}**.", key=("fourth", a, b, c))
    m = rng.randrange(2, 30)
    a = rng.choice([x for x in range(1, m * m + 1) if (m * m) % x == 0 and x < m])
    b = m * m // a
    wrong = [num(F(a + b, 2)) if is_nice(F(a + b, 2)) else num(m + 2), num(m + 1), num(m * 2), num(abs(m - 1))]
    return Item(f"Mean proportional between {a} and {b}", f"Find the mean proportional between {a} and {b}.", num(m), wrong,
                f"The mean proportional x satisfies a : x = x : b, so x = √(ab) = √{a * b} = **{m}**.", key=("mean", a, b))


def rp_combine(rng):
    a, b = rng.randrange(1, 9), rng.randrange(1, 9)
    c, d = rng.randrange(1, 9), rng.randrange(1, 9)
    from math import gcd

    l = b * c // gcd(b, c)
    A, B, C = a * l // b, l, d * l // c
    g = gcd(gcd(A, B), C)
    A, B, C = A // g, B // g, C // g
    need(len({A, B, C}) == 3 and (a, b) != (c, d) and gcd(a, b) == 1 and gcd(c, d) == 1)
    answer = f"{A} : {B} : {C}"
    wrong = [f"{a} : {b * c} : {d}" if f"{a} : {b * c} : {d}" != answer else f"{A + 1} : {B} : {C}", f"{A} : {C} : {B}", f"{a} : {b} : {d}", f"{C} : {B} : {A}"]
    return Item(f"A : B = {a} : {b} and B : C = {c} : {d}", f"If A : B = {a} : {b} and B : C = {c} : {d}, find A : B : C.", answer, wrong,
                f"Make B the same in both: B appears as {b} and {c}; use their LCM {l}. A : B = {a * l // b} : {l} and B : C = {l} : {d * l // c}. So A : B : C = **{answer}**.",
                key=(a, b, c, d))


def rp_mixture(rng):
    m, w = rng.choice([(3, 1), (4, 1), (5, 2), (7, 3), (2, 1), (5, 3), (3, 2)])
    total = (m + w) * rng.choice([4, 5, 6, 8, 10, 12])
    m2, w2 = rng.choice([(3, 2), (1, 1), (2, 1), (4, 3), (5, 4), (3, 4), (5, 3)])
    milk, water = F(total * m, m + w), F(total * w, m + w)
    added = milk * w2 / m2 - water
    need(added > 0 and is_nice(added))
    wrong = [f"{num(added + 2)} litres", f"{num(added * 2)} litres", f"{num(abs(added - 2))} litres", f"{num(F(total * w2, m2 + w2))} litres" if is_nice(F(total * w2, m2 + w2)) else f"{num(added + 4)} litres"]
    return Item(f"{total} L of milk : water = {m} : {w} → {m2} : {w2}",
                f"A {total}-litre mixture contains milk and water in the ratio {m} : {w}. How much water must be added to make the ratio {m2} : {w2}?",
                f"{num(added)} litres", wrong,
                f"Milk = {num(milk)} L and water = {num(water)} L. Milk doesn't change, so the new water must be {num(milk)} × {w2}/{m2} = {num(milk * w2 / m2)} L. Add {num(milk * w2 / m2)} − {num(water)} = **{num(added)} litres**.",
                key=(m, w, total, m2, w2))


def rp_ages(rng):
    a, b = rng.randrange(6, 50), rng.randrange(6, 50)
    need(a != b)
    k = rng.choice([4, 5, 6, 8, 10])
    from math import gcd

    def r(x, y):
        g = gcd(x, y)
        return x // g, y // g

    now, before = r(a, b), r(a - k, b - k)
    need(now != before and a - k > 0 and b - k > 0 and max(now) < 15 and max(before) < 15)
    wrong = [f"{a + k} years", f"{b} years", f"{a - k} years", f"{a + 2} years"]
    return Item(f"Ages {now[0]} : {now[1]} now, {before[0]} : {before[1]} {k} years ago",
                f"The ratio of the present ages of A and B is {now[0]} : {now[1]}. {k} years ago the ratio was {before[0]} : {before[1]}. What is A's present age?",
                f"{a} years", wrong,
                f"""
                Let the ages be {now[0]}x and {now[1]}x. Then ({now[0]}x − {k}) : ({now[1]}x − {k}) = {before[0]} : {before[1]}.
                Cross-multiplying: {before[1]}({now[0]}x − {k}) = {before[0]}({now[1]}x − {k}) → x = {num(F(a, now[0]))}. A = {now[0]} × {num(F(a, now[0]))} = **{a} years**.
                """,
                key=(a, b, k))


def rp_income_savings(rng):
    i1, i2 = rng.choice([(3, 4), (4, 5), (5, 7), (2, 3), (5, 6), (7, 9)])
    e1, e2 = rng.choice([(2, 3), (3, 4), (4, 5), (5, 7), (1, 2), (3, 5)])
    s = rng.randrange(1000, 20000, 500)
    # i1 x - e1 y = s ; i2 x - e2 y = s  → solve
    det = i1 * (-e2) - (-e1) * i2
    need(det != 0)
    x = F(s * (-e2) - (-e1) * s, det)
    y = F(i1 * s - i2 * s, det)
    need(x > 0 and y > 0 and is_nice(x, 0) and is_nice(y, 0))
    inc_a = i1 * x
    wrong = [rupees(i2 * x), rupees(inc_a + 1000), rupees(e1 * y), rupees(abs(inc_a - 1000))]
    return Item(f"Incomes {i1} : {i2}, expenses {e1} : {e2}, each saves {rupees(s)}",
                f"The incomes of P and Q are in the ratio {i1} : {i2} and their expenses are in the ratio {e1} : {e2}. If each saves {rupees(s)} a month, what is P's monthly income?",
                rupees(inc_a), wrong,
                f"""
                Let incomes be {i1}x, {i2}x and expenses {e1}y, {e2}y. Then {i1}x − {e1}y = {s} and {i2}x − {e2}y = {s}.
                Solving: x = {num(x)}, y = {num(y)}. P's income = {i1} × {num(x)} = **{rupees(inc_a)}**.
                """,
                key=(i1, i2, e1, e2, s))


def rp_coins(rng):
    r1, r2, r3 = rng.choice([(1, 2, 4), (2, 3, 4), (1, 2, 3), (3, 4, 5), (2, 3, 5), (5, 6, 8)])
    k = rng.randrange(5, 60)
    value = F(r1 * k) * 1 + F(r2 * k) * F(1, 2) + F(r3 * k) * F(1, 4)
    need(is_nice(value, 0))
    fifty = r2 * k
    wrong = [str(r1 * k), str(r3 * k), str(fifty + r2), str(abs(fifty - r2))]
    return Item(f"Coins of ₹1, 50p and 25p in the ratio {r1} : {r2} : {r3} worth {rupees(value)}",
                f"A bag contains ₹1, 50-paise and 25-paise coins in the ratio {r1} : {r2} : {r3}. The total value is {rupees(value)}. How many 50-paise coins are there?",
                str(fifty), wrong,
                f"""
                Let the counts be {r1}k, {r2}k, {r3}k. Value = {r1}k × 1 + {r2}k × 0.5 + {r3}k × 0.25 = {num(F(r1) + F(r2, 2) + F(r3, 4))}k.
                {num(F(r1) + F(r2, 2) + F(r3, 4))}k = {num(value)} → k = {k}. 50-paise coins = {r2} × {k} = **{fifty}**.
                """,
                key=(r1, r2, r3, k))


def rp_partnership(rng):
    a, b = rng.randrange(10, 90, 5) * 1000, rng.randrange(10, 90, 5) * 1000
    ma, mb = 12, rng.choice([4, 6, 8, 9, 10])
    profit = rng.randrange(6000, 90000, 1000)
    share_b = F(profit * b * mb, a * ma + b * mb)
    need(is_nice(share_b, 0))
    wrong = [rupees(F(profit * b, a + b)) if is_nice(F(profit * b, a + b)) else rupees(share_b + 500), rupees(profit - share_b), rupees(share_b + 1000), rupees(abs(share_b - 1000))]
    return Item(f"Partnership: {rupees(a)} for 12 months vs {rupees(b)} for {mb} months",
                f"A starts a business with {rupees(a)}. After {12 - mb} months B joins with {rupees(b)}. Out of a year-end profit of {rupees(profit)}, what is B's share?",
                rupees(share_b), wrong,
                f"""
                Profit is shared in the ratio of capital × time: A = {num(a)} × 12 = {num(a * 12)}, B = {num(b)} × {mb} = {num(b * mb)}.
                B's share = {num(profit)} × {num(b * mb)}/{num(a * 12 + b * mb)} = **{rupees(share_b)}**.
                """,
                key=(a, b, mb, profit))


def rp_alligation(rng):
    p1, p2 = sorted(rng.sample([20, 24, 28, 30, 32, 36, 40, 45, 48, 50, 60], 2))
    mean = rng.randrange(p1 + 1, p2)
    from math import gcd

    x, y = p2 - mean, mean - p1
    g = gcd(x, y)
    answer = f"{x // g} : {y // g}"

    def reduced(u, v):
        h = gcd(u, v)
        return f"{u // h} : {v // h}"

    wrong = [reduced(y, x), reduced(p1, p2), reduced(x // g + 1, y // g), reduced(x // g, y // g + 1), "1 : 1"]
    return Item(f"Mixing ₹{p1}/kg and ₹{p2}/kg rice to get ₹{mean}/kg",
                f"In what ratio must rice at ₹{p1} per kg be mixed with rice at ₹{p2} per kg so that the mixture is worth ₹{mean} per kg?",
                answer, wrong,
                f"""
                Alligation: cheaper : dearer = (dearer − mean) : (mean − cheaper) = ({p2} − {mean}) : ({mean} − {p1}) = {x} : {y} = **{answer}**.
                Check: ({x // g} × {p1} + {y // g} × {p2})/{x // g + y // g} = {num(F(x // g * p1 + y // g * p2, x // g + y // g))}.
                """,
                key=(p1, p2, mean))


def rp_replacement(rng):
    vol = rng.choice([40, 50, 60, 80, 100, 120])
    take = rng.choice([4, 5, 6, 8, 10, 12, 15, 20])
    n = rng.choice([2, 3])
    need(take < vol)
    left = vol * (F(vol - take, vol) ** n)
    need(is_nice(left))
    wrong = [f"{num(vol - n * take)} litres", f"{num(left + 1)} litres", f"{num(abs(left - 2))} litres", f"{num(vol * F(vol - take, vol))} litres"]
    return Item(f"{take} L of {vol} L milk replaced by water, {n} times",
                f"A container holds {vol} litres of milk. {take} litres are taken out and replaced with water; this is done {n} times in all. How much milk is left?",
                f"{num(left)} litres", wrong,
                f"Each replacement keeps ({vol} − {take})/{vol} = {F(vol - take, vol)} of the milk. After {n} times: {vol} × ({F(vol - take, vol)})^{n} = **{num(left)} litres**.",
                key=(vol, take, n))


RATIO = [
    Template("share", "easy", rp_share),
    Template("proportional", "easy", rp_proportional),
    Template("combine", "easy", rp_combine),
    Template("mixture", "medium", rp_mixture),
    Template("ages", "medium", rp_ages),
    Template("coins", "medium", rp_coins),
    Template("alligation", "medium", rp_alligation),
    Template("income", "hard", rp_income_savings),
    Template("partnership", "hard", rp_partnership),
    Template("replacement", "hard", rp_replacement),
]

# ============================================================== INTEREST


def years(n) -> str:
    return f"{num(n)} year{'s' if n != 1 else ''}"


def si_basic(rng):
    p, r, t = rng.randrange(2000, 50000, 500), rng.choice([4, 5, 6, 7, 8, 9, 10, 12, 15]), rng.choice([2, 3, 4, 5, 6])
    si = F(p * r * t, 100)
    need(is_nice(si, 0))
    ci = p * (F(100 + r, 100) ** t) - p
    wrong = [rupees(ci) if is_nice(ci) else rupees(si + 100), rupees(p + si), rupees(F(p * r, 100)), rupees(si + p // 100)]
    return Item(f"Simple interest on {rupees(p)} at {r}% for {t} years",
                f"What is the simple interest on {rupees(p)} at {r}% per annum for {t} years?",
                rupees(si), wrong, f"SI = P × R × T/100 = {num(p)} × {r} × {t}/100 = **{rupees(si)}**.", key=(p, r, t))


def ci_basic(rng):
    p, r = rng.randrange(1000, 40000, 1000), rng.choice([5, 10, 15, 20, 4, 8, 12])
    t = rng.choice([2, 3]) if r in (10, 20, 5) else 2
    ci = p * (F(100 + r, 100) ** t) - p
    need(is_nice(ci))
    si = F(p * r * t, 100)
    wrong = [rupees(si), rupees(ci + p), rupees(ci + 50), rupees(ci - 25)]
    return Item(f"Compound interest on {rupees(p)} at {r}% for {t} years",
                f"What is the compound interest on {rupees(p)} at {r}% per annum for {t} years, compounded annually?",
                rupees(ci), wrong,
                f"Amount = {num(p)} × (1 + {r}/100)^{t} = {num(p * (F(100 + r, 100) ** t))}. CI = amount − principal = **{rupees(ci)}**.",
                key=(p, r, t))


def si_multiply(rng):
    k = rng.choice([2, 3, 4])
    t = rng.choice([4, 5, 6, 8, 10, 12, 16, 20, 25])
    r = F(100 * (k - 1), t)
    need(is_nice(r))
    word = {2: "double", 3: "triple", 4: "become four times"}[k]
    wrong = [pct(F(100 * k, t)) if is_nice(F(100 * k, t)) else pct(r + 5), pct(r + 2), pct(abs(r - 2)), pct(F(100, t) if k != 2 else r * 2)]
    return Item(f"Rate for money to {word} in {t} years (SI)",
                f"At what rate of simple interest will a sum of money {word} in {t} years?",
                pct(r), wrong,
                f"To {word}, the interest must equal {k - 1} × the principal: P × R × {t}/100 = {k - 1}P → R = {100 * (k - 1)}/{t} = **{pct(r)}**.",
                key=(k, t))


def si_principal(rng):
    p, r, t = rng.randrange(1000, 40000, 500), rng.choice([4, 5, 6, 8, 10, 12, 15]), rng.choice([2, 3, 4, 5])
    si = F(p * r * t, 100)
    need(is_nice(si, 0))
    wrong = [rupees(si * 100 / (r + t)) if is_nice(si * 100 / (r + t), 0) else rupees(p + 500), rupees(p + 1000), rupees(p - 500), rupees(si * t)]
    return Item(f"Principal earning {rupees(si)} at {r}% in {t} years",
                f"A sum earns {rupees(si)} as simple interest in {t} years at {r}% per annum. What is the sum?",
                rupees(p), wrong, f"P = SI × 100/(R × T) = {num(si)} × 100/({r} × {t}) = **{rupees(p)}**.", key=(p, r, t))


def ci_si_difference(rng):
    p, r = rng.randrange(1000, 50000, 1000), rng.choice([4, 5, 6, 8, 10, 12, 15, 20])
    diff = p * F(r * r, 10000)
    need(is_nice(diff))
    check = p * F(100 + r, 100) ** 2 - p - F(p * r * 2, 100)
    assert check == diff
    wrong = [rupees(diff * 2), rupees(F(p * r, 100)), rupees(diff + 10), rupees(diff * r)]
    return Item(f"CI − SI on {rupees(p)} at {r}% for 2 years",
                f"What is the difference between compound interest and simple interest on {rupees(p)} at {r}% per annum for 2 years?",
                rupees(diff), wrong,
                f"For 2 years the difference is the interest earned on the first year's interest: P(R/100)² = {num(p)} × ({r}/100)² = **{rupees(diff)}**.",
                key=(p, r))


def si_rate_from_amount(rng):
    p, r, t = rng.randrange(2000, 30000, 500), rng.choice([4, 5, 6, 7, 8, 9, 10, 12]), rng.choice([2, 3, 4, 5, 6])
    amount = p + F(p * r * t, 100)
    need(is_nice(amount, 0))
    wrong = [pct(r + 1), pct(r - 1), pct(r * 2), pct(F(amount - p, p) * 100) if is_nice(F(amount - p, p) * 100) and F(amount - p, p) * 100 != r else pct(r + 2)]
    return Item(f"{rupees(p)} becomes {rupees(amount)} in {t} years (SI rate)",
                f"A sum of {rupees(p)} amounts to {rupees(amount)} in {t} years at simple interest. What is the rate per annum?",
                pct(r), wrong,
                f"Interest = {num(amount)} − {num(p)} = {num(amount - p)}. R = SI × 100/(P × T) = {num(amount - p)} × 100/({num(p)} × {t}) = **{pct(r)}**.",
                key=(p, r, t))


def ci_half_yearly(rng):
    p, r = rng.randrange(2000, 40000, 1000), rng.choice([8, 10, 12, 16, 20])
    amount = p * F(100 + F(r, 2), 100) ** 2
    ci = amount - p
    need(is_nice(ci))
    annual = F(p * r, 100)
    wrong = [rupees(annual), rupees(ci + 20), rupees(ci - 10), rupees(ci + p * F(1, 100))]
    return Item(f"{rupees(p)} at {r}% compounded half-yearly for 1 year",
                f"Find the compound interest on {rupees(p)} for 1 year at {r}% per annum, compounded half-yearly.",
                rupees(ci), wrong,
                f"Half-yearly: rate {num(F(r, 2))}% per period, 2 periods. Amount = {num(p)} × (1 + {num(F(r, 2))}/100)² = {num(amount)}. CI = **{rupees(ci)}** (a little more than the {rupees(annual)} from annual compounding).",
                key=(p, r))


def si_two_amounts(rng):
    p, r = rng.randrange(1000, 20000, 500), rng.choice([4, 5, 6, 8, 10, 12])
    t1, t2 = sorted(rng.sample([2, 3, 4, 5, 6, 7, 8], 2))
    a1, a2 = p + F(p * r * t1, 100), p + F(p * r * t2, 100)
    need(is_nice(a1, 0) and is_nice(a2, 0))
    ask_rate = rng.random() < 0.5
    answer = pct(r) if ask_rate else rupees(p)
    wrong = [pct(r + 1), pct(r + 2), pct(abs(r - 1)), pct(r * 2)] if ask_rate else [rupees(p + 500), rupees(abs(p - 500)), rupees(a1 - (a2 - a1)), rupees(p + 1000)]
    return Item(f"{rupees(a1)} after {t1} years, {rupees(a2)} after {t2} years ({'rate' if ask_rate else 'sum'})",
                f"A sum of money at simple interest amounts to {rupees(a1)} in {t1} years and to {rupees(a2)} in {t2} years. What is the {'rate of interest' if ask_rate else 'sum'}?",
                answer, wrong,
                f"""
                The extra {t2 - t1} years earn {num(a2)} − {num(a1)} = {num(a2 - a1)}, i.e. {num(F(a2 - a1, t2 - t1))} a year.
                Principal = {num(a1)} − {t1} × {num(F(a2 - a1, t2 - t1))} = {rupees(p)}; rate = {num(F(a2 - a1, t2 - t1))}/{num(p)} × 100 = {pct(r)}. Answer: **{answer}**.
                """,
                key=(p, r, t1, t2, ask_rate))


def ci_si_three_years(rng):
    p, r = rng.randrange(1000, 50000, 1000), rng.choice([5, 10, 20, 4])
    diff = p * F(r * r * (300 + r), 100 ** 3)
    need(is_nice(diff))
    check = p * F(100 + r, 100) ** 3 - p - F(p * r * 3, 100)
    assert check == diff
    two_year = p * F(r * r, 10000)
    wrong = [rupees(two_year), rupees(two_year * 3), rupees(diff + 10), rupees(diff * 2)]
    return Item(f"CI − SI on {rupees(p)} at {r}% for 3 years",
                f"What is the difference between compound interest and simple interest on {rupees(p)} at {r}% per annum for 3 years?",
                rupees(diff), wrong,
                f"""
                CI = {num(p)} × (1 + {r}/100)³ − {num(p)} = {num(p * F(100 + r, 100) ** 3 - p)}; SI = {num(p)} × {r} × 3/100 = {num(F(p * r * 3, 100))}.
                Difference = **{rupees(diff)}**. Shortcut: P·R²(300 + R)/100³.
                """,
                key=(p, r))


def ci_multiple(rng):
    k, n = rng.choice([2, 3, 4]), rng.choice([3, 4, 5, 6, 8, 10])
    m = rng.choice([2, 3])
    target = k ** m
    wrong = [f"{n * target // k} years", f"{n * (m + 1)} years", f"{n * m + 2} years", f"{n * target} years"]
    return Item(f"Compound interest: ×{k} in {n} years → ×{target}",
                f"At compound interest, a sum of money becomes {k} times itself in {n} years. In how many years will it become {target} times itself at the same rate?",
                f"{n * m} years", wrong,
                f"Under compound interest growth multiplies: every {n} years the sum is multiplied by {k}. {target} = {k}^{m}, so it takes {m} × {n} = **{n * m} years** — not proportional as with simple interest.",
                key=(k, n, m))


INTEREST = [
    Template("si", "easy", si_basic),
    Template("ci", "easy", ci_basic),
    Template("si-multiply", "easy", si_multiply),
    Template("si-principal", "easy", si_principal),
    Template("ci-si-2y", "medium", ci_si_difference),
    Template("si-rate", "medium", si_rate_from_amount),
    Template("ci-half-yearly", "medium", ci_half_yearly),
    Template("si-two-amounts", "hard", si_two_amounts),
    Template("ci-si-3y", "hard", ci_si_three_years),
    Template("ci-multiple", "hard", ci_multiple),
]

TOPICS = {
    "percentages": ("pct", PERCENTAGES),
    "profit-and-loss": ("pl", PROFIT_LOSS),
    "time-and-work": ("tw", TIME_WORK),
    "speed-time-distance": ("std", SPEED),
    "averages": ("avg", AVERAGES),
    "ratio-and-proportion": ("rp", RATIO),
    "simple-and-compound-interest": ("int", INTEREST),
}

__all__ = ["TOPICS", "Retry"]
