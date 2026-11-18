#!/usr/bin/env python3
"""ICF training runner.  See ./run help"""
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
DRILLS = ROOT / "drills"
MOCKS = ROOT / "mocks"

G, R, Y, B, DIM, X = "\033[32m", "\033[31m", "\033[33m", "\033[34m", "\033[2m", "\033[0m"


def _dirs(base):
    return sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith("_")) if base.exists() else []


def find(token):
    token = token.lower()
    for base in (DRILLS, MOCKS):
        for p in _dirs(base):
            if p.name.lower().startswith(token) or token in p.name.lower():
                return p
    return None


def listing():
    print("\n%sDRILLS%s  (15 min each — one ICF primitive at a time)" % (B, X))
    for p in _dirs(DRILLS):
        print("  %-34s %s" % (p.name, _headline(p)))
    print("\n%sMOCKS%s   (90 min each — full 4-level exam)" % (B, X))
    for p in _dirs(MOCKS):
        print("  %-34s %s" % (p.name, _headline(p)))
    print("\n%s./run <name> [level]   ./run --ref <name>   ./run verify   ./run timer 90%s\n" % (DIM, X))


def _headline(p):
    f = p / "README.md"
    if not f.exists():
        return ""
    for line in f.read_text().splitlines():
        if line.startswith("> "):
            h = line[2:].strip()
            return h if len(h) <= 76 else h[:73] + "..."
    return ""


def tests_for(p, level=None):
    if level:
        t = p / ("test_level%s.py" % level)
        return [t] if t.exists() else []
    return sorted(p.glob("test_*.py"))


def run(p, level=None, ref=False, quiet=False):
    tests = tests_for(p, level)
    if not tests:
        print("%sno tests found for %s level=%s%s" % (R, p.name, level, X))
        return False
    env = dict(os.environ)
    if ref:
        env["ICF_REF"] = "1"
    ok = True
    for t in tests:
        r = subprocess.run([sys.executable, "-m", "unittest", "-v", t.stem],
                           cwd=str(p), env=env,
                           capture_output=quiet, text=True)
        if r.returncode != 0:
            ok = False
            if quiet:
                print("%s  FAIL %s/%s%s" % (R, p.name, t.name, X))
                tail = (r.stderr or "").strip().splitlines()[-12:]
                print(DIM + "\n".join("      " + l for l in tail) + X)
    if quiet and ok:
        print("%s  ok   %s%s" % (G, p.name, X))
    return ok


def verify():
    print("%sself-check: every reference solution against every test%s" % (B, X))
    allok = True
    for base in (DRILLS, MOCKS):
        for p in _dirs(base):
            if not (p / "reference.py").exists():
                continue
            allok &= run(p, ref=True, quiet=True)
    print(("%sALL REFERENCES PASS%s" % (G, X)) if allok else ("%sSOME REFERENCES FAIL%s" % (R, X)))
    return allok


def timer(minutes):
    """Exam clock. Checkpoints are scaled from the 90-minute protocol in docs/05."""
    total = int(float(minutes) * 60)
    scale = total / 5400.0
    marks = [
        (total - int(15 * 60 * scale), "L1 should be green"),
        (total - int(33 * 60 * scale), "L2 should be green"),
        (total - int(65 * 60 * scale), "L3 should be green"),
        (int(5 * 60 * scale), "STOP CODING. RUN EVERY LEVEL. SUBMIT."),
    ]
    fired = set()
    start = time.time()
    try:
        while True:
            left = total - int(time.time() - start)
            if left < 0:
                break
            m, s_ = divmod(left, 60)
            colour = R if left <= int(5 * 60 * scale) else (Y if left < total * 0.3 else G)
            sys.stdout.write("\r%s  %02d:%02d remaining%s   " % (colour, m, s_, X))
            sys.stdout.flush()
            for at, label in marks:
                if left <= at and (at, label) not in fired:
                    fired.add((at, label))
                    sys.stdout.write("\n%s  >>> %02d:%02d left -- %s%s\n" %
                                     (Y, m, s_, label, X))
                    sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        return
    print("\n%sTIME. Stop typing, run every level, submit.%s" % (R, X))


def main(argv):
    if not argv or argv[0] in ("list", "ls"):
        return listing()
    if argv[0] in ("help", "-h", "--help"):
        return print(__doc__ + """
  ./run                 list drills and mocks
  ./run d01             run drill d01 tests against YOUR solution.py
  ./run m2              run all 4 levels of mock 2
  ./run m2 3            run only level 3 of mock 2
  ./run --ref m2 3      run the reference solution (to see expected behaviour / unstick yourself)
  ./run verify          self-check the kit: all reference solutions vs all tests
  ./run timer 90        90-minute exam countdown with level checkpoints
  ./run reset m2        restore mock 2's solution.py to the blank starter
""")
    if argv[0] == "verify":
        return sys.exit(0 if verify() else 1)
    if argv[0] == "timer":
        return timer(argv[1] if len(argv) > 1 else 90)
    if argv[0] == "reset":
        p = find(argv[1])
        starter = p / "_starter.py"
        (p / "solution.py").write_text(starter.read_text())
        return print("%sreset %s/solution.py%s" % (G, p.name, X))
    ref = False
    if argv[0] in ("--ref", "-r"):
        ref, argv = True, argv[1:]
    p = find(argv[0])
    if p is None:
        print("%sno drill/mock matching %r%s" % (R, argv[0], X))
        return listing()
    level = argv[1] if len(argv) > 1 else None
    sys.exit(0 if run(p, level, ref) else 1)


if __name__ == "__main__":
    main(sys.argv[1:])
