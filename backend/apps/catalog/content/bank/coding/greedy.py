from . import P

TOPIC = "greedy"

PROBLEMS = [
    P(
        "content-children", "Cookies for Content Children", "easy", ["greedy", "sorting"],
        statement="Child `i` is content with a cookie of size at least `greed[i]`; cookie `j` has size `sizes[j]`. Each child gets at most one cookie. Return the maximum number of content children.",
        inputs="- `greed`: a list of greed factors\n- `sizes`: a list of cookie sizes",
        output="The maximum number of content children.",
        constraints="- `1 <= greed.length <= 3 × 10^4`\n- `0 <= sizes.length <= 3 × 10^4`",
        examples=[
            ({"greed": [1, 2, 3], "sizes": [1, 1]}, 1, "Both cookies only satisfy the child with greed 1."),
            ({"greed": [1, 2], "sizes": [1, 2, 3]}, 2, ""),
        ],
        approach="Sort both lists. Walk through the cookies from smallest; give each cookie to the least greedy unsatisfied child if it is big enough.",
        explanation="Using the smallest cookie that works for the least greedy child never wastes a big cookie that a greedier child might need (exchange argument).",
        time="O(n log n + m log m)", space="O(1) besides sorting",
        code="""
        def find_content_children(greed: list[int], sizes: list[int]) -> int:
            greed, sizes = sorted(greed), sorted(sizes)
            child = 0
            for cookie in sizes:
                if child < len(greed) and cookie >= greed[child]:
                    child += 1
            return child
        """,
    ),
    P(
        "lemonade-change", "Giving Change at a Lemonade Stand", "easy", ["greedy"],
        statement="Lemonade costs 5. Customers pay in order with a 5, 10 or 20 note and you start with no change. Return `true` if you can give every customer correct change.",
        inputs="- `bills`: the notes customers pay with, in order",
        output="`true` or `false`.",
        constraints="- `1 <= bills.length <= 10^5`\n- `bills[i]` is 5, 10 or 20",
        examples=[
            ({"bills": [5, 5, 5, 10, 20]}, True, ""),
            ({"bills": [5, 5, 10, 10, 20]}, False, "The last customer needs 15 but you only hold two 10s."),
        ],
        approach="Count your 5s and 10s. For a 10, give back a 5. For a 20, prefer giving a 10 + 5; otherwise three 5s.",
        explanation="5s are the most flexible note (they're needed for every kind of change), so spend a 10 first whenever possible.",
        time="O(n)", space="O(1)",
        code="""
        def lemonade_change(bills: list[int]) -> bool:
            fives = tens = 0
            for bill in bills:
                if bill == 5:
                    fives += 1
                elif bill == 10:
                    if not fives:
                        return False
                    fives, tens = fives - 1, tens + 1
                elif tens and fives:
                    tens, fives = tens - 1, fives - 1
                elif fives >= 3:
                    fives -= 3
                else:
                    return False
            return True
        """,
    ),
    P(
        "loading-a-truck", "Most Units on a Truck", "easy", ["greedy", "sorting"],
        statement="`box_types[i] = [count, units]`: there are `count` boxes of that type, each holding `units` units. The truck carries at most `truck_size` boxes. Return the maximum total units.",
        inputs="- `box_types`: a list of `[count, units per box]`\n- `truck_size`: the box limit",
        output="The maximum number of units.",
        constraints="- `1 <= box_types.length <= 1000`\n- `1 <= truck_size <= 10^6`",
        examples=[
            ({"box_types": [[1, 3], [2, 2], [3, 1]], "truck_size": 4}, 8, "1×3 + 2×2 + 1×1."),
            ({"box_types": [[5, 10], [2, 5], [4, 7], [3, 9]], "truck_size": 10}, 91, ""),
        ],
        approach="Sort box types by units per box, highest first, and load as many of each as still fit.",
        explanation="Every box takes one slot, so a slot is always best used by the box with the most units — the greedy choice is optimal.",
        time="O(n log n)", space="O(1) besides sorting",
        code="""
        def maximum_units(box_types: list[list[int]], truck_size: int) -> int:
            total = 0
            for count, units in sorted(box_types, key=lambda b: -b[1]):
                take = min(count, truck_size)
                total += take * units
                truck_size -= take
                if truck_size == 0:
                    break
            return total
        """,
    ),
    P(
        "planting-flowers", "Room to Plant Flowers", "easy", ["greedy"],
        statement="A flowerbed is a list of `0` (empty) and `1` (planted). Flowers can't be planted in adjacent plots. Return `true` if `n` new flowers can be planted without breaking the rule.",
        inputs="- `bed`: a list of 0s and 1s (no adjacent 1s)\n- `n`: flowers to plant",
        output="`true` or `false`.",
        constraints="- `1 <= bed.length <= 2 × 10^4`\n- `0 <= n <= bed.length`",
        examples=[
            ({"bed": [1, 0, 0, 0, 1], "n": 1}, True, "Plant in the middle."),
            ({"bed": [1, 0, 0, 0, 1], "n": 2}, False, ""),
        ],
        tests=[({"bed": [0, 0, 1, 0, 0], "n": 2}, True)],
        approach="Scan left to right and plant in every empty plot whose neighbours (or the edges) are empty. Count plantings.",
        explanation="Planting as early as possible never blocks more spots than planting later would, so the greedy count is the maximum.",
        time="O(n)", space="O(n) (a copy of the bed)",
        code="""
        def can_place_flowers(bed: list[int], n: int) -> bool:
            bed = bed[:]
            for i in range(len(bed)):
                if bed[i] == 0 and (i == 0 or bed[i - 1] == 0) and (i == len(bed) - 1 or bed[i + 1] == 0):
                    bed[i] = 1
                    n -= 1
            return n <= 0
        """,
    ),
    P(
        "negate-k-times", "Largest Sum After k Negations", "easy", ["greedy", "sorting"],
        statement="Exactly `k` times, choose an index and replace `nums[i]` with `−nums[i]` (the same index may be chosen repeatedly). Return the largest possible sum.",
        inputs="- `nums`: a list of integers\n- `k`: the number of negations",
        output="The maximum sum.",
        constraints="- `1 <= nums.length <= 10^4`\n- `1 <= k <= 10^4`",
        examples=[
            ({"nums": [4, 2, 3], "k": 1}, 5, "Negate 2: 4 − 2 + 3 = 5."),
            ({"nums": [3, -1, 0, 2], "k": 3}, 6, "Negate −1, then waste the rest on 0."),
        ],
        tests=[({"nums": [2, -3, -1, 5, -4], "k": 2}, 13)],
        approach="Sort ascending and flip negative numbers from the most negative while `k` lasts. If an odd number of flips is left over, flip the smallest absolute value once.",
        explanation="Flipping the most negative number gains the most. Leftover flips can be paired up on any element; only an odd leftover costs anything, and it's cheapest on the smallest absolute value.",
        time="O(n log n)", space="O(n)",
        code="""
        def largest_sum_after_negations(nums: list[int], k: int) -> int:
            nums = sorted(nums)
            for i in range(len(nums)):
                if k and nums[i] < 0:
                    nums[i] = -nums[i]
                    k -= 1
            total = sum(nums)
            if k % 2:
                total -= 2 * min(nums)
            return total
        """,
    ),
    P(
        "moving-chips", "Cheapest Way to Stack the Chips", "easy", ["greedy"],
        statement="Chips sit at integer `positions`. Moving a chip by 2 costs nothing; moving it by 1 costs 1. Return the minimum cost to move all chips to the same position.",
        inputs="- `positions`: a list of chip positions",
        output="The minimum total cost.",
        constraints="- `1 <= positions.length <= 100`",
        examples=[
            ({"positions": [1, 2, 3]}, 1, "Move the chip at 2 by one step."),
            ({"positions": [2, 2, 2, 3, 3]}, 2, "Move the two chips at 3."),
        ],
        approach="Free moves keep a chip's parity, so all even-position chips can gather for free, and so can all odd ones. Then move the smaller group by one step each.",
        explanation="Only crossing between even and odd positions costs anything, and each chip needs at most one such step.",
        time="O(n)", space="O(1)",
        code="""
        def min_cost_to_move_chips(positions: list[int]) -> int:
            odd = sum(p % 2 for p in positions)
            return min(odd, len(positions) - odd)
        """,
    ),
    P(
        "can-reach-the-end", "Can You Reach the Last Index?", "medium", ["greedy"],
        statement="You start at index 0. `nums[i]` is the maximum jump length from index `i`. Return `true` if you can reach the last index.",
        inputs="- `nums`: a list of non-negative integers",
        output="`true` or `false`.",
        constraints="- `1 <= nums.length <= 10^4`",
        examples=[
            ({"nums": [2, 3, 1, 1, 4]}, True, "0 → 1 → 4."),
            ({"nums": [3, 2, 1, 0, 4]}, False, "Every route lands on the 0 at index 3."),
        ],
        approach="Track the farthest index reachable so far. Scan left to right; if the current index is beyond that, you're stuck; otherwise extend the reach with `i + nums[i]`.",
        explanation="Every index up to the farthest reach is reachable, so you only need that one number rather than exploring paths.",
        time="O(n)", space="O(1)",
        code="""
        def can_jump(nums: list[int]) -> bool:
            reach = 0
            for i, step in enumerate(nums):
                if i > reach:
                    return False
                reach = max(reach, i + step)
            return True
        """,
    ),
    P(
        "fewest-jumps", "Fewest Jumps to the End", "medium", ["greedy", "bfs"],
        statement="Starting at index 0, `nums[i]` is the maximum jump length from index `i`. The last index is always reachable. Return the minimum number of jumps to reach it.",
        inputs="- `nums`: a list of non-negative integers",
        output="The minimum number of jumps.",
        constraints="- `1 <= nums.length <= 10^4`",
        examples=[
            ({"nums": [2, 3, 1, 1, 4]}, 2, "0 → 1 → 4."),
            ({"nums": [2, 3, 0, 1, 4]}, 2, ""),
        ],
        tests=[({"nums": [0]}, 0)],
        approach="Think in layers (like BFS): all indices reachable with `j` jumps form a range. Scan the current range, computing the farthest index the next jump could reach; when you pass the end of the range, count a jump and move to the next range.",
        explanation="Within one range every index costs the same number of jumps, so only the farthest reach of the next layer matters.",
        time="O(n)", space="O(1)",
        code="""
        def jump(nums: list[int]) -> int:
            jumps = current_end = farthest = 0
            for i in range(len(nums) - 1):
                farthest = max(farthest, i + nums[i])
                if i == current_end:
                    jumps += 1
                    current_end = farthest
            return jumps
        """,
    ),
    P(
        "circular-fuel-route", "Circular Route With Fuel Stops", "medium", ["greedy"],
        statement="Stations sit on a circular road. At station `i` you collect `gas[i]` fuel, and driving to station `i + 1` costs `cost[i]`. Starting with an empty tank, return the index of the station from which you can complete the circuit, or `-1` if none works. The answer is unique if it exists.",
        inputs="- `gas`, `cost`: lists of the same length",
        output="The starting index or `-1`.",
        constraints="- `1 <= n <= 10^5`",
        examples=[
            ({"gas": [1, 2, 3, 4, 5], "cost": [3, 4, 5, 1, 2]}, 3, ""),
            ({"gas": [2, 3, 4], "cost": [3, 4, 3]}, -1, "Total fuel 9 < total cost 10."),
        ],
        approach="If total gas < total cost, return −1. Otherwise scan once with a running tank; whenever it drops below zero, no station from the current start up to here can work, so restart from the next station.",
        explanation="If you can't get from start `s` to station `i`, starting at any station between them leaves you with even less fuel at `i`. With enough total fuel, the last restart point succeeds.",
        time="O(n)", space="O(1)",
        code="""
        def can_complete_circuit(gas: list[int], cost: list[int]) -> int:
            if sum(gas) < sum(cost):
                return -1
            start = tank = 0
            for i in range(len(gas)):
                tank += gas[i] - cost[i]
                if tank < 0:
                    start, tank = i + 1, 0
            return start
        """,
    ),
    P(
        "partition-labels", "Partition Into Letter-Exclusive Parts", "medium", ["greedy", "hash-map"],
        statement="Split `s` into as many parts as possible so that each letter appears in at most one part. Return the sizes of the parts in order.",
        inputs="- `s`: a lowercase string",
        output="A list of part lengths.",
        constraints="- `1 <= s.length <= 500`",
        examples=[
            ({"s": "ababcbacadefegdehijhklij"}, [9, 7, 8], "'ababcbaca', 'defegde', 'hijhklij'."),
            ({"s": "eccbbbbdec"}, [10], "e appears at both ends."),
        ],
        approach="Record the last index of every letter. Scan left to right, extending the current part's end to the last occurrence of each letter seen; when the scan reaches that end, close the part.",
        explanation="A part must reach at least the last occurrence of every letter it contains; cutting as soon as that is satisfied gives the most parts.",
        time="O(n)", space="O(26)",
        code="""
        def partition_labels(s: str) -> list[int]:
            last = {ch: i for i, ch in enumerate(s)}
            sizes, start, end = [], 0, 0
            for i, ch in enumerate(s):
                end = max(end, last[ch])
                if i == end:
                    sizes.append(end - start + 1)
                    start = i + 1
            return sizes
        """,
    ),
    P(
        "remove-overlapping-intervals", "Fewest Intervals to Remove", "medium", ["greedy", "sorting"],
        statement="Return the minimum number of intervals to remove so that the rest don't overlap. Intervals that only touch (`[1, 2]` and `[2, 3]`) don't overlap.",
        inputs="- `intervals`: a list of `[start, end]` with `start < end`",
        output="The minimum number of removals.",
        constraints="- `1 <= intervals.length <= 10^5`",
        examples=[
            ({"intervals": [[1, 2], [2, 3], [3, 4], [1, 3]]}, 1, "Remove [1, 3]."),
            ({"intervals": [[1, 2], [1, 2], [1, 2]]}, 2, ""),
        ],
        tests=[({"intervals": [[1, 2], [2, 3]]}, 0)],
        approach="Sort by end time. Keep an interval if it starts at or after the end of the last kept one; otherwise remove it.",
        explanation="Keeping the interval that finishes earliest leaves the most room for the rest — the classic activity-selection argument. Removals = total − kept.",
        time="O(n log n)", space="O(1) besides sorting",
        code="""
        def erase_overlap_intervals(intervals: list[list[int]]) -> int:
            removed, last_end = 0, float("-inf")
            for start, end in sorted(intervals, key=lambda iv: iv[1]):
                if start >= last_end:
                    last_end = end
                else:
                    removed += 1
            return removed
        """,
    ),
    P(
        "fewest-arrows", "Fewest Arrows to Burst All Balloons", "medium", ["greedy", "sorting"],
        statement="Each balloon spans `[start, end]` horizontally. A vertical arrow shot at `x` bursts every balloon with `start <= x <= end`. Return the minimum number of arrows to burst all balloons.",
        inputs="- `points`: a list of `[start, end]` spans",
        output="The minimum number of arrows.",
        constraints="- `1 <= points.length <= 10^5`",
        examples=[
            ({"points": [[10, 16], [2, 8], [1, 6], [7, 12]]}, 2, "Shoot at 6 and at 12."),
            ({"points": [[1, 2], [3, 4], [5, 6], [7, 8]]}, 4, ""),
        ],
        tests=[({"points": [[1, 2], [2, 3], [3, 4], [4, 5]]}, 2)],
        approach="Sort by end. Shoot an arrow at the end of the first balloon; it bursts every balloon starting at or before that point. The next balloon starting after it needs a new arrow at its own end.",
        explanation="Shooting as far right as possible while still hitting the earliest-ending balloon covers the most other balloons.",
        time="O(n log n)", space="O(1) besides sorting",
        code="""
        def find_min_arrows(points: list[list[int]]) -> int:
            arrows, x = 0, float("-inf")
            for start, end in sorted(points, key=lambda p: p[1]):
                if start > x:
                    arrows += 1
                    x = end
            return arrows
        """,
    ),
    P(
        "fair-candy", "Fair Candy Distribution", "hard", ["greedy"],
        statement="Children stand in a line with `ratings`. Each child gets at least one candy, and a child with a higher rating than a neighbour must get more candy than that neighbour. Return the minimum total candy.",
        inputs="- `ratings`: a list of integers",
        output="The minimum number of candies.",
        constraints="- `1 <= ratings.length <= 2 × 10^4`",
        examples=[
            ({"ratings": [1, 0, 2]}, 5, "2, 1, 2."),
            ({"ratings": [1, 2, 2]}, 4, "1, 2, 1 — equal neighbours have no constraint."),
        ],
        tests=[({"ratings": [1, 3, 4, 5, 2]}, 11)],
        approach="Two passes. Left to right: if a child beats the left neighbour, give one more than them. Right to left: if a child beats the right neighbour, make sure they have at least one more than them.",
        explanation="Each pass satisfies one side's constraints with the fewest candies; taking the maximum of both keeps both satisfied without adding anything unnecessary.",
        time="O(n)", space="O(n)",
        code="""
        def candy(ratings: list[int]) -> int:
            n = len(ratings)
            candies = [1] * n
            for i in range(1, n):
                if ratings[i] > ratings[i - 1]:
                    candies[i] = candies[i - 1] + 1
            for i in range(n - 2, -1, -1):
                if ratings[i] > ratings[i + 1]:
                    candies[i] = max(candies[i], candies[i + 1] + 1)
            return sum(candies)
        """,
    ),
    P(
        "fewest-refuelling-stops", "Fewest Refuelling Stops", "hard", ["greedy"],
        statement="A car drives towards `target` miles away with `start_fuel` litres (1 litre = 1 mile). `stations[i] = [position, fuel]` is a station offering that much fuel. Return the minimum number of stops to reach the target, or `-1` if impossible.",
        inputs="- `target`: the distance\n- `start_fuel`: initial fuel\n- `stations`: `[position, fuel]` sorted by position",
        output="The minimum number of stops, or `-1`.",
        constraints="- `1 <= target, start_fuel <= 10^9`\n- `0 <= stations.length <= 500`",
        examples=[
            ({"target": 100, "start_fuel": 10, "stations": [[10, 60], [20, 30], [30, 30], [60, 40]]}, 2, "Stop at 10 (→ 60 litres) and 60 (→ +40)."),
            ({"target": 100, "start_fuel": 1, "stations": [[10, 100]]}, -1, "You can't reach the first station."),
        ],
        tests=[({"target": 1, "start_fuel": 1, "stations": []}, 0)],
        approach="Drive as far as the fuel allows, pushing every station passed onto a max-heap of fuel amounts. When the tank can't reach the next point, retroactively \"stop\" at the passed station with the most fuel. If the heap is empty, it's impossible.",
        explanation="Deciding stops lazily lets you always choose the best station among those you have passed; any optimal plan can be rearranged into this one.",
        time="O(n log n)", space="O(n)",
        code="""
        import heapq

        def min_refuel_stops(target: int, start_fuel: int, stations: list[list[int]]) -> int:
            heap, fuel, stops, i = [], start_fuel, 0, 0
            while fuel < target:
                while i < len(stations) and stations[i][0] <= fuel:
                    heapq.heappush(heap, -stations[i][1])
                    i += 1
                if not heap:
                    return -1
                fuel += -heapq.heappop(heap)
                stops += 1
            return stops
        """,
    ),
    P(
        "patch-the-array", "Patch the Array to Cover a Range", "hard", ["greedy"],
        statement="Given a sorted list of positive integers `nums`, add (patch) as few numbers as possible so that every integer from `1` to `n` can be written as the sum of some elements of the list. Return the number of patches.",
        inputs="- `nums`: a sorted list of positive integers\n- `n`: the upper end of the range",
        output="The minimum number of patches.",
        constraints="- `1 <= nums.length <= 1000`\n- `1 <= n <= 2^31 - 1`",
        examples=[
            ({"nums": [1, 3], "n": 6}, 1, "Add 2: every value 1–6 can then be formed."),
            ({"nums": [1, 5, 10], "n": 20}, 2, "Add 2 and 4."),
        ],
        tests=[({"nums": [1, 2, 2], "n": 5}, 0)],
        approach="Track `miss`, the smallest sum you can't make yet (all of `1 … miss−1` are possible). If the next number is ≤ `miss`, use it: `miss += num`. Otherwise patch with `miss` itself, which doubles the reach.",
        explanation="Adding `miss` is the largest number that keeps the covered range gap-free, so it extends coverage the most per patch.",
        time="O(len(nums) + log n)", space="O(1)",
        code="""
        def min_patches(nums: list[int], n: int) -> int:
            miss, i, patches = 1, 0, 0
            while miss <= n:
                if i < len(nums) and nums[i] <= miss:
                    miss += nums[i]
                    i += 1
                else:
                    miss += miss
                    patches += 1
            return patches
        """,
    ),
]
