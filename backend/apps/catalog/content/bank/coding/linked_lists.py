import textwrap

from . import P

TOPIC = "linked-lists"

NODE = """
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
"""

LIST_IO = "Lists are shown as `1 → 2 → 3`; `(empty)` is `None`."


def L(code: str) -> str:
    return NODE.strip() + "\n\n\n" + textwrap.dedent(code).strip()


PROBLEMS = [
    P(
        "middle-of-list", "Middle of a Linked List", "easy", ["fast-slow-pointers"],
        statement="Return the middle node of a singly linked list. If there are two middle nodes, return the **second** one.",
        inputs=f"- `head`: the first node of a non-empty list. {LIST_IO}",
        output="The middle node (shown as the list from that node onward).",
        constraints="- `1 <= number of nodes <= 100`",
        examples=[
            ({"head": [1, 2, 3, 4, 5]}, [3, 4, 5], "The middle node is 3."),
            ({"head": [1, 2, 3, 4, 5, 6]}, [4, 5, 6], "Two middles (3 and 4); return the second."),
        ],
        types={"head": "list"}, returns="list",
        approach="Move a `slow` pointer one step and a `fast` pointer two steps at a time. When `fast` reaches the end, `slow` is in the middle.",
        explanation="`fast` always covers twice the distance of `slow`, so when `fast` has walked the whole list, `slow` has walked half of it — in one pass, without counting first.",
        time="O(n)", space="O(1)",
        code=L("""
        def middle_node(head: ListNode) -> ListNode:
            slow = fast = head
            while fast and fast.next:
                slow = slow.next
                fast = fast.next.next
            return slow
        """),
    ),
    P(
        "dedupe-sorted-list", "Remove Duplicates From a Sorted List", "easy", [],
        statement="The linked list is sorted. Delete nodes so that each value appears only once, and return the head.",
        inputs=f"- `head`: the first node of a sorted list (possibly empty). {LIST_IO}",
        output="The head of the de-duplicated list.",
        constraints="- `0 <= number of nodes <= 300`",
        examples=[
            ({"head": [1, 1, 2]}, [1, 2], ""),
            ({"head": [1, 1, 2, 3, 3]}, [1, 2, 3], ""),
        ],
        tests=[({"head": []}, [])],
        types={"head": "list"}, returns="list",
        approach="Walk the list. While the next node has the same value as the current one, skip it by re-pointing `current.next`; otherwise move forward.",
        explanation="Sorting puts equal values next to each other, so comparing neighbours finds every duplicate.",
        time="O(n)", space="O(1)",
        code=L("""
        def delete_duplicates(head: ListNode | None) -> ListNode | None:
            current = head
            while current and current.next:
                if current.next.val == current.val:
                    current.next = current.next.next
                else:
                    current = current.next
            return head
        """),
    ),
    P(
        "list-is-palindrome", "Is the List a Palindrome?", "easy", ["fast-slow-pointers", "in-place-reversal"],
        statement="Return `true` if the values of the singly linked list read the same forwards and backwards. Try for O(1) extra space.",
        inputs=f"- `head`: the first node of a non-empty list. {LIST_IO}",
        output="`true` or `false`.",
        constraints="- `1 <= number of nodes <= 10^5`\n- `0 <= val <= 9`",
        examples=[
            ({"head": [1, 2, 2, 1]}, True, ""),
            ({"head": [1, 2]}, False, ""),
        ],
        tests=[({"head": [1, 2, 3, 2, 1]}, True), ({"head": [7]}, True)],
        types={"head": "list"},
        approach="Find the middle with slow/fast pointers, reverse the second half in place, then compare the first half with the reversed second half node by node.",
        explanation="Both halves are walked once and nothing is copied. (In production you would reverse the second half back afterwards to leave the list unchanged.)",
        time="O(n)", space="O(1)",
        code=L("""
        def is_palindrome(head: ListNode) -> bool:
            slow = fast = head
            while fast and fast.next:
                slow, fast = slow.next, fast.next.next
            prev = None
            while slow:
                slow.next, prev, slow = prev, slow, slow.next
            left, right = head, prev
            while right:
                if left.val != right.val:
                    return False
                left, right = left.next, right.next
            return True
        """),
    ),
    P(
        "remove-value-from-list", "Remove Every Node With a Value", "easy", [],
        statement="Remove all nodes whose value equals `val` and return the new head.",
        inputs=f"- `head`: the first node of a list (possibly empty). {LIST_IO}\n- `val`: the value to remove",
        output="The head of the remaining list.",
        constraints="- `0 <= number of nodes <= 10^4`",
        examples=[
            ({"head": [1, 2, 6, 3, 4, 5, 6], "val": 6}, [1, 2, 3, 4, 5], ""),
            ({"head": [7, 7, 7], "val": 7}, [], "Every node is removed."),
        ],
        types={"head": "list"}, returns="list",
        approach="Put a dummy node before the head so the first node is no different from the others. Walk from the dummy: if the next node has value `val`, unlink it; otherwise advance.",
        explanation="Without the dummy you would need special code for removing heads repeatedly, as in the second example.",
        time="O(n)", space="O(1)",
        code=L("""
        def remove_elements(head: ListNode | None, val: int) -> ListNode | None:
            dummy = ListNode(0, head)
            current = dummy
            while current.next:
                if current.next.val == val:
                    current.next = current.next.next
                else:
                    current = current.next
            return dummy.next
        """),
    ),
    P(
        "reverse-a-section", "Reverse a Section of a List", "medium", ["in-place-reversal"],
        statement="Reverse the nodes from position `left` to position `right` (1-indexed, inclusive) in one pass, and return the head.",
        inputs=f"- `head`: the first node of a list. {LIST_IO}\n- `left`, `right`: positions with `1 <= left <= right <= n`",
        output="The head of the list with that section reversed.",
        constraints="- `1 <= n <= 500`",
        examples=[
            ({"head": [1, 2, 3, 4, 5], "left": 2, "right": 4}, [1, 4, 3, 2, 5], ""),
            ({"head": [5], "left": 1, "right": 1}, [5], ""),
        ],
        tests=[({"head": [3, 5], "left": 1, "right": 2}, [5, 3])],
        types={"head": "list"}, returns="list",
        approach="Walk a pointer `before` to the node just before position `left` (a dummy head handles `left = 1`). Then repeatedly take the node after the section's current first node and move it to the front of the section — `right − left` times.",
        explanation="Each move re-points three links and grows the reversed prefix of the section by one, so the section is reversed without a second pass.",
        time="O(n)", space="O(1)",
        code=L("""
        def reverse_between(head: ListNode, left: int, right: int) -> ListNode:
            dummy = ListNode(0, head)
            before = dummy
            for _ in range(left - 1):
                before = before.next
            first = before.next
            for _ in range(right - left):
                moved = first.next
                first.next = moved.next
                moved.next = before.next
                before.next = moved
            return dummy.next
        """),
    ),
    P(
        "rotate-list", "Rotate a List", "medium", [],
        statement="Rotate the linked list to the right by `k` places (the last `k` nodes move to the front) and return the new head.",
        inputs=f"- `head`: the first node of a list (possibly empty). {LIST_IO}\n- `k`: a non-negative integer",
        output="The head of the rotated list.",
        constraints="- `0 <= number of nodes <= 500`\n- `0 <= k <= 2 × 10^9`",
        examples=[
            ({"head": [1, 2, 3, 4, 5], "k": 2}, [4, 5, 1, 2, 3], ""),
            ({"head": [0, 1, 2], "k": 4}, [2, 0, 1], "Rotating 4 times = rotating once."),
        ],
        tests=[({"head": [], "k": 3}, [])],
        types={"head": "list"}, returns="list",
        approach="Find the length `n` and the tail. Join the tail to the head to make a ring, walk `n − k % n` steps to find the new tail, and break the ring after it.",
        explanation="Taking `k % n` avoids walking around the ring many times when `k` is huge.",
        time="O(n)", space="O(1)",
        code=L("""
        def rotate_right(head: ListNode | None, k: int) -> ListNode | None:
            if not head or not head.next:
                return head
            n, tail = 1, head
            while tail.next:
                tail = tail.next
                n += 1
            tail.next = head  # ring
            new_tail = head
            for _ in range(n - k % n - 1):
                new_tail = new_tail.next
            new_head = new_tail.next
            new_tail.next = None
            return new_head
        """),
    ),
    P(
        "odd-then-even-positions", "Odd Positions, Then Even", "medium", [],
        statement="Group the nodes at odd positions (1st, 3rd, …) first, followed by the nodes at even positions, keeping the relative order inside each group. Use O(1) extra space.",
        inputs=f"- `head`: the first node of a list (possibly empty). {LIST_IO}",
        output="The head of the regrouped list.",
        constraints="- `0 <= number of nodes <= 10^4`",
        examples=[
            ({"head": [1, 2, 3, 4, 5]}, [1, 3, 5, 2, 4], ""),
            ({"head": [2, 1, 3, 5, 6, 4, 7]}, [2, 3, 6, 7, 1, 5, 4], "Positions, not values, decide the group."),
        ],
        types={"head": "list"}, returns="list",
        approach="Keep two chains: `odd` starting at the head and `even` starting at the second node. Alternately link each odd node to the next odd node and each even node to the next even node, then attach the even chain after the odd chain.",
        explanation="Each node is re-linked once and no new nodes are created.",
        time="O(n)", space="O(1)",
        code=L("""
        def odd_even_list(head: ListNode | None) -> ListNode | None:
            if not head:
                return head
            odd, even = head, head.next
            even_head = even
            while even and even.next:
                odd.next = even.next
                odd = odd.next
                even.next = odd.next
                even = even.next
            odd.next = even_head
            return head
        """),
    ),
    P(
        "add-digit-lists", "Add Two Numbers Stored as Lists", "medium", [],
        statement="Two non-negative integers are stored as linked lists of digits in **reverse** order (the ones digit first). Return their sum as a list in the same format.",
        inputs=f"- `l1`, `l2`: lists of digits, least significant first. {LIST_IO}",
        output="The sum as a reversed digit list.",
        constraints="- `1 <= number of nodes <= 100`\n- No leading zeros except the number 0",
        examples=[
            ({"l1": [2, 4, 3], "l2": [5, 6, 4]}, [7, 0, 8], "342 + 465 = 807."),
            ({"l1": [9, 9, 9, 9], "l2": [9, 9]}, [8, 9, 0, 0, 1], "9999 + 99 = 10098."),
        ],
        types={"l1": "list", "l2": "list"}, returns="list",
        approach="Walk both lists together like column addition: add the two digits and the carry, append `total % 10` as a new node, carry `total // 10`. Continue while either list or the carry remains.",
        explanation="Storing the digits in reverse puts the ones column first, which is exactly the order addition needs.",
        time="O(max(m, n))", space="O(max(m, n)) for the result",
        code=L("""
        def add_two_numbers(l1: ListNode | None, l2: ListNode | None) -> ListNode:
            dummy = tail = ListNode()
            carry = 0
            while l1 or l2 or carry:
                total = carry + (l1.val if l1 else 0) + (l2.val if l2 else 0)
                carry, digit = divmod(total, 10)
                tail.next = ListNode(digit)
                tail = tail.next
                l1 = l1.next if l1 else None
                l2 = l2.next if l2 else None
            return dummy.next
        """),
    ),
    P(
        "partition-list-around-value", "Partition a List Around a Value", "medium", [],
        statement="Rearrange the list so all nodes with values **less than** `x` come before nodes with values greater than or equal to `x`, keeping the original relative order within each part.",
        inputs=f"- `head`: the first node of a list (possibly empty). {LIST_IO}\n- `x`: the pivot value",
        output="The head of the partitioned list.",
        constraints="- `0 <= number of nodes <= 200`",
        examples=[
            ({"head": [1, 4, 3, 2, 5, 2], "x": 3}, [1, 2, 2, 4, 3, 5], ""),
            ({"head": [2, 1], "x": 2}, [1, 2], ""),
        ],
        types={"head": "list"}, returns="list",
        approach="Build two chains with dummy heads — `less` and `rest` — appending each node to the right one. Finally link `less` to `rest` and terminate `rest`.",
        explanation="Appending in order keeps the original order inside each part (a stable partition). Ending the `rest` chain with `None` prevents a cycle from the old links.",
        time="O(n)", space="O(1)",
        code=L("""
        def partition(head: ListNode | None, x: int) -> ListNode | None:
            less_head = less = ListNode()
            rest_head = rest = ListNode()
            while head:
                if head.val < x:
                    less.next, less = head, head
                else:
                    rest.next, rest = head, head
                head = head.next
            rest.next = None
            less.next = rest_head.next
            return less_head.next
        """),
    ),
    P(
        "swap-adjacent-pairs", "Swap Adjacent Pairs", "medium", [],
        statement="Swap every two adjacent nodes and return the head. Change the links, not the values.",
        inputs=f"- `head`: the first node of a list (possibly empty). {LIST_IO}",
        output="The head of the list with pairs swapped.",
        constraints="- `0 <= number of nodes <= 100`",
        examples=[
            ({"head": [1, 2, 3, 4]}, [2, 1, 4, 3], ""),
            ({"head": [1, 2, 3]}, [2, 1, 3], "The last node has no partner."),
        ],
        tests=[({"head": []}, [])],
        types={"head": "list"}, returns="list",
        approach="With a dummy before the head, look at the next two nodes `a` and `b`; re-point `prev → b → a → (rest)` and move `prev` to `a`.",
        explanation="Three link changes per pair; the dummy makes the first pair no different from the others.",
        time="O(n)", space="O(1)",
        code=L("""
        def swap_pairs(head: ListNode | None) -> ListNode | None:
            dummy = prev = ListNode(0, head)
            while prev.next and prev.next.next:
                a, b = prev.next, prev.next.next
                prev.next, a.next, b.next = b, b.next, a
                prev = a
            return dummy.next
        """),
    ),
    P(
        "reverse-in-groups", "Reverse Nodes in Groups of k", "hard", ["in-place-reversal"],
        statement="Reverse the nodes of the list `k` at a time and return the head. If fewer than `k` nodes remain at the end, leave them as they are. Use O(1) extra space.",
        inputs=f"- `head`: the first node of a list. {LIST_IO}\n- `k`: the group size",
        output="The head of the list after reversing each full group.",
        constraints="- `1 <= k <= n <= 5000`",
        examples=[
            ({"head": [1, 2, 3, 4, 5], "k": 2}, [2, 1, 4, 3, 5], ""),
            ({"head": [1, 2, 3, 4, 5], "k": 3}, [3, 2, 1, 4, 5], "Only one full group of 3."),
        ],
        tests=[({"head": [1, 2, 3, 4], "k": 4}, [4, 3, 2, 1]), ({"head": [1, 2], "k": 1}, [1, 2])],
        types={"head": "list"}, returns="list",
        approach="Keep `group_prev`, the node before the current group. Check that `k` nodes follow it; if not, stop. Reverse those `k` nodes in place, connect `group_prev` to the new group head and the old group head (now the tail) to the next group, and continue from that tail.",
        explanation="Each node is visited a constant number of times: once while counting and once while reversing.",
        time="O(n)", space="O(1)",
        code=L("""
        def reverse_k_group(head: ListNode, k: int) -> ListNode:
            dummy = ListNode(0, head)
            group_prev = dummy
            while True:
                kth = group_prev
                for _ in range(k):
                    kth = kth.next
                    if kth is None:
                        return dummy.next
                group_next = kth.next
                prev, curr = group_next, group_prev.next
                while curr is not group_next:
                    curr.next, prev, curr = prev, curr, curr.next
                old_head = group_prev.next
                group_prev.next = kth
                group_prev = old_head
        """),
    ),
]
