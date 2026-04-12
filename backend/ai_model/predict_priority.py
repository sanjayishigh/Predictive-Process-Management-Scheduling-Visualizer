import os
import warnings

import pandas as pd

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
model_path = os.path.join(base_dir, "models", "dnn_priority_scheduler.pkl")

_model = None
_load_attempted = False


def _heuristic_priority(process):
    """Used when the pickle cannot be loaded (NumPy/sklearn version mismatch)."""
    w = int(process.get("waiting_time", 0))
    rem = max(1, int(process.get("remaining_time", 1)))
    burst = max(1, int(process.get("burst_time", 1)))
    tt = int(process.get("task_type", 0))
    priority = int(min(99, max(1, w * 4 + (burst - rem + 1) * 2 + tt * 3)))
    conf = 0.55 + min(0.4, w * 0.02 + (1.0 / rem) * 0.15)
    return {"priority": priority, "confidence": float(min(0.99, conf))}


def _get_model():
    global _model, _load_attempted
    if _load_attempted:
        return _model
    _load_attempted = True
    try:
        import joblib

        _model = joblib.load(model_path)
    except Exception as e:
        _model = None
        warnings.warn(
            f"Could not load {model_path}: {e!r}. "
            "Using heuristic priority (reinstall deps from requirements.txt to use the trained model).",
            UserWarning,
            stacklevel=2,
        )
    return _model


def predict_priority(process):
    model = _get_model()
    if model is None:
        return _heuristic_priority(process)

    features = pd.DataFrame(
        [
            {
                "burst_time": process["burst_time"],
                "waiting_time": process["waiting_time"],
                "remaining_time": process["remaining_time"],
                "arrival_time": process["arrival_time"],
                "task_type": process["task_type"],
            }
        ]
    )

    prediction = model.predict(features)
    probability = model.predict_proba(features)

    return {
        "priority": int(prediction[0]),
        "confidence": float(probability.max()),
    }
