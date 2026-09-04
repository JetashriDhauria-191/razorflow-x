import sys
import backend.models as _bm
sys.modules['models'] = _bm

for _k, _v in _bm.__dict__.items():
    if not _k.startswith("__"):
        globals()[_k] = _v
