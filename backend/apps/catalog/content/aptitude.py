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
                {
                    "slug": "pct-more-less",
                    "title": "25% more, how much less?",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "A's salary is 25% more than B's. By what percentage is B's salary less than A's?",
                    "options": ["25%", "22%", "20%", "15%"],
                    "answer": "C",
                    "explanation": """
                        Let B = 100, so A = 125. B is 25 less than A, and "less than A" is measured on A:
                        25 / 125 × 100 = **20%**.

                        Rule: if A is r% more than B, B is r / (100 + r) × 100 % less than A.
                    """,
                },
                {
                    "slug": "pct-population-growth",
                    "title": "Two years of growth",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "A town's population of 10,000 grows by 10% in the first year and by 20% in the second. What is the population after two years?",
                    "options": ["13,200", "13,000", "13,300", "12,800"],
                    "answer": "A",
                    "explanation": """
                        Successive growth multiplies: 10,000 × 1.10 × 1.20 = **13,200**.
                        (Adding 10% + 20% = 30% → 13,000 is the classic trap.)
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
                {
                    "slug": "pl-false-weight",
                    "title": "The 900-gram kilogram",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "A dishonest shopkeeper claims to sell at cost price but uses a 900 g weight in place of 1 kg. What is his profit percentage?",
                    "options": ["10%", "9.09%", "12.5%", "11.11%"],
                    "answer": "D",
                    "explanation": """
                        He is paid for 1000 g but gives only 900 g. Gain = 100 g on goods costing 900 g:
                        100 / 900 × 100 = **11.11%** (11 1/9 %).
                    """,
                },
                {
                    "slug": "pl-loss-to-gain",
                    "title": "From a loss to a gain",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "By selling an article for ₹450, a trader loses 10%. At what price should he sell it to gain 20%?",
                    "options": ["₹540", "₹600", "₹580", "₹620"],
                    "answer": "B",
                    "explanation": """
                        A 10% loss means SP = 90% of CP, so CP = 450 / 0.9 = ₹500.
                        For a 20% gain: 500 × 1.2 = **₹600**.
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
                {
                    "slug": "tw-more-workers",
                    "title": "More workers, fewer days",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "12 workers can build a wall in 15 days. How many days would 20 workers take, working at the same rate?",
                    "options": ["8 days", "10 days", "12 days", "9 days"],
                    "answer": "D",
                    "explanation": """
                        Total work = 12 × 15 = 180 worker-days. With 20 workers: 180 / 20 = **9 days**.
                    """,
                },
                {
                    "slug": "tw-one-leaves",
                    "title": "One worker leaves midway",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "A can finish a job in 20 days and B in 30 days. They start together, but A leaves after 6 days. In how many days, in total, is the job finished?",
                    "options": ["18 days", "21 days", "20 days", "24 days"],
                    "answer": "B",
                    "explanation": """
                        Together they do 1/20 + 1/30 = 5/60 = 1/12 of the job per day.
                        In 6 days: 6/12 = 1/2 of the job. B finishes the other half alone in 1/2 × 30 = 15 days.
                        Total = 6 + 15 = **21 days**.
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
                {
                    "slug": "std-trains-opposite",
                    "title": "Two trains crossing",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "Two trains, 120 m and 180 m long, run on parallel tracks in opposite directions at 40 km/h and 50 km/h. How long do they take to cross each other completely?",
                    "options": ["10 s", "15 s", "12 s", "18 s"],
                    "answer": "C",
                    "explanation": """
                        Opposite directions → speeds add: 90 km/h = 90 × 5/18 = 25 m/s.
                        They must cover both lengths: 120 + 180 = 300 m. Time = 300 / 25 = **12 s**.
                    """,
                },
                {
                    "slug": "std-boat-stream",
                    "title": "Upstream and downstream",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "A boat covers 24 km downstream in 2 hours and the same distance upstream in 3 hours. What is the speed of the stream?",
                    "options": ["2 km/h", "1 km/h", "3 km/h", "4 km/h"],
                    "answer": "A",
                    "explanation": """
                        Downstream speed = 24 / 2 = 12 km/h; upstream = 24 / 3 = 8 km/h.
                        Stream speed = (12 − 8) / 2 = **2 km/h** (and the boat's own speed is (12 + 8) / 2 = 10 km/h).
                    """,
                },
            ],
        },
        {
            "slug": "averages",
            "name": "Averages",
            "section": "quantitative",
            "description": "Totals, replacements and consecutive numbers.",
            "questions": [
                {
                    "slug": "avg-removed-number",
                    "title": "A number is removed",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "The average of 5 numbers is 20. When one number is removed, the average of the rest becomes 18. Which number was removed?",
                    "options": ["26", "28", "30", "32"],
                    "answer": "B",
                    "explanation": """
                        Work with totals, not averages: 5 × 20 = 100 and 4 × 18 = 72.
                        Removed number = 100 − 72 = **28**.
                    """,
                },
                {
                    "slug": "avg-teacher-age",
                    "title": "The teacher joins",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "The average age of 10 students is 15 years. When the teacher's age is included, the average rises to 17. How old is the teacher?",
                    "options": ["35", "32", "40", "37"],
                    "answer": "D",
                    "explanation": """
                        Students' total = 10 × 15 = 150. New total = 11 × 17 = 187.
                        Teacher = 187 − 150 = **37 years**.
                    """,
                },
                {
                    "slug": "avg-consecutive-odd",
                    "title": "Seven consecutive odd numbers",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "The average of 7 consecutive odd numbers is 33. What is the largest of them?",
                    "options": ["39", "37", "41", "45"],
                    "answer": "A",
                    "explanation": """
                        For evenly spaced numbers the average is the middle term: the 4th number is 33.
                        Three more odd numbers above it: 35, 37, **39**.
                    """,
                },
                {
                    "slug": "avg-batting",
                    "title": "Raising a batting average",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "A batsman's average after 16 innings is 40. How many runs must he score in the 17th innings to raise his average to 42?",
                    "options": ["72", "76", "74", "82"],
                    "answer": "C",
                    "explanation": """
                        Runs so far = 16 × 40 = 640. Needed total after 17 innings = 17 × 42 = 714.
                        Runs required = 714 − 640 = **74**.
                    """,
                },
            ],
        },
        {
            "slug": "ratio-and-proportion",
            "name": "Ratio and Proportion",
            "section": "quantitative",
            "description": "Sharing, mixtures and age ratios.",
            "questions": [
                {
                    "slug": "rp-share",
                    "title": "Sharing ₹1,800",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "₹1,800 is divided between A and B in the ratio 4 : 5. What is B's share?",
                    "options": ["₹800", "₹900", "₹1,100", "₹1,000"],
                    "answer": "D",
                    "explanation": """
                        Total parts = 4 + 5 = 9; one part = 1800 / 9 = ₹200.
                        B gets 5 parts = **₹1,000**.
                    """,
                },
                {
                    "slug": "rp-mixture-water",
                    "title": "Diluting milk",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "A 40-litre mixture contains milk and water in the ratio 3 : 1. How much water must be added to make the ratio 3 : 2?",
                    "options": ["5 litres", "10 litres", "8 litres", "12 litres"],
                    "answer": "B",
                    "explanation": """
                        Milk = 30 L, water = 10 L. Milk doesn't change, so for 3 : 2 water must be 30 × 2/3 = 20 L.
                        Add 20 − 10 = **10 litres**.
                    """,
                },
                {
                    "slug": "rp-ages",
                    "title": "Ages four years ago",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "The ratio of the present ages of A and B is 5 : 7. Four years ago it was 3 : 5. What is A's present age?",
                    "options": ["10 years", "8 years", "12 years", "15 years"],
                    "answer": "A",
                    "explanation": """
                        Let the ages be 5x and 7x. Then (5x − 4) / (7x − 4) = 3/5
                        → 25x − 20 = 21x − 12 → 4x = 8 → x = 2. A is 5 × 2 = **10 years** old.
                    """,
                },
                {
                    "slug": "rp-fourth-proportional",
                    "title": "Fourth proportional",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Find the fourth proportional to 4, 9 and 12.",
                    "options": ["24", "30", "27", "36"],
                    "answer": "C",
                    "explanation": """
                        4 : 9 = 12 : x → 4x = 9 × 12 = 108 → x = **27**.
                    """,
                },
            ],
        },
        {
            "slug": "simple-and-compound-interest",
            "name": "Simple and Compound Interest",
            "section": "quantitative",
            "description": "Interest on principal versus interest on interest.",
            "questions": [
                {
                    "slug": "si-basic",
                    "title": "Simple interest for 3 years",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "What is the simple interest on ₹5,000 at 8% per annum for 3 years?",
                    "options": ["₹1,000", "₹1,250", "₹1,200", "₹1,500"],
                    "answer": "C",
                    "explanation": """
                        SI = P × R × T / 100 = 5000 × 8 × 3 / 100 = **₹1,200**.
                    """,
                },
                {
                    "slug": "ci-basic",
                    "title": "Compound interest for 2 years",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "What is the compound interest on ₹10,000 at 10% per annum for 2 years, compounded annually?",
                    "options": ["₹2,100", "₹2,000", "₹2,050", "₹2,200"],
                    "answer": "A",
                    "explanation": """
                        Amount = 10,000 × 1.1² = ₹12,100, so CI = **₹2,100**.
                        It exceeds simple interest (₹2,000) by the interest earned on the first year's interest (₹100).
                    """,
                },
                {
                    "slug": "ci-si-difference",
                    "title": "CI minus SI",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "What is the difference between compound and simple interest on ₹8,000 at 5% per annum for 2 years?",
                    "options": ["₹15", "₹25", "₹40", "₹20"],
                    "answer": "D",
                    "explanation": """
                        For 2 years, CI − SI = P × (R/100)² = 8000 × (0.05)² = 8000 × 0.0025 = **₹20**.
                    """,
                },
                {
                    "slug": "si-doubling",
                    "title": "When does money double?",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "At what rate of simple interest does a sum of money double itself in 8 years?",
                    "options": ["10%", "12.5%", "12%", "15%"],
                    "answer": "B",
                    "explanation": """
                        Doubling means interest = principal, i.e. R × T = 100. R = 100 / 8 = **12.5%** per annum.
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
                {
                    "slug": "ns-squares-plus-one",
                    "title": "1, 2, 5, 10, 17, 26, ?",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Find the next number: **1, 2, 5, 10, 17, 26, ?**",
                    "options": ["35", "36", "39", "37"],
                    "answer": "D",
                    "explanation": """
                        The terms are n² + 1 for n = 0, 1, 2, …: 0+1, 1+1, 4+1, 9+1, 16+1, 25+1 → next 36 + 1 = **37**.
                        (Differences 1, 3, 5, 7, 9 → next 11 gives the same answer.)
                    """,
                },
                {
                    "slug": "ns-squares-minus-one",
                    "title": "120, 99, 80, 63, 48, ?",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "Find the next number: **120, 99, 80, 63, 48, ?**",
                    "options": ["35", "33", "36", "38"],
                    "answer": "A",
                    "explanation": """
                        Each term is a square minus one: 11² − 1, 10² − 1, 9² − 1, 8² − 1, 7² − 1 → 6² − 1 = **35**.
                        Differences −21, −19, −17, −15 → next −13 confirms it.
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
                {
                    "slug": "br-mothers-mother",
                    "title": "My mother's mother's only daughter",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "Introducing a woman, Arjun says: \"She is the only daughter of my mother's mother.\" How is the woman related to Arjun?",
                    "options": ["Aunt", "Grandmother", "Mother", "Sister"],
                    "answer": "C",
                    "explanation": """
                        Arjun's mother is a daughter of his mother's mother. If that grandmother has only one
                        daughter, it must be Arjun's mother. The woman is his **mother**.
                    """,
                },
                {
                    "slug": "br-symbol-code",
                    "title": "Relations written as symbols",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "If **P + Q** means P is the father of Q, and **P × Q** means P is the sister of Q, what does **A + B × C** mean?",
                    "options": ["A is the uncle of C", "A is the father of C", "A is the brother of C", "C is the father of A"],
                    "answer": "B",
                    "explanation": """
                        A + B: A is B's father. B × C: B is C's sister, so B and C share parents.
                        Therefore A is also **C's father**.
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
                {
                    "slug": "cd-reverse",
                    "title": "TRAIN → NIART",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "If TRAIN is written as NIART, how is PLANE written in the same code?",
                    "options": ["ENLAP", "ELANP", "ENALP", "PENAL"],
                    "answer": "C",
                    "explanation": """
                        The letters are simply reversed. PLANE → **ENALP**.
                    """,
                },
                {
                    "slug": "cd-letter-values",
                    "title": "Adding letter positions",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "If A = 1, B = 2, …, Z = 26, what is the value of the word CODE (the sum of its letters)?",
                    "options": ["25", "29", "31", "27"],
                    "answer": "D",
                    "explanation": """
                        C = 3, O = 15, D = 4, E = 5 → 3 + 15 + 4 + 5 = **27**.
                    """,
                },
            ],
        },
        {
            "slug": "direction-sense",
            "name": "Direction Sense",
            "section": "logical",
            "description": "Turns, distances and shadows.",
            "questions": [
                {
                    "slug": "ds-net-position",
                    "title": "North, right, right",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Ravi walks 5 km north, turns right and walks 3 km, then turns right again and walks 5 km. Where is he now relative to his starting point?",
                    "options": ["3 km West", "5 km North", "3 km East", "13 km East"],
                    "answer": "C",
                    "explanation": """
                        North 5 km, then right (east) 3 km, then right again (south) 5 km. The north and south
                        legs cancel, leaving him **3 km east** of the start.
                    """,
                },
                {
                    "slug": "ds-shortest-distance",
                    "title": "Shortest way back",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "A man walks 6 km east and then 8 km north. What is the shortest distance between him and his starting point?",
                    "options": ["10 km", "12 km", "14 km", "7 km"],
                    "answer": "A",
                    "explanation": """
                        The two legs are perpendicular, so use Pythagoras: √(6² + 8²) = √100 = **10 km**.
                    """,
                },
                {
                    "slug": "ds-turns",
                    "title": "Clockwise, then anticlockwise",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Meera faces north. She turns 90° clockwise, then 180° anticlockwise. Which direction is she facing now?",
                    "options": ["East", "South", "North", "West"],
                    "answer": "D",
                    "explanation": """
                        North → 90° clockwise → East → 180° anticlockwise → **West**.
                        Net effect: 90° anticlockwise from north.
                    """,
                },
                {
                    "slug": "ds-morning-shadow",
                    "title": "The morning shadow",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "One morning after sunrise, Kiran stood facing a pole. The pole's shadow fell exactly to his right. Which direction was he facing?",
                    "options": ["North", "South", "East", "West"],
                    "answer": "B",
                    "explanation": """
                        In the morning the sun is in the east, so shadows point **west**. The shadow is on his
                        right, so his right hand points west — which means he is facing **south**.
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
                {
                    "slug": "voc-obsolete",
                    "title": "Synonym: Obsolete",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Choose the word closest in meaning to **OBSOLETE**.",
                    "options": ["Obvious", "Outdated", "Durable", "Hidden"],
                    "answer": "B",
                    "explanation": """
                        *Obsolete* means no longer in use — **outdated**. "Obvious" is a sound-alike trap.
                    """,
                },
                {
                    "slug": "voc-benevolent",
                    "title": "Antonym: Benevolent",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Choose the word most nearly **opposite** in meaning to **BENEVOLENT**.",
                    "options": ["Kind", "Generous", "Charitable", "Malevolent"],
                    "answer": "D",
                    "explanation": """
                        *Benevolent* means well-meaning and kind. Its opposite is **malevolent** — wishing harm on
                        others (*bene* = good, *male* = bad).
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
                {
                    "slug": "sc-each-of",
                    "title": "Each of the players …",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Fill in the blank: \"Each of the players ___ given a new jersey.\"",
                    "options": ["were", "have been", "was", "are"],
                    "answer": "C",
                    "explanation": """
                        The subject is **each** (singular); "of the players" only describes it. So the verb is
                        singular: **was**.
                    """,
                },
                {
                    "slug": "sc-since-for",
                    "title": "Since or for?",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Fill in the blank: \"She has been working here ___ 2019.\"",
                    "options": ["since", "for", "from", "by"],
                    "answer": "A",
                    "explanation": """
                        Use **since** with a point in time (2019, Monday) and *for* with a duration (three years,
                        two weeks) in the perfect tenses.
                    """,
                },
            ],
        },
    ],
}

# The hand-written questions above, before the generated bank is merged in
# (generate_aptitude tops each topic up relative to these).
HAND_WRITTEN_TOPICS = [{"slug": t["slug"], "questions": t["questions"]} for t in CATEGORY["topics"]]

# Expanded bank: content/bank/aptitude/<topic>.json (see `manage.py generate_aptitude`).
from .bank import extend_aptitude  # noqa: E402

extend_aptitude(CATEGORY)
