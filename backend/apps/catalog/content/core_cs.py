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
                {
                    "slug": "dbms-keys",
                    "title": "Super, candidate, primary and foreign keys",
                    "type": "concept",
                    "difficulty": "easy",
                    "statement": "Explain super key, candidate key, primary key, alternate key and foreign key with one example table.",
                    "explanation": """
                        Table `Student(roll_no, email, name, dept_id)`:

                        - **Super key** — any set of columns that uniquely identifies a row: `{roll_no}`,
                          `{email}`, `{roll_no, name}`, …
                        - **Candidate key** — a *minimal* super key (remove any column and it stops being unique):
                          `{roll_no}` and `{email}`.
                        - **Primary key** — the candidate key chosen to identify rows; it can't be NULL:
                          `roll_no`.
                        - **Alternate key** — the candidate keys not chosen: `email` (usually given a UNIQUE
                          constraint).
                        - **Foreign key** — a column that references another table's key, enforcing referential
                          integrity: `dept_id → Department(id)`. You can't insert a student with a department that
                          doesn't exist.
                    """,
                },
                {
                    "slug": "dbms-indexing",
                    "title": "What is an index? What does it cost?",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "What is a database index, how does a B+ tree index speed up queries, and what are the trade-offs?",
                    "explanation": """
                        An **index** is a separate, sorted data structure that maps column values to row
                        locations — like a book's index — so the database can find rows without scanning the whole
                        table.

                        Most relational databases use a **B+ tree**: a balanced, wide tree whose leaves hold the
                        keys in sorted order and are linked to each other. A lookup walks root → leaf in
                        O(log n) page reads (usually 3–4 even for millions of rows), and range queries
                        (`WHERE age BETWEEN 20 AND 30`, `ORDER BY`) just follow the linked leaves.

                        **Trade-offs**
                        - Every `INSERT`/`UPDATE`/`DELETE` must also update each index → slower writes.
                        - Indexes take disk space and memory.
                        - Low-selectivity columns (e.g. a boolean) rarely benefit.
                        - Composite indexes only help queries that use their *leftmost* columns.

                        Rule of thumb: index columns used in frequent `WHERE`, `JOIN` and `ORDER BY` clauses, and
                        check with `EXPLAIN`.
                    """,
                },
                {
                    "slug": "dbms-isolation-levels",
                    "title": "Isolation levels and read anomalies",
                    "type": "concept",
                    "difficulty": "hard",
                    "statement": "Explain dirty reads, non-repeatable reads and phantom reads, and which SQL isolation levels prevent each.",
                    "explanation": """
                        - **Dirty read** — reading another transaction's *uncommitted* change (which may be
                          rolled back).
                        - **Non-repeatable read** — reading the same row twice in one transaction and getting
                          different values because another transaction committed an update in between.
                        - **Phantom read** — re-running a range query and getting *new rows* because another
                          transaction inserted rows that match.

                        | Isolation level | Dirty | Non-repeatable | Phantom |
                        |---|---|---|---|
                        | Read Uncommitted | possible | possible | possible |
                        | Read Committed | prevented | possible | possible |
                        | Repeatable Read | prevented | prevented | possible* |
                        | Serializable | prevented | prevented | prevented |

                        \\* PostgreSQL's Repeatable Read (snapshot isolation) also prevents phantoms. Higher levels
                        give stronger guarantees at the cost of more blocking or more transaction retries.
                        PostgreSQL and Oracle default to **Read Committed**; MySQL InnoDB defaults to
                        **Repeatable Read**.
                    """,
                },
                {
                    "slug": "dbms-delete-truncate-drop",
                    "title": "DELETE vs TRUNCATE vs DROP",
                    "type": "concept",
                    "difficulty": "easy",
                    "statement": "What is the difference between DELETE, TRUNCATE and DROP?",
                    "explanation": """
                        | | **DELETE** | **TRUNCATE** | **DROP** |
                        |---|---|---|---|
                        | Removes | Selected rows (`WHERE`) | All rows | The whole table (data + structure) |
                        | Type | DML | DDL | DDL |
                        | Row-by-row / triggers | Yes, fires row triggers | No | No |
                        | Speed on big tables | Slowest | Fast | Fast |
                        | Table still exists | Yes | Yes | No |

                        `DELETE` can be rolled back in a transaction. Whether `TRUNCATE` can depends on the
                        database (PostgreSQL: yes, inside a transaction; MySQL/Oracle: it commits implicitly).
                    """,
                },
                {
                    "slug": "dbms-durability-mcq",
                    "title": "Surviving a crash",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Which ACID property guarantees that once a transaction has committed, its changes survive a system crash?",
                    "options": ["Atomicity", "Consistency", "Isolation", "Durability"],
                    "answer": "D",
                    "explanation": """
                        **Durability.** It is typically implemented with a write-ahead log that is flushed to disk
                        before the commit is acknowledged, so committed work can be replayed after a crash.
                    """,
                },
                {
                    "slug": "dbms-2nf-mcq",
                    "title": "What does 2NF remove?",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Moving a table from 1NF to 2NF removes which kind of dependency?",
                    "options": ["Transitive dependency", "Partial dependency", "Multivalued dependency", "Join dependency"],
                    "answer": "B",
                    "explanation": """
                        2NF removes **partial dependencies** — non-key columns that depend on only *part* of a
                        composite primary key. 3NF then removes transitive dependencies; 4NF multivalued ones.
                    """,
                },
                {
                    "slug": "dbms-index-structure-mcq",
                    "title": "The default index structure",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Which data structure do most relational databases use for their default index type?",
                    "options": ["B+ tree", "Hash table", "Linked list", "Binary heap"],
                    "answer": "A",
                    "explanation": """
                        The **B+ tree**: balanced, shallow, keeps keys sorted and links its leaves, so it supports
                        both equality lookups and range scans. Hash indexes only help equality lookups.
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
                {
                    "slug": "os-paging-segmentation",
                    "title": "Paging, segmentation and page faults",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "Explain paging and segmentation. What is a page fault and how does the OS handle it?",
                    "explanation": """
                        **Paging** splits a process's logical memory into fixed-size *pages* and physical memory
                        into same-size *frames*. A **page table** maps pages to frames, so a process doesn't need
                        contiguous physical memory. Fixed sizes remove external fragmentation but can waste part of
                        the last page (internal fragmentation).

                        **Segmentation** splits memory into variable-size logical *segments* (code, stack, heap)
                        that match how programmers think. Sizes vary, so it suffers external fragmentation.

                        A **page fault** happens when a process touches a page that isn't in RAM:
                        1. The MMU traps to the OS.
                        2. The OS finds the page on disk (swap / the file).
                        3. It picks a free frame — evicting a victim page if needed (FIFO, LRU, …).
                        4. It loads the page, updates the page table and restarts the instruction.

                        The **TLB** caches recent page-table entries so most translations need no memory access.
                    """,
                },
                {
                    "slug": "os-virtual-memory-thrashing",
                    "title": "Virtual memory and thrashing",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "What is virtual memory? What is thrashing and how can it be reduced?",
                    "explanation": """
                        **Virtual memory** gives each process the illusion of a large, private, contiguous address
                        space. Only the pages actually in use need to be in RAM; the rest live on disk and are
                        loaded on demand (demand paging). Benefits: isolation between processes, running programs
                        larger than RAM, and sharing pages (e.g. shared libraries).

                        **Thrashing** is when the system spends more time swapping pages in and out than running
                        programs. It happens when the combined *working sets* (pages each process actively needs)
                        don't fit in RAM, so every process keeps faulting.

                        Reduce it by: running fewer processes at once, giving processes enough frames for their
                        working set (working-set model, page-fault-frequency control), better locality in programs,
                        or adding RAM.
                    """,
                },
                {
                    "slug": "os-mutex-vs-semaphore",
                    "title": "Mutex vs semaphore",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "What is the difference between a mutex and a semaphore? Give a use case for each.",
                    "explanation": """
                        - A **mutex** is a lock with **ownership**: only one thread holds it, and only that thread
                          may release it. Use it to protect a critical section, e.g. updating a shared counter or
                          a linked list.
                        - A **semaphore** is a **counter** with two atomic operations: `wait` (P) decrements and
                          blocks at 0; `signal` (V) increments. Any thread may signal. A *counting* semaphore
                          initialised to N lets up to N threads in at once — e.g. limiting a pool of 5 database
                          connections. A *binary* semaphore (0/1) is often used for signalling between threads
                          (producer tells consumer "an item is ready").

                        Key difference: a mutex is about **mutual exclusion with ownership**; a semaphore is about
                        **counting available resources or signalling events**.
                    """,
                },
                {
                    "slug": "os-scheduling-compare",
                    "title": "Comparing CPU scheduling algorithms",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "Compare FCFS, SJF, Round Robin and Priority scheduling.",
                    "explanation": """
                        | Algorithm | How it picks | Strength | Weakness |
                        |---|---|---|---|
                        | **FCFS** | Order of arrival | Simple, no starvation | Convoy effect: short jobs wait behind long ones |
                        | **SJF / SRTF** | Shortest (remaining) burst | Minimum average waiting time | Needs burst estimates; long jobs can starve |
                        | **Round Robin** | Each process gets a time quantum in turn | Fair, good response time | Quantum too small → overhead; too large → becomes FCFS |
                        | **Priority** | Highest priority first | Expresses importance | Starvation of low priority (fixed by *aging*) |

                        Real systems combine ideas, e.g. **multilevel feedback queues** that start every process
                        at high priority and demote CPU-heavy ones.
                    """,
                },
                {
                    "slug": "os-belady-mcq",
                    "title": "Belady's anomaly",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "Which page replacement algorithm can suffer from **Belady's anomaly** (more frames causing more page faults)?",
                    "options": ["LRU", "Optimal", "FIFO", "None of these"],
                    "answer": "C",
                    "explanation": """
                        **FIFO.** LRU and Optimal are *stack algorithms*: the pages kept with N frames are always a
                        subset of those kept with N + 1, so adding frames can never increase faults. FIFO lacks this
                        property — the classic reference string 1 2 3 4 1 2 5 1 2 3 4 5 gives 9 faults with 3
                        frames but 10 with 4.
                    """,
                },
                {
                    "slug": "os-round-robin-mcq",
                    "title": "A very large time quantum",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "In Round Robin scheduling, what happens if the time quantum is made very large?",
                    "options": [
                        "It behaves like Shortest Job First",
                        "It causes starvation of long processes",
                        "It behaves like Priority scheduling",
                        "It behaves like First-Come, First-Served",
                    ],
                    "answer": "D",
                    "explanation": """
                        If the quantum is longer than every CPU burst, each process runs to completion in arrival
                        order — exactly **FCFS**. A very small quantum has the opposite problem: too much
                        context-switch overhead.
                    """,
                },
                {
                    "slug": "os-bankers-mcq",
                    "title": "What is the Banker's algorithm for?",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "The Banker's algorithm is used for deadlock …",
                    "options": ["prevention", "avoidance", "detection", "recovery"],
                    "answer": "B",
                    "explanation": """
                        **Avoidance.** Before granting a request it checks whether the system would remain in a
                        *safe state* (some order exists in which every process can finish). Prevention instead
                        breaks one of the four Coffman conditions by design.
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
                {
                    "slug": "cn-osi-layers",
                    "title": "The OSI model's seven layers",
                    "type": "concept",
                    "difficulty": "easy",
                    "statement": "List the seven layers of the OSI model with the job of each and an example protocol or device.",
                    "explanation": """
                        | # | Layer | Job | Examples |
                        |---|---|---|---|
                        | 7 | Application | Network services for apps | HTTP, DNS, SMTP |
                        | 6 | Presentation | Encoding, encryption, compression | TLS, JPEG, UTF-8 |
                        | 5 | Session | Opening/maintaining sessions | RPC sessions |
                        | 4 | Transport | End-to-end delivery, ports | TCP, UDP |
                        | 3 | Network | Logical addressing and routing | IP, ICMP — routers |
                        | 2 | Data Link | Framing, MAC addresses, local delivery | Ethernet, Wi-Fi — switches |
                        | 1 | Physical | Bits on the wire / radio | Cables, hubs |

                        Mnemonic (top-down): **A**ll **P**eople **S**eem **T**o **N**eed **D**ata **P**rocessing.
                        The practical TCP/IP model merges layers 5–7 into Application and 1–2 into Link.
                    """,
                },
                {
                    "slug": "cn-tcp-handshake",
                    "title": "TCP's three-way handshake",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "Explain how TCP opens a connection (three-way handshake) and how it closes one.",
                    "explanation": """
                        **Opening**
                        1. Client → `SYN` with its initial sequence number *x*.
                        2. Server → `SYN-ACK`: its own sequence number *y*, acknowledging *x + 1*.
                        3. Client → `ACK` acknowledging *y + 1*. Both sides now agree on sequence numbers and the
                           connection is established.

                        Three messages are the minimum for **both** sides to learn and confirm each other's
                        starting sequence numbers (it also protects against stale duplicate SYNs).

                        **Closing** (four-way): each direction is closed separately — `FIN` → `ACK` from one side,
                        then `FIN` → `ACK` from the other. The side that closes first waits in **TIME_WAIT**
                        (2 × maximum segment lifetime) so delayed packets from the old connection can't be mistaken
                        for a new one.
                    """,
                },
                {
                    "slug": "cn-dns-resolution",
                    "title": "How DNS resolution works",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "How does DNS turn a domain name into an IP address? What is the difference between recursive and iterative queries?",
                    "explanation": """
                        1. The browser and OS check their **caches**.
                        2. The OS asks a configured **recursive resolver** (ISP, 8.8.8.8, …).
                        3. If the resolver doesn't have it cached, it asks a **root server** → gets referred to the
                           **TLD server** for `.com` → which refers it to the domain's **authoritative server** →
                           which returns the A/AAAA record.
                        4. The resolver caches the answer for its **TTL** and returns it.

                        - **Recursive query**: "give me the final answer" — the client → resolver request.
                        - **Iterative query**: "tell me who to ask next" — the resolver ↔ root/TLD/authoritative
                          servers.

                        DNS usually runs over UDP port 53 (TCP for large responses and zone transfers).
                    """,
                },
                {
                    "slug": "cn-http-vs-https",
                    "title": "HTTP vs HTTPS",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "What does HTTPS add to HTTP, and how does TLS protect the connection?",
                    "explanation": """
                        HTTPS is **HTTP over TLS** (default port 443 instead of 80). TLS provides:

                        - **Confidentiality** — traffic is encrypted, so eavesdroppers on the Wi-Fi or ISP can't
                          read it.
                        - **Integrity** — messages carry authentication codes, so tampering is detected.
                        - **Authentication** — the server presents a **certificate** signed by a trusted
                          Certificate Authority, proving it really is `example.com`.

                        During the handshake the client verifies the certificate, both sides agree on a cipher
                        and use **asymmetric** cryptography (e.g. ECDHE key exchange) to derive a shared secret;
                        the bulk data is then encrypted with fast **symmetric** keys (e.g. AES-GCM).
                    """,
                },
                {
                    "slug": "cn-subnet-hosts-mcq",
                    "title": "Hosts in a /26",
                    "type": "mcq",
                    "difficulty": "medium",
                    "statement": "How many **usable** host addresses does an IPv4 /26 subnet provide?",
                    "options": ["64", "30", "62", "126"],
                    "answer": "C",
                    "explanation": """
                        /26 leaves 32 − 26 = 6 host bits → 2⁶ = 64 addresses. Two are reserved (network and
                        broadcast), so **62** are usable.
                    """,
                },
                {
                    "slug": "cn-https-port-mcq",
                    "title": "The HTTPS port",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "What is the default port for HTTPS?",
                    "options": ["443", "80", "22", "8080"],
                    "answer": "A",
                    "explanation": """
                        **443.** HTTP uses 80, SSH 22; 8080 is a common alternative HTTP port, not a standard.
                    """,
                },
                {
                    "slug": "cn-arp-mcq",
                    "title": "IP address to MAC address",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Which protocol finds the MAC address that belongs to an IP address on the local network?",
                    "options": ["DNS", "DHCP", "ICMP", "ARP"],
                    "answer": "D",
                    "explanation": """
                        **ARP** (Address Resolution Protocol) broadcasts "who has 192.168.1.5?" and the owner
                        replies with its MAC address. DNS maps names to IPs; DHCP hands out IP addresses.
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
                {
                    "slug": "oop-abstract-vs-interface",
                    "title": "Abstract class vs interface",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "When would you use an abstract class instead of an interface?",
                    "explanation": """
                        - An **abstract class** is a partial implementation: it can hold state (fields),
                          constructors and concrete methods alongside abstract ones. A class can extend only
                          **one** (in Java/C#). Use it when related classes share code and an "is-a" relationship —
                          e.g. `abstract class Shape` with a shared `name` field and `describe()` method.
                        - An **interface** is a contract of capabilities with no instance state. A class can
                          implement **many**. Use it to express "can-do" roles across unrelated classes —
                          `Comparable`, `Serializable`, `Runnable`.

                        Modern Java interfaces allow `default` methods, which blurs the line, but they still can't
                        hold instance fields. Rule of thumb: share *code* → abstract class; share a *contract* →
                        interface.
                    """,
                },
                {
                    "slug": "oop-composition-vs-inheritance",
                    "title": "Composition over inheritance",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "What does \"favour composition over inheritance\" mean? Give an example.",
                    "explanation": """
                        **Inheritance** ("is-a") reuses code by extending a class; **composition** ("has-a")
                        reuses code by holding other objects and delegating to them.

                        Inheritance couples a subclass tightly to its parent's internals, and deep hierarchies
                        break when the parent changes (the *fragile base class* problem). Composition lets you
                        swap behaviour at runtime.

                        Example: instead of `FlyingDuck`, `RubberDuck`, `RobotDuck` subclasses for every
                        combination, give `Duck` a `fly_behaviour` object (`CanFly`, `CannotFly`) and call
                        `self.fly_behaviour.fly()`. New behaviours need new small classes, not a new branch of
                        the hierarchy. (This is the Strategy pattern.)

                        Inheritance is still right for genuine "is-a" relationships with stable base classes.
                    """,
                },
                {
                    "slug": "oop-solid",
                    "title": "SOLID in one line each",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "Explain each of the five SOLID principles in one or two sentences.",
                    "explanation": """
                        - **S — Single Responsibility**: a class should have one reason to change (don't mix
                          invoice calculation with PDF printing).
                        - **O — Open/Closed**: open for extension, closed for modification — add new behaviour by
                          adding code (a new `PaymentMethod` class), not by editing a growing `if/else`.
                        - **L — Liskov Substitution**: subclasses must work anywhere their parent is expected
                          without surprising callers.
                        - **I — Interface Segregation**: prefer several small, focused interfaces over one fat
                          interface clients are forced to implement.
                        - **D — Dependency Inversion**: depend on abstractions, not concrete classes — pass a
                          `Notifier` interface in, rather than constructing `EmailService` inside.
                    """,
                },
                {
                    "slug": "oop-shallow-deep-copy",
                    "title": "Shallow copy vs deep copy",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "What is the difference between a shallow copy and a deep copy of an object?",
                    "explanation": """
                        - A **shallow copy** creates a new outer object but **shares** the nested objects with the
                          original. Changing a nested list in the copy also changes it in the original.
                        - A **deep copy** recursively copies everything, so the two objects are fully independent.

                        ```python
                        import copy
                        a = {"tags": ["dp"]}
                        b = copy.copy(a)        # shallow
                        c = copy.deepcopy(a)    # deep
                        b["tags"].append("graphs")
                        # a["tags"] == ["dp", "graphs"]  — shared with b
                        # c["tags"] == ["dp"]            — independent
                        ```

                        Deep copies cost more time and memory and must handle cycles; shallow copies are enough
                        for objects that contain only immutable values.
                    """,
                },
                {
                    "slug": "oop-private-mcq",
                    "title": "Visible only inside the class",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "In Java, which access modifier makes a member accessible **only within its own class**?",
                    "options": ["protected", "private", "public", "default (no modifier)"],
                    "answer": "B",
                    "explanation": """
                        **private.** Default (package-private) allows the whole package; `protected` adds
                        subclasses; `public` allows everyone.
                    """,
                },
                {
                    "slug": "oop-runtime-polymorphism-mcq",
                    "title": "What kind of polymorphism is overriding?",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Method overriding is an example of …",
                    "options": ["compile-time polymorphism", "encapsulation", "runtime polymorphism", "abstraction"],
                    "answer": "C",
                    "explanation": """
                        **Runtime polymorphism** (dynamic dispatch): which override runs is decided by the
                        object's actual class at runtime. Overloading is the compile-time kind.
                    """,
                },
                {
                    "slug": "oop-diamond-mcq",
                    "title": "The diamond problem",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "The \"diamond problem\" arises from which feature?",
                    "options": ["Multiple inheritance", "Method overloading", "Encapsulation", "Composition"],
                    "answer": "A",
                    "explanation": """
                        **Multiple inheritance**: if B and C both inherit from A and override a method, and D
                        inherits from both B and C, which version does D get? Java avoids it by allowing a single
                        superclass; C++ uses virtual inheritance; Python uses the C3 method resolution order.
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
                {
                    "slug": "sql-join-types",
                    "title": "INNER, LEFT, RIGHT and FULL joins",
                    "type": "concept",
                    "difficulty": "easy",
                    "statement": "Explain INNER JOIN, LEFT JOIN, RIGHT JOIN and FULL OUTER JOIN using `employees` and `departments` as the example.",
                    "explanation": """
                        `employees(id, name, dept_id)` joined to `departments(id, name)` on
                        `employees.dept_id = departments.id`:

                        - **INNER JOIN** — only employees that have a matching department.
                        - **LEFT JOIN** — *all* employees; department columns are NULL for employees without one.
                        - **RIGHT JOIN** — *all* departments; employee columns are NULL for empty departments.
                        - **FULL OUTER JOIN** — everything from both sides, NULLs where there's no match.

                        A `CROSS JOIN` pairs every row with every row (no condition). Interview favourite: a
                        `LEFT JOIN` plus `WHERE right_table.id IS NULL` finds rows with **no** match.
                    """,
                    "solutions": {
                        "sql": """
                            SELECT e.name AS employee, d.name AS department
                            FROM employees AS e
                            LEFT JOIN departments AS d ON e.dept_id = d.id;
                        """,
                    },
                },
                {
                    "slug": "sql-top-salary-per-department",
                    "title": "Highest-paid employee in each department",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": """
                        Tables `employees(id, name, salary, dept_id)` and `departments(id, name)`. List each
                        department with the employee(s) earning the highest salary in it. Include ties.
                    """,
                    "explanation": """
                        Rank employees **within each department** with a window function and keep rank 1.
                        `PARTITION BY` restarts the ranking per department; `RANK()` gives tied employees the
                        same rank, so both are returned.

                        Without window functions: join each employee to a subquery of
                        `MAX(salary)` grouped by `dept_id` and keep rows where the salaries match.
                    """,
                    "solutions": {
                        "sql": """
                            SELECT department, employee, salary
                            FROM (
                              SELECT d.name AS department,
                                     e.name AS employee,
                                     e.salary,
                                     RANK() OVER (PARTITION BY e.dept_id ORDER BY e.salary DESC) AS rnk
                              FROM employees AS e
                              JOIN departments AS d ON d.id = e.dept_id
                            ) ranked
                            WHERE rnk = 1;
                        """,
                    },
                },
                {
                    "slug": "sql-customers-without-orders",
                    "title": "Customers who never ordered",
                    "type": "concept",
                    "difficulty": "easy",
                    "statement": "Tables `customers(id, name)` and `orders(id, customer_id, total)`. Return the names of customers who have never placed an order.",
                    "explanation": """
                        Use an **anti-join**: `NOT EXISTS` keeps customers for whom no matching order row exists.
                        An equivalent form is `LEFT JOIN orders … WHERE orders.id IS NULL`.

                        Avoid `NOT IN (SELECT customer_id FROM orders)` if `customer_id` can be NULL — a single
                        NULL makes `NOT IN` return no rows at all.
                    """,
                    "solutions": {
                        "sql": """
                            SELECT c.name
                            FROM customers AS c
                            WHERE NOT EXISTS (
                              SELECT 1 FROM orders AS o WHERE o.customer_id = c.id
                            );
                        """,
                    },
                },
                {
                    "slug": "sql-running-total",
                    "title": "Running total of daily sales",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "Table `sales(sale_date, amount)` has one row per day. Return each day with its amount and the running total up to that day.",
                    "explanation": """
                        A window `SUM` ordered by date adds up every row from the first day to the current one.
                        Unlike `GROUP BY`, window functions keep every row while computing an aggregate across
                        related rows. Add `PARTITION BY store_id` to restart the total per store.
                    """,
                    "solutions": {
                        "sql": """
                            SELECT sale_date,
                                   amount,
                                   SUM(amount) OVER (ORDER BY sale_date) AS running_total
                            FROM sales
                            ORDER BY sale_date;
                        """,
                    },
                },
                {
                    "slug": "sql-count-null-mcq",
                    "title": "COUNT(column) vs COUNT(*)",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "`COUNT(email)` can return a smaller number than `COUNT(*)` on the same table. What does `COUNT(email)` skip?",
                    "options": ["Duplicate emails", "Empty strings", "Rows where email is NULL", "Nothing — they are always equal"],
                    "answer": "C",
                    "explanation": """
                        `COUNT(column)` counts only **non-NULL** values; `COUNT(*)` counts rows. Empty strings are
                        not NULL and are counted. To skip duplicates use `COUNT(DISTINCT email)`.
                    """,
                },
                {
                    "slug": "sql-union-all-mcq",
                    "title": "UNION vs UNION ALL",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Which operator combines two result sets and **keeps duplicate rows**?",
                    "options": ["UNION", "INTERSECT", "UNION ALL", "EXCEPT"],
                    "answer": "C",
                    "explanation": """
                        **UNION ALL** keeps every row. `UNION` removes duplicates, which requires an extra
                        sort/hash step — so `UNION ALL` is faster when you know there are no duplicates or
                        don't care.
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
                {
                    "slug": "se-merge-vs-rebase",
                    "title": "git merge vs git rebase",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "What is the difference between `git merge` and `git rebase`? When should you avoid rebasing?",
                    "explanation": """
                        Both bring changes from one branch into another:

                        - **Merge** creates a new *merge commit* joining the two histories. History is preserved
                          exactly as it happened (non-linear).
                        - **Rebase** replays your commits on top of the other branch, creating *new* commits with
                          new hashes. History becomes linear and easier to read.

                        Golden rule: **don't rebase commits that others have already pulled** (shared/public
                        branches). Rewriting them forces everyone else to reconcile duplicate commits. Rebasing
                        your own local feature branch before opening a pull request is fine and common.
                    """,
                },
                {
                    "slug": "se-ci-cd",
                    "title": "Continuous integration and delivery",
                    "type": "concept",
                    "difficulty": "easy",
                    "statement": "What do Continuous Integration (CI) and Continuous Delivery/Deployment (CD) mean?",
                    "explanation": """
                        - **Continuous Integration** — developers merge small changes into the main branch often;
                          every push automatically builds the code and runs the tests, so integration problems are
                          found within minutes, not at the end of a release.
                        - **Continuous Delivery** — every change that passes the pipeline is automatically
                          prepared for release (packaged, deployed to staging); releasing to production is one
                          manual click.
                        - **Continuous Deployment** — the same, but production releases happen automatically
                          too, with no manual step.

                        Typical tools: GitHub Actions, GitLab CI, Jenkins.
                    """,
                },
                {
                    "slug": "se-coupling-cohesion",
                    "title": "Coupling and cohesion",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "Explain coupling and cohesion. Which combination do we aim for?",
                    "explanation": """
                        - **Cohesion** — how closely the responsibilities *inside* one module belong together. A
                          `PaymentService` that only handles payments is highly cohesive; a `Utils` class doing
                          dates, emails and maths is not.
                        - **Coupling** — how much one module depends on the *internals* of another. Calling a
                          small, stable interface is loose coupling; reaching into another class's fields is tight
                          coupling.

                        Aim for **high cohesion and low coupling**: modules that are easy to understand on their
                        own and can change without breaking others. Interfaces, dependency injection and clear
                        module boundaries all push in this direction.
                    """,
                },
                {
                    "slug": "se-design-patterns",
                    "title": "Singleton, Factory and Observer",
                    "type": "concept",
                    "difficulty": "medium",
                    "statement": "Explain the Singleton, Factory and Observer design patterns with a real use case for each.",
                    "explanation": """
                        - **Singleton** — guarantees exactly one instance with a global access point. Use case: a
                          configuration object or a logger. Caveats: hidden global state and harder testing.
                        - **Factory** — a method/class decides *which* concrete class to create, so callers depend
                          only on an interface. Use case: `NotificationFactory.create("sms" | "email")` returning
                          the right sender.
                        - **Observer** — subjects keep a list of subscribers and notify them when something
                          changes. Use case: UI event listeners, or a "new order" event that triggers email, stock
                          update and analytics independently.

                        Patterns are names for proven solutions — mention the *problem* each solves, not just the
                        structure.
                    """,
                },
                {
                    "slug": "se-white-box-mcq",
                    "title": "Testing with knowledge of the code",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Testing that is designed using knowledge of the program's internal code and logic is called …",
                    "options": ["black-box testing", "white-box testing", "acceptance testing", "smoke testing"],
                    "answer": "B",
                    "explanation": """
                        **White-box** (glass-box) testing uses the code structure — e.g. covering every branch.
                        Black-box testing checks inputs and outputs against the specification only.
                    """,
                },
                {
                    "slug": "se-regression-mcq",
                    "title": "Did my change break anything?",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Re-running existing tests after a code change to make sure previously working features still work is called …",
                    "options": ["unit testing", "load testing", "alpha testing", "regression testing"],
                    "answer": "D",
                    "explanation": """
                        **Regression testing.** Automated test suites in a CI pipeline are the usual way to run it
                        on every change.
                    """,
                },
                {
                    "slug": "se-agile-manifesto-mcq",
                    "title": "Working software over …",
                    "type": "mcq",
                    "difficulty": "easy",
                    "statement": "Complete this value from the Agile Manifesto: \"Working software over ___.\"",
                    "options": ["comprehensive documentation", "customer collaboration", "following a plan", "processes and tools"],
                    "answer": "A",
                    "explanation": """
                        "Working software over **comprehensive documentation**." The other values are
                        individuals and interactions over processes and tools; customer collaboration over
                        contract negotiation; responding to change over following a plan.
                    """,
                },
            ],
        },
    ],
}
