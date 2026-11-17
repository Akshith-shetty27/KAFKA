import textwrap

from . import P

TOPIC = "trees-and-graphs"

NODE = """
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
"""

TREE_IO = "Trees are shown in level order with `null` for missing children, e.g. `[3, 9, 20, null, null, 15, 7]`."


def T(code: str) -> str:
    return NODE.strip() + "\n\n\n" + textwrap.dedent(code).strip()


BIG_TREE = [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1]
BST = [6, 2, 8, 0, 4, 7, 9, None, None, 3, 5]
WORDS = ["hot", "dot", "dog", "lot", "log", "cog"]

PROBLEMS = [
    P(
        "mirror-a-tree", "Mirror a Binary Tree", "easy", ["dfs"],
        statement="Mirror (invert) a binary tree: swap the left and right children of every node. Return the root.",
        inputs=f"- `root`: the root of a binary tree (possibly empty). {TREE_IO}",
        output="The root of the mirrored tree.",
        constraints="- `0 <= number of nodes <= 100`",
        examples=[
            ({"root": [4, 2, 7, 1, 3, 6, 9]}, [4, 7, 2, 9, 6, 3, 1], ""),
            ({"root": [2, 1, 3]}, [2, 3, 1], ""),
        ],
        tests=[({"root": []}, [])],
        types={"root": "tree"}, returns="tree",
        approach="Recursively mirror the left and right subtrees, then swap them.",
        explanation="Every node is visited once; the recursion depth is the tree height.",
        time="O(n)", space="O(h)",
        code=T("""
        def invert_tree(root: TreeNode | None) -> TreeNode | None:
            if root:
                root.left, root.right = invert_tree(root.right), invert_tree(root.left)
            return root
        """),
    ),
    P(
        "identical-trees", "Are Two Trees Identical?", "easy", ["dfs"],
        statement="Return `true` if binary trees `p` and `q` have the same shape and the same values in every node.",
        inputs=f"- `p`, `q`: roots of two binary trees. {TREE_IO}",
        output="`true` or `false`.",
        constraints="- `0 <= number of nodes <= 100`",
        examples=[
            ({"p": [1, 2, 3], "q": [1, 2, 3]}, True, ""),
            ({"p": [1, 2], "q": [1, None, 2]}, False, "The 2 is a left child in one tree and a right child in the other."),
        ],
        types={"p": "tree", "q": "tree"},
        approach="Compare recursively: both empty → equal; one empty or values differ → not equal; otherwise compare the left subtrees and the right subtrees.",
        explanation="The recursion walks both trees in lockstep and stops at the first difference.",
        time="O(n)", space="O(h)",
        code=T("""
        def is_same_tree(p: TreeNode | None, q: TreeNode | None) -> bool:
            if p is None or q is None:
                return p is q
            return p.val == q.val and is_same_tree(p.left, q.left) and is_same_tree(p.right, q.right)
        """),
    ),
    P(
        "symmetric-tree", "Is the Tree Symmetric?", "easy", ["dfs"],
        statement="Return `true` if a binary tree is a mirror image of itself around its centre.",
        inputs=f"- `root`: the root of a non-empty binary tree. {TREE_IO}",
        output="`true` or `false`.",
        constraints="- `1 <= number of nodes <= 1000`",
        examples=[
            ({"root": [1, 2, 2, 3, 4, 4, 3]}, True, ""),
            ({"root": [1, 2, 2, None, 3, None, 3]}, False, "Both 3s are right children."),
        ],
        types={"root": "tree"},
        approach="Two subtrees are mirrors if their roots are equal, the left of one mirrors the right of the other, and vice versa. Check whether the root's left and right subtrees are mirrors.",
        explanation="This is the identical-trees check with the children crossed over.",
        time="O(n)", space="O(h)",
        code=T("""
        def is_symmetric(root: TreeNode) -> bool:
            def mirror(a: TreeNode | None, b: TreeNode | None) -> bool:
                if a is None or b is None:
                    return a is b
                return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)

            return mirror(root.left, root.right)
        """),
    ),
    P(
        "root-to-leaf-sum", "Root-to-Leaf Path With a Given Sum", "easy", ["dfs"],
        statement="Return `true` if the tree has a path from the root down to a **leaf** whose values add up to `target`.",
        inputs=f"- `root`: the root of a binary tree (possibly empty). {TREE_IO}\n- `target`: an integer",
        output="`true` or `false`.",
        constraints="- `0 <= number of nodes <= 5000`",
        examples=[
            ({"root": BIG_TREE, "target": 22}, True, "5 → 4 → 11 → 2."),
            ({"root": [1, 2, 3], "target": 5}, False, "The paths sum to 3 and 4."),
        ],
        tests=[({"root": [], "target": 0}, False)],
        types={"root": "tree"},
        approach="Subtract each node's value from the target on the way down. At a leaf, check whether what remains is zero.",
        explanation="The path must end at a leaf, so checking only at leaves avoids counting partial paths. An empty tree has no paths at all.",
        time="O(n)", space="O(h)",
        code=T("""
        def has_path_sum(root: TreeNode | None, target: int) -> bool:
            if root is None:
                return False
            remaining = target - root.val
            if root.left is None and root.right is None:
                return remaining == 0
            return has_path_sum(root.left, remaining) or has_path_sum(root.right, remaining)
        """),
    ),
    P(
        "valid-search-tree", "Is It a Valid Binary Search Tree?", "medium", ["dfs"],
        statement="Return `true` if the binary tree is a valid binary search tree: every node's value is greater than all values in its left subtree and smaller than all values in its right subtree.",
        inputs=f"- `root`: the root of a non-empty binary tree. {TREE_IO}",
        output="`true` or `false`.",
        constraints="- `1 <= number of nodes <= 10^4`",
        examples=[
            ({"root": [2, 1, 3]}, True, ""),
            ({"root": [5, 1, 4, None, None, 3, 6]}, False, "4 is in the right subtree of 5 but smaller than 5."),
        ],
        tests=[({"root": [5, 4, 6, None, None, 3, 7]}, False)],
        types={"root": "tree"},
        approach="Pass down the open range `(low, high)` each node must lie in. Going left tightens the upper bound to the parent's value; going right tightens the lower bound.",
        explanation="Checking only a node against its direct children misses violations deeper down (third test: 3 sits under 6 but is less than the root 5). The range carries every ancestor's constraint.",
        time="O(n)", space="O(h)",
        code=T("""
        def is_valid_bst(root: TreeNode | None, low=float("-inf"), high=float("inf")) -> bool:
            if root is None:
                return True
            if not low < root.val < high:
                return False
            return is_valid_bst(root.left, low, root.val) and is_valid_bst(root.right, root.val, high)
        """),
    ),
    P(
        "lowest-common-ancestor-bst", "Lowest Common Ancestor in a BST", "medium", [],
        statement="In a binary search tree, return the value of the lowest common ancestor of the nodes with values `p` and `q` (a node may be its own ancestor). Both values exist in the tree.",
        inputs=f"- `root`: the root of a BST. {TREE_IO}\n- `p`, `q`: two values in the tree",
        output="The value of the lowest common ancestor.",
        constraints="- `2 <= number of nodes <= 10^5`\n- All values are distinct",
        examples=[
            ({"root": BST, "p": 2, "q": 8}, 6, "2 and 8 are on opposite sides of 6."),
            ({"root": BST, "p": 2, "q": 4}, 2, "2 is an ancestor of 4."),
        ],
        types={"root": "tree"},
        approach="Start at the root. If both values are smaller, the ancestor is in the left subtree; if both are larger, in the right. Otherwise the current node is where the paths split — the answer.",
        explanation="The BST ordering tells you which side each value is on without searching, so the walk follows a single path.",
        time="O(h)", space="O(1)",
        code=T("""
        def lowest_common_ancestor(root: TreeNode, p: int, q: int) -> int:
            node = root
            while node:
                if p < node.val and q < node.val:
                    node = node.left
                elif p > node.val and q > node.val:
                    node = node.right
                else:
                    return node.val
        """),
    ),
    P(
        "right-side-view", "What You See From the Right", "medium", ["bfs"],
        statement="Standing on the right side of a binary tree, return the values of the nodes you can see, from top to bottom (the last node of each level).",
        inputs=f"- `root`: the root of a binary tree (possibly empty). {TREE_IO}",
        output="A list with one value per level.",
        constraints="- `0 <= number of nodes <= 100`",
        examples=[
            ({"root": [1, 2, 3, None, 5, None, 4]}, [1, 3, 4], ""),
            ({"root": [1, 2, 3, 4]}, [1, 3, 4], "4 is visible because nothing is to its right on that level."),
        ],
        tests=[({"root": []}, [])],
        types={"root": "tree"},
        approach="Level-order traversal (BFS) with a queue, processing one level at a time; record the last node of each level.",
        explanation="BFS visits each level left to right, so the last node dequeued for a level is the rightmost one.",
        time="O(n)", space="O(width)",
        code=T("""
        from collections import deque

        def right_side_view(root: TreeNode | None) -> list[int]:
            if root is None:
                return []
            view, queue = [], deque([root])
            while queue:
                for i in range(len(queue)):
                    node = queue.popleft()
                    if node.left:
                        queue.append(node.left)
                    if node.right:
                        queue.append(node.right)
                view.append(node.val)
            return view
        """),
    ),
    P(
        "spreading-rot", "Minutes Until Everything Rots", "medium", ["bfs"],
        statement="In a grid, `0` is empty, `1` a fresh orange and `2` a rotten orange. Every minute, fresh oranges next to a rotten one (up, down, left, right) rot. Return the minutes until no fresh orange remains, or `-1` if some never rot.",
        inputs="- `grid`: an `m × n` list of 0s, 1s and 2s",
        output="The number of minutes, or `-1`.",
        constraints="- `1 <= m, n <= 10`",
        examples=[
            ({"grid": [[2, 1, 1], [1, 1, 0], [0, 1, 1]]}, 4, ""),
            ({"grid": [[2, 1, 1], [0, 1, 1], [1, 0, 1]]}, -1, "The bottom-left orange is isolated."),
        ],
        tests=[({"grid": [[0, 2]]}, 0)],
        approach="Multi-source BFS: put every rotten orange in the queue at minute 0 and spread level by level, counting fresh oranges as they rot. If any fresh oranges remain at the end, return −1.",
        explanation="Starting from all rotten oranges at once makes each BFS level exactly one minute.",
        time="O(m·n)", space="O(m·n)",
        code="""
        from collections import deque

        def oranges_rotting(grid: list[list[int]]) -> int:
            rows, cols = len(grid), len(grid[0])
            queue, fresh = deque(), 0
            for r in range(rows):
                for c in range(cols):
                    if grid[r][c] == 2:
                        queue.append((r, c))
                    elif grid[r][c] == 1:
                        fresh += 1
            minutes = 0
            while queue and fresh:
                minutes += 1
                for _ in range(len(queue)):
                    r, c = queue.popleft()
                    for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                            grid[nr][nc] = 2
                            fresh -= 1
                            queue.append((nr, nc))
            return -1 if fresh else minutes
        """,
    ),
    P(
        "count-connected-groups", "Count Connected Groups", "medium", ["dfs"],
        statement="A graph has `n` nodes labelled `0 … n−1` and undirected `edges`. Return the number of connected components.",
        inputs="- `n`: the number of nodes\n- `edges`: a list of `[a, b]` pairs",
        output="The number of connected components.",
        constraints="- `1 <= n <= 2000`\n- `0 <= edges.length <= 5000`",
        examples=[
            ({"n": 5, "edges": [[0, 1], [1, 2], [3, 4]]}, 2, "{0, 1, 2} and {3, 4}."),
            ({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]]}, 1, ""),
        ],
        tests=[({"n": 3, "edges": []}, 3)],
        approach="Build an adjacency list. For every node not yet visited, start a DFS that marks its whole component, and count how many times you start one.",
        explanation="Each DFS covers exactly one component, and every node and edge is processed once. (A union–find structure is an equally good alternative.)",
        time="O(n + e)", space="O(n + e)",
        code="""
        def count_components(n: int, edges: list[list[int]]) -> int:
            graph = [[] for _ in range(n)]
            for a, b in edges:
                graph[a].append(b)
                graph[b].append(a)
            seen, components = [False] * n, 0
            for start in range(n):
                if seen[start]:
                    continue
                components += 1
                stack, seen[start] = [start], True
                while stack:
                    node = stack.pop()
                    for nxt in graph[node]:
                        if not seen[nxt]:
                            seen[nxt] = True
                            stack.append(nxt)
            return components
        """,
    ),
    P(
        "word-ladder-length", "Shortest Word Ladder", "hard", ["bfs"],
        statement="Transform `begin` into `end` by changing **one letter at a time**; every intermediate word must be in `words`. Return the number of words in the shortest such sequence (including `begin` and `end`), or `0` if impossible.",
        inputs="- `begin`, `end`: words of equal length\n- `words`: the allowed dictionary (`begin` need not be in it)",
        output="The length of the shortest ladder, or `0`.",
        constraints="- `1 <= word length <= 10`\n- `1 <= words.length <= 5000`",
        examples=[
            ({"begin": "hit", "end": "cog", "words": WORDS}, 5, "hit → hot → dot → dog → cog."),
            ({"begin": "hit", "end": "cog", "words": WORDS[:-1]}, 0, "cog isn't in the dictionary."),
        ],
        approach="BFS over words, where neighbours differ by one letter. Generate neighbours by trying all 26 letters at every position and keeping those in the dictionary set; remove words from the set once visited.",
        explanation="BFS explores ladders in order of length, so the first time `end` is reached is the shortest ladder. Generating candidate words is cheaper than comparing every pair of dictionary words.",
        time="O(N · L · 26)", space="O(N · L)",
        code="""
        from collections import deque
        from string import ascii_lowercase

        def ladder_length(begin: str, end: str, words: list[str]) -> int:
            remaining = set(words)
            if end not in remaining:
                return 0
            queue = deque([(begin, 1)])
            while queue:
                word, steps = queue.popleft()
                if word == end:
                    return steps
                for i in range(len(word)):
                    for ch in ascii_lowercase:
                        candidate = word[:i] + ch + word[i + 1:]
                        if candidate in remaining:
                            remaining.remove(candidate)
                            queue.append((candidate, steps + 1))
            return 0
        """,
    ),
    P(
        "maximum-path-sum", "Maximum Path Sum in a Binary Tree", "hard", ["dfs"],
        statement="A path is any sequence of connected nodes (each used at most once); it doesn't have to pass through the root or end at a leaf. Return the largest sum of values along any non-empty path.",
        inputs=f"- `root`: the root of a non-empty binary tree. {TREE_IO}",
        output="The maximum path sum.",
        constraints="- `1 <= number of nodes <= 3 × 10^4`\n- `-1000 <= val <= 1000`",
        examples=[
            ({"root": [1, 2, 3]}, 6, "2 → 1 → 3."),
            ({"root": [-10, 9, 20, None, None, 15, 7]}, 42, "15 → 20 → 7."),
        ],
        tests=[({"root": [-3]}, -3), ({"root": [2, -1]}, 2)],
        types={"root": "tree"},
        approach="Post-order DFS returning the best *downward* path starting at each node (`val + max(0, left, right)`). At each node also consider the path that bends there: `val + max(0, left) + max(0, right)`, and keep the global best.",
        explanation="Every path has one highest node where it bends; evaluating the bent path at every node covers all paths. Negative branches are dropped by taking max with 0.",
        time="O(n)", space="O(h)",
        code=T("""
        def max_path_sum(root: TreeNode) -> int:
            best = root.val

            def down(node: TreeNode | None) -> int:
                nonlocal best
                if node is None:
                    return 0
                left = max(0, down(node.left))
                right = max(0, down(node.right))
                best = max(best, node.val + left + right)
                return node.val + max(left, right)

            down(root)
            return best
        """),
    ),
]
