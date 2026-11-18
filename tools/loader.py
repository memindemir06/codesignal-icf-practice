"""Loads a drill/mock implementation by file path so several can coexist in one process."""
import importlib.util
import os
import pathlib
import sys


def load(test_file, ref=None):
    d = pathlib.Path(test_file).resolve().parent
    if ref is None:
        ref = bool(os.environ.get("ICF_REF"))
    fname = "reference.py" if ref else "solution.py"
    path = d / fname
    if not path.exists():
        raise SystemExit("missing %s" % path)
    modname = "icf_%s_%s" % (d.name, "ref" if ref else "sol")
    if modname in sys.modules:
        return sys.modules[modname]
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod
