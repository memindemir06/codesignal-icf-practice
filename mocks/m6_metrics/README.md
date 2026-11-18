> Metrics service — samples, sliding-window aggregates, retention policies, snapshot & rollback.

# Mock 6 — Metrics Service

**90 minutes. One file: `solution.py`. Four levels.**

The one that drills **sliding windows** — the only common ICF primitive the other five
mocks don't cover — and gives you a second rep at snapshot/rollback with a twist: it is
sample *ages* that must be preserved, not expiry times.

```
./run timer 90
./run m6 1
./run m6
```
