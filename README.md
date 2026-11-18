# CodeSignal Industry Coding Framework Practice Kit

An unofficial Python practice kit with 10 focused drills and six four-level mocks.
You'll need **Python 3**. The tests use the standard library, so there's nothing to install.
Clone or download the repository and run these commands from its root.

```bash
./run                 # list the drills and mocks
./run d01             # run a drill against your solution.py
./run m2 3            # run mock 2, level 3
./run m2              # run all four levels of mock 2
./run --ref m2 3      # run the reference solution, to see the tests are satisfiable
./run reset m2        # wipe solution.py back to the blank starter
./run timer 90        # 90-minute exam clock with level checkpoints
./run verify          # self-check: all 16 reference solutions vs all 314 tests
```

Start with [the ranking drill](drills/d01_top_n_ranking/README.md), edit its
`solution.py`, and run `./run d01` for feedback. On Windows, you can replace
`./run` with `py -3 tools/run.py`. Starter tests can fail until you implement
the exercise. The worked answers in `reference.py` are for review after your attempt.

---

## What you're preparing for

One problem. Four levels that build on each other. 90 minutes. A browser IDE with visible
unit tests you can run whenever you like. Score 200–600; partial credit per test.
**You are not expected to finish** — CodeSignal caps the clock deliberately to measure how
far you get. Full detail in [`docs/01-test-format.md`](docs/01-test-format.md).

The test is not about algorithms. It is about building a small system and then extending it
three times, fast, without breaking what already worked.

---

## The kit

### Reference — read these first, re-read `02` on the morning

| | |
|---|---|
| [`docs/01-test-format.md`](docs/01-test-format.md) | Exactly what the test is: structure, scoring, environment, rules |
| [`docs/02-traps.md`](docs/02-traps.md) | **36 traps** that cost real candidates real levels. The highest-value page here |
| [`docs/03-python-cheatsheet.md`](docs/03-python-cheatsheet.md) | The nine patterns that actually appear, and the Python to type for each |
| [`docs/04-architecture-playbook.md`](docs/04-architecture-playbook.md) | The one skeleton that solves every ICF problem, and the five decisions you make in minute 1–3 |
| [`docs/05-timing-protocol.md`](docs/05-timing-protocol.md) | The minute-by-minute 90-minute plan and triage rules |
| [`docs/06-scoring-and-strategy.md`](docs/06-scoring-and-strategy.md) | What your score means, and a decision tree for when you're stuck |

### Drills — 10 × ~15 minutes, one primitive each

Each has a spec, a stubbed `solution.py`, a test suite, and a worked `reference.py`.

| Drill | Skill | Level it serves |
|---|---|---|
| `d01_top_n_ranking` | Ranking with tie-breaks, filtered pools, two output formats | L2 |
| `d02_ttl_lifetimes` | Half-open intervals, overwrite-resets-TTL, lazy expiry | L3 |
| `d03_prefix_and_format` | Both prefix shapes, exact output punctuation | L2 |
| `d04_deferred_effects` | The cashback pattern and the `_settle()` discipline | L3 |
| `d05_point_in_time_history` | Historical queries and the "includes the op *at* `time_at`" rule | L4 |
| `d06_merge_entities` | Merge: balance, additive metric, inherited history, identity | L4 |
| `d07_snapshot_restore` | Backup/restore with lifespan recalculation | L4 |
| `d08_interval_sessions` | Session accumulation and window overlap | L1–L3 |
| `d09_capacity_quota` | Quotas, ownership, reject-don't-clamp | L1–L3 |
| `d10_backward_compat_refactor` | **Starts from working code** — extend it without breaking it | L3 |

### Mocks — 6 × 90 minutes, full four-level exams

| Mock | Domain | L2 is | L3 is | L4 is |
|---|---|---|---|---|
| `m1_cloud_storage` | File hosting | prefix+suffix search | users & quotas, merge | backup / restore |
| `m2_banking` | Banking | top spenders | cashback | merge + balance history |
| `m3_inmemory_db` | Key-value DB | prefix scan | TTL + `_at` twins | backup / restore |
| `m4_fx_platform` | FX payments | per-currency ranking | expiring quotes | merge + history |
| `m5_worker_hours` | Attendance | position ranking | promotions & salary | double-pay periods |
| `m6_metrics` | Monitoring | sliding-window aggregates | retention | snapshot / rollback |

`m2_banking` is the closest to the canonical ICF problem — variants of it appear
constantly. **If you only do one mock cold and timed, do that one.**

---

## The two-week plan

One to two hours a day. Do the sessions marked **timed** with `./run timer 90` running in a
second terminal, phone in another room.

| Day | Work | Time |
|---|---|---|
| **1** | Read `docs/01`, `02`, `05`. Then drills `d01`, `d02`, `d03`. | 90 min |
| **2** | Read `docs/03`, `04`. Type the skeleton from memory into a scratch file. Drills `d04`, `d09`. | 75 min |
| **3** | Drills `d05`, `d06` — the two Level-4 primitives. Take your time; `d06` is the hard one. | 75 min |
| **4** | Drills `d07`, `d08`, `d10`. | 75 min |
| **5** | **Mock 1 (cloud storage), timed.** Then review: which trap number bit you? | 2 hrs |
| **6** | Re-do only the levels you failed on Mock 1, untimed, reading `reference.py` after. Re-do any drill whose skill was the cause. | 60 min |
| **7** | **Mock 2 (banking), timed.** This is the important one. | 2 hrs |
| **8** | Review Mock 2 line by line against `reference.py`. Type the L1 skeleton from `docs/04` from memory, twice. | 75 min |
| **9** | **Mock 3 (in-memory DB), timed.** Focus: the Level-3 delegation refactor. | 2 hrs |
| **10** | **Mock 5 (worker hours), timed.** Focus: string returns and interval maths. | 2 hrs |
| **11** | **Mock 4 (FX platform), timed.** The hardest state model. | 2 hrs |
| **12** | **Mock 6 (metrics), timed.** Sliding windows and rollback. | 2 hrs |
| **13** | `./run reset m2 && ./run m2` — redo banking cold. You should now be at Level 4 by 1:05. | 2 hrs |
| **14** | Light. Re-read `docs/02` and `docs/06`. Two drills for warmth. Sleep. | 45 min |

**Compressing to one week:** days 1–4 in two sittings, then mocks 2, 1, 3 timed, then the
day-14 review. Skip mocks 4 and 6 before skipping the banking mock.

### The rule that makes this work

When you finish a mock, **don't just look at the diff to `reference.py`**. Write down which
numbered trap from `docs/02-traps.md` cost you the time. If the same number shows up twice,
redo the drill that covers it before your next mock.

---

## How to run a mock properly

1. `./run timer 90` in a second terminal.
2. Open only `mocks/<name>/level1.md`. It names all four levels in one line each — read
   those four lines and decide your data model **before** reading Level 1 in detail.
3. Write your code in `solution.py`. Don't change the method signatures.
4. `./run m1 1` until green. Then, and only then, open `level2.md`.
5. Before opening each new level, run **all** previous levels.
6. Hard stop at 1:25 on the clock. Run everything. Count what's green.

`reference.py` sits next to your `solution.py` in every directory. It's there for after the
clock stops. Reading it early costs you the only thing this kit can actually give you.

---

## Kit self-check

`./run verify` runs all 16 reference solutions against all 314 tests. If that's green, any
failure you see is yours, not the kit's.
