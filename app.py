import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_BACKEND = _ROOT / "backend"
_backend_dir = str(_BACKEND)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

_spec = importlib.util.spec_from_file_location("_predictive_scheduler_backend", _BACKEND / "app.py")
_backend_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_backend_mod)
app = _backend_mod.app

if __name__ == "__main__":
    app.run(debug=True, port=5000)
