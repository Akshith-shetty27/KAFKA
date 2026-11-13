"""
Aptitude content: multiple-choice questions grouped into three sections.

MCQ format: options = list of strings (labelled A, B, C, … in order),
answer = the correct label, explanation = worked solution (Markdown).
"""

CATEGORY = {
    "slug": "aptitude",
    "name": "Aptitude",
    "glyph": "Σ",
    "description": "Speed and accuracy for placement assessments: quantitative, logical and verbal.",
    "sections": [
        {"slug": "quantitative", "name": "Quantitative Aptitude"},
        {"slug": "logical", "name": "Logical Reasoning"},
        {"slug": "verbal", "name": "Verbal Ability"},
    ],
    "topics": [
        # ======================================================= QUANTITATIVE
        {
            "slug": "percentages",
            "name": "Percentages",
            "section": "quantitative",
            "description": "Successive changes, base switching and percentage points.",
            "questions": [
                {
                    "slug": "pct-up-then-down",
                    "title": "Up 20%, then down 20%",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "A number is increased by 20% and the result is then decreased by 20%. What is the net change?",
                    "options": ["No change", "4% decrease", "4% increase", "2% decrease"],
                    "answer": "B",
                    "explanation": """
                        Take 100. After +20%: 120. After −20% of 120 (= 24): 96.
                        Net change = 96 − 100 = **−4%**.

                        Shortcut for successive changes a% and b%: `a + b + ab/100` = 20 − 20 − 400/100 = −4.
                    """,
                },
                {
                    "slug": "pct-consumption-cut",
                    "title": "Keeping expenditure constant",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "The price of sugar rises by 25%. By what percentage must a family reduce its consumption so that its expenditure on sugar stays the same?",
                    "options": ["25%", "20%", "15%", "22.5%"],
                    "answer": "B",
                    "explanation": """
                        Expenditure = price × quantity. Price becomes 1.25×, so quantity must become
                        1 / 1.25 = 0.8×, a reduction of **20%**.

                        General rule: reduction = r / (100 + r) × 100 = 25 / 125 × 100 = 20%.
                    """,
                },
                {
                    "slug": "pct-election-margin",
                    "title": "Election margin",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "In an election between two candidates, the winner received 58% of the valid votes and won by 2,560 votes. How many valid votes were cast?",
                    "options": ["18,000", "20,000", "15,000", "16,000"],
                    "answer": "D",
                    "explanation": """
                        The loser got 42%, so the margin is 58% − 42% = 16% of the valid votes.
                        16% of V = 2,560 → V = 2,560 × 100 / 16 = **16,000**.
                    """,
                },
            ],
        },
        {
            "slug": "profit-and-loss",
            "name": "Profit and Loss",
            "section": "quantitative",
            "description": "Cost price, selling price, mark-ups and discounts.",
            "questions": [
                {
                    "slug": "pl-basic-profit",
                    "title": "Profit percentage",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "An article bought for ₹800 is sold for ₹920. What is the profit percentage?",
                    "options": ["12%", "13.5%", "15%", "18%"],
                    "answer": "C",
                    "explanation": """
                        Profit = 920 − 800 = ₹120. Profit % is always on cost price:
                        120 / 800 × 100 = **15%**.
                    """,
                },
                {
                    "slug": "pl-markup-discount",
                    "title": "Mark-up then discount",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "A shopkeeper marks goods 40% above cost price and then gives a 10% discount on the marked price. What is the profit percentage?",
                    "options": ["26%", "30%", "28%", "24%"],
                    "answer": "A",
                    "explanation": """
                        Let CP = 100. Marked price = 140. Selling price = 90% of 140 = 126.
                        Profit = **26%**. (Not 40 − 10 = 30: the discount applies to the larger marked price.)
                    """,
                },
                {
                    "slug": "pl-same-sp-gain-loss",
                    "title": "Same selling price, gain and loss",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "Two articles are each sold for ₹990. One is sold at a 10% gain and the other at a 10% loss. What is the overall result?",
                    "options": ["No profit, no loss", "1% gain", "1% loss", "2% loss"],
                    "answer": "C",
                    "explanation": """
                        CP of the first = 990 / 1.1 = ₹900. CP of the second = 990 / 0.9 = ₹1,100.
                        Total CP = ₹2,000, total SP = ₹1,980 → loss of ₹20 = **1% loss**.

                        Rule: equal SPs with x% gain and x% loss always give a loss of x²/100 %.
                    """,
                },
            ],
        },
        {
            "slug": "time-and-work",
            "name": "Time and Work",
            "section": "quantitative",
            "description": "Work rates, combined work, pipes and cisterns.",
            "questions": [
                {
                    "slug": "tw-together",
                    "title": "Working together",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "A can complete a job in 10 days and B can complete it in 15 days. How long will they take working together?",
                    "options": ["12.5 days", "7.5 days", "5 days", "6 days"],
                    "answer": "D",
                    "explanation": """
                        Rates: A = 1/10 job/day, B = 1/15 job/day. Together = 1/10 + 1/15 = 3/30 + 2/30 = 1/6.
                        Time = **6 days**.
                    """,
                },
                {
                    "slug": "tw-find-one-rate",
                    "title": "Finding one worker's time",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "A and B together finish a task in 12 days. A alone can finish it in 20 days. How many days would B alone take?",
                    "options": ["24 days", "28 days", "30 days", "32 days"],
                    "answer": "C",
                    "explanation": """
                        B's rate = 1/12 − 1/20 = 5/60 − 3/60 = 2/60 = 1/30.
                        B alone takes **30 days**.
                    """,
                },
                {
                    "slug": "tw-fill-and-drain",
                    "title": "Filling pipe vs draining pipe",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "Pipe A fills a tank in 6 hours. Pipe B empties the full tank in 9 hours. If both are opened on an empty tank, how long until it is full?",
                    "options": ["15 hours", "16 hours", "18 hours", "3.6 hours"],
                    "answer": "C",
                    "explanation": """
                        Net rate = 1/6 − 1/9 = 3/18 − 2/18 = 1/18 tank per hour → **18 hours**.
                        A draining pipe contributes a negative rate.
                    """,
                },
            ],
        },
        {
            "slug": "speed-time-distance",
            "name": "Speed, Time and Distance",
            "section": "quantitative",
            "description": "Unit conversion, trains and average speed.",
            "questions": [
                {
                    "slug": "std-kmh-to-ms",
                    "title": "Converting km/h to m/s",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "A car travels at 54 km/h. What is its speed in metres per second?",
                    "options": ["15 m/s", "12 m/s", "18 m/s", "20 m/s"],
                    "answer": "A",
                    "explanation": """
                        1 km/h = 1000 m / 3600 s = 5/18 m/s. So 54 × 5/18 = **15 m/s**.
                    """,
                },
                {
                    "slug": "std-train-pole",
                    "title": "Train passing a pole",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "A 240 m long train passes a pole in 12 seconds. What is its speed in km/h?",
                    "options": ["60 km/h", "66 km/h", "72 km/h", "80 km/h"],
                    "answer": "C",
                    "explanation": """
                        Passing a pole means covering the train's own length: 240 m in 12 s = 20 m/s.
                        20 × 18/5 = **72 km/h**.
                    """,
                },
                {
                    "slug": "std-average-speed",
                    "title": "Average speed for a round trip",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "A person drives to the office at 40 km/h and returns along the same route at 60 km/h. What is the average speed for the whole trip?",
                    "options": ["50 km/h", "48 km/h", "45 km/h", "52 km/h"],
                    "answer": "B",
                    "explanation": """
                        Average speed = total distance / total time, not the average of the speeds.
                        For equal distances: 2ab / (a + b) = 2 × 40 × 60 / 100 = **48 km/h**.
                    """,
                },
            ],
        },
        # ============================================================ LOGICAL
        {
            "slug": "number-series",
            "name": "Number Series",
            "section": "logical",
            "description": "Spot the rule: differences, ratios and squares.",
            "questions": [
                {
                    "slug": "ns-pronic",
                    "title": "2, 6, 12, 20, 30, ?",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Find the next number: **2, 6, 12, 20, 30, ?**",
                    "options": ["40", "44", "36", "42"],
                    "answer": "D",
                    "explanation": """
                        Differences are 4, 6, 8, 10 → next difference 12, giving 30 + 12 = **42**.
                        Equivalently, the terms are n(n + 1): 1·2, 2·3, 3·4, 4·5, 5·6, 6·7.
                    """,
                },
                {
                    "slug": "ns-double-plus-one",
                    "title": "3, 7, 15, 31, 63, ?",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Find the next number: **3, 7, 15, 31, 63, ?**",
                    "options": ["125", "126", "127", "129"],
                    "answer": "C",
                    "explanation": """
                        Each term is double the previous plus one: 63 × 2 + 1 = **127**.
                        (The terms are 2ⁿ − 1.)
                    """,
                },
                {
                    "slug": "ns-doubling-differences",
                    "title": "2, 3, 5, 9, 17, ?",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "Find the next number: **2, 3, 5, 9, 17, ?**",
                    "options": ["31", "33", "34", "25"],
                    "answer": "B",
                    "explanation": """
                        Differences: 1, 2, 4, 8 — each doubles. Next difference is 16: 17 + 16 = **33**.
                    """,
                },
            ],
        },
        {
            "slug": "blood-relations",
            "name": "Blood Relations",
            "section": "logical",
            "description": "Family-tree reasoning from verbal clues.",
            "questions": [
                {
                    "slug": "br-granddaughter",
                    "title": "Sister, mother, grandfather",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "A is B's sister. C is B's mother. D is C's father. How is A related to D?",
                    "options": ["Daughter", "Granddaughter", "Grandmother", "Niece"],
                    "answer": "B",
                    "explanation": """
                        A and B share mother C, so A is C's daughter. D is C's father.
                        A is therefore D's **granddaughter**.
                    """,
                },
                {
                    "slug": "br-grandfathers-only-son",
                    "title": "My grandfather's only son",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "Pointing to a man, Ritu says: \"He is the son of my grandfather's only son.\" How is the man related to Ritu?",
                    "options": ["Cousin", "Uncle", "Brother", "Father"],
                    "answer": "C",
                    "explanation": """
                        Ritu's (paternal) grandfather's only son is Ritu's father. The son of Ritu's father
                        is Ritu's **brother**.
                    """,
                },
                {
                    "slug": "br-wife",
                    "title": "Father, brother, daughter",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "X is the father of Y. Y is the brother of Z. Z is the daughter of W, and W is a woman. How is W related to X?",
                    "options": ["Sister", "Mother", "Wife", "Cannot be determined"],
                    "answer": "C",
                    "explanation": """
                        Y and Z are siblings, so X is also Z's father. W is a woman and Z's parent, so W is
                        Z's mother. The mother of X's child is X's **wife**.
                    """,
                },
            ],
        },
        {
            "slug": "coding-decoding",
            "name": "Coding–Decoding",
            "section": "logical",
            "description": "Letter shifts, reversals and position patterns.",
            "questions": [
                {
                    "slug": "cd-shift-one",
                    "title": "CAT → DBU",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "If CAT is coded as DBU, how is DOG coded?",
                    "options": ["EPH", "EPG", "FQH", "CNF"],
                    "answer": "A",
                    "explanation": """
                        Each letter moves one place forward: C→D, A→B, T→U.
                        DOG → **EPH**.
                    """,
                },
                {
                    "slug": "cd-shift-two",
                    "title": "MANGO → OCPIQ",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "In a certain code, MANGO is written as OCPIQ. How is APPLE written in that code?",
                    "options": ["CRRNG", "BQQMF", "CRRMG", "CQRNG"],
                    "answer": "A",
                    "explanation": """
                        Every letter moves two places forward (M→O, A→C, N→P, G→I, O→Q).
                        APPLE → **CRRNG**.
                    """,
                },
                {
                    "slug": "cd-increasing-shift",
                    "title": "FRIEND → HUMJTK",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "If FRIEND is coded as HUMJTK, how is CANDLE coded?",
                    "options": ["EDRIRL", "EDRJRL", "ECRIRL", "FDRIRL"],
                    "answer": "A",
                    "explanation": """
                        The shifts increase by one per position: +2, +3, +4, +5, +6, +7
                        (F→H, R→U, I→M, E→J, N→T, D→K).

                        CANDLE: C+2 = E, A+3 = D, N+4 = R, D+5 = I, L+6 = R, E+7 = L → **EDRIRL**.
                    """,
                },
            ],
        },
        # ============================================================== VERBAL
        {
            "slug": "vocabulary",
            "name": "Vocabulary",
            "section": "verbal",
            "description": "Synonyms and antonyms that show up in placement tests.",
            "questions": [
                {
                    "slug": "voc-ephemeral",
                    "title": "Synonym: Ephemeral",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Choose the word closest in meaning to **EPHEMERAL**.",
                    "options": ["Short-lived", "Eternal", "Ethereal", "Essential"],
                    "answer": "A",
                    "explanation": """
                        *Ephemeral* means lasting a very short time — **short-lived**. "Eternal" is its opposite;
                        "ethereal" (delicate, heavenly) is a common sound-alike trap.
                    """,
                },
                {
                    "slug": "voc-candid",
                    "title": "Antonym: Candid",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Choose the word most nearly **opposite** in meaning to **CANDID**.",
                    "options": ["Frank", "Honest", "Open", "Evasive"],
                    "answer": "D",
                    "explanation": """
                        *Candid* means frank and straightforward. Frank, honest and open are synonyms; the
                        opposite is **evasive** (avoiding a direct answer).
                    """,
                },
                {
                    "slug": "voc-meticulous",
                    "title": "Synonym: Meticulous",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Choose the word closest in meaning to **METICULOUS**.",
                    "options": ["Careless", "Thorough", "Hasty", "Generous"],
                    "answer": "B",
                    "explanation": """
                        *Meticulous* means showing great attention to detail — **thorough**. Careless and hasty
                        are opposites.
                    """,
                },
            ],
        },
        {
            "slug": "sentence-correction",
            "name": "Sentence Correction",
            "section": "verbal",
            "description": "Agreement, prepositions and common grammar traps.",
            "questions": [
                {
                    "slug": "sc-neither-nor",
                    "title": "Neither … nor agreement",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "Choose the grammatically correct sentence.",
                    "options": [
                        "Neither the manager nor the employees was aware of the change.",
                        "Neither the manager nor the employees were aware of the change.",
                        "Neither the manager or the employees were aware of the change.",
                        "Neither the manager nor the employees is aware of the change.",
                    ],
                    "answer": "B",
                    "explanation": """
                        With *neither … nor*, the verb agrees with the subject **nearer** to it. "Employees" is
                        plural, so the verb is **were**. Option C wrongly pairs *neither* with *or*.
                    """,
                },
                {
                    "slug": "sc-one-of",
                    "title": "One of my friends …",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Fill in the blank: \"One of my friends ___ a software engineer.\"",
                    "options": ["is", "are", "were", "have been"],
                    "answer": "A",
                    "explanation": """
                        The subject is **one** (singular); "of my friends" only describes it. So the verb is
                        **is**.
                    """,
                },
                {
                    "slug": "sc-senior-to",
                    "title": "Senior ___ me",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Fill in the blank: \"She is senior ___ me by two years.\"",
                    "options": ["than", "to", "from", "over"],
                    "answer": "B",
                    "explanation": """
                        Latin comparatives such as *senior, junior, superior, inferior, prior* take **to**, not
                        *than*.
                    """,
                },
            ],
        },
    ],
}
