import os, sys

_STUBS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "stubs"))
if _STUBS not in sys.path:
    sys.path.insert(0, _STUBS)
