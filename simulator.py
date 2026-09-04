import sys
import backend.simulator as _mod
sys.modules['simulator'] = _mod
for _k, _v in _mod.__dict__.items():
    if not _k.startswith("__"):
        globals()[_k] = _v
