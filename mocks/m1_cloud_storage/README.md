> Cloud file storage — files, prefix/suffix search, users with quotas, merge, backup & restore.

# Mock 1 — Cloud Storage

**90 minutes. One file: `solution.py`. Four levels.**

```
./run timer 90        # in a second terminal
./run m1 1            # run level 1 tests
./run m1              # run every level (do this before you "finish")
```

### Rules of engagement

1. Open `level1.md`. **Do not open `level2.md` until `./run m1 1` is green.** That is how the
   real test works — later levels are locked.
2. Do not change the method signatures.
3. When a level goes green, run *all* levels before moving on.
4. At 1:25 stop coding, run everything, note your score.

### Scoring yourself

| Levels green | Approx. ICF score |
|---|---|
| 1 | ~300 |
| 1–2 | ~400 |
| 1–3 | ~500 |
| 1–4 | ~600 |

Stuck? `./run --ref m1 3` proves the tests are satisfiable, and `reference.py` is the
worked solution — but read it only after you've stopped the clock.
