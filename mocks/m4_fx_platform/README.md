> FX platform — multi-currency balances, per-currency spend rankings, expiring quotes, client merge.

# Mock 4 — FX Platform

**90 minutes. One file: `solution.py`. Four levels.**

This mock has the most complex state model in the kit. Everything is keyed by
**(client, currency)** rather than by a single id. If your Level 1 stores a scalar balance
per client you will rewrite it at Level 3. Read all four level summaries before you type.

```
./run timer 90
./run m4 1
./run m4
```
