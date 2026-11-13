"""
Core computer science content: concept questions (the explanation is the
model answer) plus a few MCQs per subject. SQL questions carry a `sql`
solution.
"""

CATEGORY = {
    "slug": "core-cs",
    "name": "Core CS",
    "glyph": "◎",
    "description": "DBMS, operating systems, networks, OOP, SQL and software engineering — the theory round.",
    "topics": [
        # ================================================================ DBMS
        {
            "slug": "dbms",
            "name": "Database Management Systems",
            "description": "Transactions, normalization and how databases keep data correct.",
            "questions": [
                {
                    "slug": "dbms-acid",
                    "title": "Explain the ACID properties",
                    "type": "concept",
                    "difficulty": "easy",
                    "statement": "What are the ACID properties of a database transaction? Give a one-line example for each.",
                    "explanation": """
                        A **transaction** is a group of operations treated as one unit. ACID describes the
                        guarantees a DBMS gives for it:

                        - **Atomicity** — all or nothing. A bank transfer that debits A but crashes before
                          crediting B is rolled back completely.
                        - **Consistency** — a transaction moves the database from one valid state to another;
                          constraints (e.g. balance ≥ 0, foreign keys) still hold afterwards.
                        - **Isolation** — concurrent transactions don't see each other's half-finished work;
                          the result is as if they ran one after another (to the chosen isolation level).
                        - **Durability** — once committed, the change survives crashes (it's in the
                          write-ahead log / on disk).

                        *Interview tip:* mention how they're implemented — atomicity and durability via logging
                        (WAL / undo-redo), isolation via locking or MVCC.
                    """,
                },
                {
                    "slug": "dbms-normalization",
                    "title": "Normalization: 1NF, 2NF and 3NF",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "What is normalization and why do we do it? Explain 1NF, 2NF and 3NF with an example.",
                    "explanation": """
                        **Normalization** organises tables to remove redundancy, which prevents *update,
                        insert and delete anomalies* (e.g. changing a teacher's phone number in 40 rows).

                        Example table: `Enrollment(student_id, course_id, student_name, course_name, instructor, instructor_phone)`
                        with key `(student_id, course_id)`.

                        - **1NF** — every column holds atomic values; no repeating groups or lists in a cell.
                        - **2NF** — 1NF **and** no *partial dependency*: no non-key column depends on only part
                          of a composite key. `student_name` depends only on `student_id` → move it to
                          `Student(student_id, student_name)`; likewise `Course(course_id, course_name, instructor, instructor_phone)`.
                        - **3NF** — 2NF **and** no *transitive dependency*: non-key columns depend only on the
                          key. In `Course`, `instructor_phone` depends on `instructor`, not on `course_id` →
                          split out `Instructor(instructor, instructor_phone)`.

                        Trade-off: more joins at read time. Read-heavy systems sometimes *denormalize*
                        deliberately.
                    """,
                },
                {
                    "slug": "dbms-transitive-mcq",
                    "title": "Which normal form removes transitive dependency?",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "A table is in 2NF, but a non-key column depends on another non-key column. Which normal form addresses this?",
                    "options": ["1NF", "2NF", "3NF", "4NF"],
                    "answer": "C",
                    "explanation": """
                        A non-key attribute depending on another non-key attribute is a **transitive
                        dependency** (key → A → B). Removing it is exactly the requirement of **3NF**.
                        4NF deals with multi-valued dependencies.
                    """,
                },
            ],
        },
        # ================================================== OPERATING SYSTEMS
        {
            "slug": "operating-systems",
            "name": "Operating Systems",
            "description": "Processes, threads, scheduling, deadlocks and memory.",
            "questions": [
                {
                    "slug": "os-process-vs-thread",
                    "title": "Process vs thread",
                    "type": "concept",
                    "difficulty": "easy",
                    "statement": "What is the difference between a process and a thread?",
                    "explanation": """
                        - A **process** is a program in execution with its **own address space** (code, data,
                          heap, open files). Processes are isolated: one crashing doesn't corrupt another.
                        - A **thread** is a unit of execution *inside* a process. Threads of the same process
                          **share** code, data, heap and files, but each has its own **stack, registers and
                          program counter**.

                        Consequences: creating and context-switching threads is cheaper; communication
                        between threads is just shared memory (fast, but needs synchronisation — locks,
                        semaphores) while processes need IPC (pipes, sockets, shared memory segments).

                        Example: a browser may use separate *processes* per tab for isolation and multiple
                        *threads* inside a tab for rendering and networking.
                    """,
                },
                {
                    "slug": "os-deadlock",
                    "title": "Deadlock and its four conditions",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "What is a deadlock? State the four necessary conditions and one way to prevent it.",
                    "explanation": """
                        A **deadlock** is a set of processes each waiting for a resource held by another in the
                        set, so none can proceed. Example: T1 holds lock A and waits for B; T2 holds B and
                        waits for A.

                        All four (Coffman) conditions must hold simultaneously:

                        1. **Mutual exclusion** — a resource can be held by only one process at a time.
                        2. **Hold and wait** — a process holds resources while waiting for more.
                        3. **No preemption** — resources can't be forcibly taken away.
                        4. **Circular wait** — a cycle of processes, each waiting on the next.

                        **Prevention** breaks one condition. The most practical is breaking circular wait by
                        **acquiring locks in a fixed global order** (always A before B). Other strategies:
                        avoidance (Banker's algorithm), or detection and recovery (find cycles in the
                        wait-for graph, then abort/rollback a victim).
                    """,
                },
                {
                    "slug": "os-starvation-mcq",
                    "title": "Which scheduler can starve long jobs?",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "Which CPU scheduling algorithm can cause **starvation** of long processes if short processes keep arriving?",
                    "options": ["First-Come, First-Served", "Round Robin", "Shortest Job First", "None of these"],
                    "answer": "C",
                    "explanation": """
                        **Shortest Job First** always picks the shortest waiting job, so a long job can be
                        postponed indefinitely by a stream of short ones. FCFS and Round Robin guarantee every
                        process eventually runs. The usual fix is **aging** — gradually raising the priority of
                        processes that have waited long.
                    """,
                },
            ],
        },
        # ================================================== COMPUTER NETWORKS
        {
            "slug": "computer-networks",
            "name": "Computer Networks",
            "description": "OSI/TCP-IP layers, transport protocols and the web request path.",
            "questions": [
                {
                    "slug": "cn-tcp-vs-udp",
                    "title": "TCP vs UDP",
                    "type": "concept",
                    "difficulty": "easy",
                    "statement": "Compare TCP and UDP. When would you choose each?",
                    "explanation": """
                        | | **TCP** | **UDP** |
                        |---|---|---|
                        | Connection | Connection-oriented (3-way handshake) | Connectionless |
                        | Reliability | Retransmits lost segments, acknowledgements | Best effort, no retransmission |
                        | Ordering | In-order delivery | No ordering guarantee |
                        | Flow / congestion control | Yes | No |
                        | Header | 20+ bytes | 8 bytes |

                        Choose **TCP** when every byte must arrive correctly and in order: web pages (HTTP/1.1,
                        HTTP/2), email, file transfer, database connections.

                        Choose **UDP** when low latency matters more than perfect delivery, or the application
                        handles reliability itself: live video/voice, online games, DNS lookups. (HTTP/3 runs
                        on QUIC, which builds reliability on top of UDP.)
                    """,
                },
                {
                    "slug": "cn-type-a-url",
                    "title": "What happens when you type a URL?",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "Walk through what happens, step by step, after you type `https://example.com` into a browser and press Enter.",
                    "explanation": """
                        1. **Parse the URL** — scheme `https`, host `example.com`, default port 443.
                        2. **DNS resolution** — browser cache → OS cache → configured resolver, which walks
                           root → `.com` → the domain's authoritative server to get an IP address.
                        3. **TCP connection** — three-way handshake (SYN, SYN-ACK, ACK) with the server's IP on
                           port 443.
                        4. **TLS handshake** — agree on a cipher, server presents its certificate, browser
                           verifies it against trusted CAs, both derive session keys.
                        5. **HTTP request** — `GET /` with headers (Host, cookies, Accept, …), encrypted.
                        6. **Server side** — load balancer / reverse proxy → application server → maybe a
                           database; a response with status, headers and HTML is returned.
                        7. **Rendering** — the browser parses HTML into the DOM, CSS into the CSSOM, fetches
                           referenced resources (often over the same connection), runs JavaScript, then lays out
                           and paints the page.

                        Mention caching (DNS TTLs, HTTP cache headers, CDNs) for a stronger answer.
                    """,
                },
                {
                    "slug": "cn-router-layer-mcq",
                    "title": "Where do routers operate?",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "At which OSI layer do routers primarily operate?",
                    "options": ["Data Link (Layer 2)", "Network (Layer 3)", "Transport (Layer 4)", "Session (Layer 5)"],
                    "answer": "B",
                    "explanation": """
                        Routers forward packets between networks using **IP addresses**, which live at the
                        **Network layer (Layer 3)**. Switches typically work at Layer 2 using MAC addresses.
                    """,
                },
            ],
        },
        # ================================================================= OOP
        {
            "slug": "oop",
            "name": "Object-Oriented Programming",
            "description": "The four pillars, polymorphism and design principles.",
            "questions": [
                {
                    "slug": "oop-four-pillars",
                    "title": "The four pillars of OOP",
                    "type": "concept",
                    "difficulty": "easy",
                    "statement": "Explain the four pillars of object-oriented programming with a short example of each.",
                    "explanation": """
                        - **Encapsulation** — bundle data with the methods that operate on it and hide internal
                          state. A `BankAccount` keeps `balance` private and exposes `deposit()` / `withdraw()`
                          that enforce rules.
                        - **Abstraction** — expose *what* an object does, hide *how*. Calling `car.start()`
                          without knowing about the ignition system; abstract classes and interfaces express this.
                        - **Inheritance** — a class reuses and extends another. `SavingsAccount extends
                          BankAccount` and adds `add_interest()`.
                        - **Polymorphism** — one interface, many implementations. `shape.area()` works for
                          `Circle` and `Rectangle`, each computing it differently (runtime polymorphism via
                          overriding; compile-time via overloading).
                    """,
                },
                {
                    "slug": "oop-overloading-vs-overriding",
                    "title": "Overloading vs overriding",
                    "type": "concept",
                    "difficulty": "easy",
                    "statement": "What is the difference between method overloading and method overriding?",
                    "explanation": """
                        | | **Overloading** | **Overriding** |
                        |---|---|---|
                        | Where | Same class | Subclass redefines a parent method |
                        | Signature | Same name, **different parameters** | **Same** name and parameters |
                        | Resolved | At compile time (static polymorphism) | At runtime (dynamic dispatch) |
                        | Purpose | Convenience: `add(int, int)`, `add(double, double)` | Specialise behaviour: `Dog.speak()` vs `Animal.speak()` |

                        Note: Python doesn't support overloading by signature (the last definition wins);
                        default/variable arguments are used instead. Java and C++ support both.
                    """,
                },
                {
                    "slug": "oop-liskov-mcq",
                    "title": "Substituting a subclass",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "Which SOLID principle states that objects of a subclass should be usable anywhere the parent class is expected, without breaking correctness?",
                    "options": [
                        "Open/Closed Principle",
                        "Liskov Substitution Principle",
                        "Interface Segregation Principle",
                        "Dependency Inversion Principle",
                    ],
                    "answer": "B",
                    "explanation": """
                        The **Liskov Substitution Principle**. Classic violation: `Square extends Rectangle`
                        where setting the width also changes the height, breaking code that expects a
                        rectangle's sides to be independent.
                    """,
                },
            ],
        },
        # ================================================================= SQL
        {
            "slug": "sql",
            "name": "SQL",
            "description": "Queries that come up in technical rounds: joins, grouping and ranking.",
            "questions": [
                {
                    "slug": "sql-second-highest-salary",
                    "title": "Second highest salary",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": """
                        Table `employees(id, name, salary)`. Write a query that returns the **second highest
                        distinct salary**. Return `NULL` if there isn't one.
                    """,
                    "explanation": """
                        Take the maximum of all salaries strictly below the maximum. If every salary is the
                        same, the inner filter leaves no rows and `MAX` returns `NULL`, as required.

                        For the *N-th* highest, use a window function: `DENSE_RANK()` gives equal salaries the
                        same rank without gaps, so rank 2 is the second highest distinct salary.

                        ```sql
                        SELECT DISTINCT salary
                        FROM (
                          SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
                          FROM employees
                        ) ranked
                        WHERE rnk = 2;
                        ```
                    """,
                    "solutions": {
                        "sql": """
                            SELECT MAX(salary) AS second_highest_salary
                            FROM employees
                            WHERE salary < (SELECT MAX(salary) FROM employees);
                        """,
                    },
                },
                {
                    "slug": "sql-earning-more-than-manager",
                    "title": "Employees earning more than their manager",
                    "type": "concept",
                    "difficulty": "easy",
                    "statement": """
                        Table `employees(id, name, salary, manager_id)` where `manager_id` references another
                        row's `id` (NULL for the top boss). List the names of employees who earn more than
                        their manager.
                    """,
                    "explanation": """
                        This is a **self-join**: join the table to itself, once as the employee (`e`) and once
                        as the manager (`m`), matching `e.manager_id = m.id`. An inner join naturally drops
                        employees without a manager.
                    """,
                    "solutions": {
                        "sql": """
                            SELECT e.name
                            FROM employees AS e
                            JOIN employees AS m ON e.manager_id = m.id
                            WHERE e.salary > m.salary;
                        """,
                    },
                },
                {
                    "slug": "sql-duplicate-emails",
                    "title": "Find duplicate emails",
                    "type": "concept",
                    "difficulty": "easy",
                    "statement": "Table `users(id, email)`. Return every email address that appears more than once.",
                    "explanation": """
                        Group rows by email and keep only groups with more than one row. Filtering on an
                        aggregate (`COUNT(*)`) must use **HAVING** — `WHERE` runs before grouping, so it can't
                        see counts.
                    """,
                    "solutions": {
                        "sql": """
                            SELECT email
                            FROM users
                            GROUP BY email
                            HAVING COUNT(*) > 1;
                        """,
                    },
                },
                {
                    "slug": "sql-having-mcq",
                    "title": "Filtering after aggregation",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Which clause filters **groups** after `GROUP BY` has been applied?",
                    "options": ["HAVING", "WHERE", "ORDER BY", "LIMIT"],
                    "answer": "A",
                    "explanation": """
                        Logical order: `FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT`.
                        `WHERE` filters individual rows before grouping; **HAVING** filters the groups, so it
                        can use aggregates like `COUNT(*) > 1`.
                    """,
                },
            ],
        },
        # ================================================= SOFTWARE ENGINEERING
        {
            "slug": "software-engineering",
            "name": "Software Engineering",
            "description": "Development life cycles, testing and agile practice.",
            "questions": [
                {
                    "slug": "se-waterfall-vs-agile",
                    "title": "SDLC: Waterfall vs Agile",
                    "type": "concept",
                    "difficulty": "easy",
                    "statement": "Name the phases of the software development life cycle and compare the Waterfall and Agile models.",
                    "explanation": """
                        Typical **SDLC phases**: requirements → design → implementation → testing →
                        deployment → maintenance.

                        - **Waterfall** runs the phases once, in sequence; each phase finishes before the next
                          starts. Predictable and well documented, but changes are expensive and working
                          software appears only at the end. Suits fixed, well-understood requirements.
                        - **Agile** runs all phases in short iterations (sprints of 1–4 weeks), delivering a
                          working increment each time and adapting to feedback. Embraces change, needs close
                          customer involvement. Scrum and Kanban are common Agile frameworks.
                    """,
                },
                {
                    "slug": "se-testing-levels",
                    "title": "Unit, integration and system testing",
                    "type": "concept",
                    "difficulty": "easy",
                    "statement": "Differentiate unit, integration and system testing.",
                    "explanation": """
                        - **Unit testing** — tests the smallest pieces (a function or class) in isolation,
                          usually by developers, with dependencies mocked. Fast and numerous.
                        - **Integration testing** — tests that modules work *together*: e.g. the API layer with
                          a real database, or two services talking over HTTP. Catches interface mismatches.
                        - **System testing** — tests the complete, deployed application end-to-end against the
                          requirements, including non-functional aspects (performance, security).

                        Often followed by **acceptance testing** by the customer. The *testing pyramid*:
                        many unit tests, fewer integration tests, few end-to-end tests.
                    """,
                },
                {
                    "slug": "se-product-owner-mcq",
                    "title": "Who owns the backlog?",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "In Scrum, who is accountable for maximising the product's value and ordering the product backlog?",
                    "options": ["Scrum Master", "Development Team", "Project Manager", "Product Owner"],
                    "answer": "D",
                    "explanation": """
                        The **Product Owner** owns and orders the product backlog. The Scrum Master coaches the
                        team and removes impediments; Scrum has no "project manager" role.
                    """,
                },
            ],
        },
    ],
}
