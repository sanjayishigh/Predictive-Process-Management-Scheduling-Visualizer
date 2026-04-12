import pandas as pd
import joblib


model = joblib.load("../models/dnn_priority_scheduler.pkl")


def predict_priority(process):

    features = pd.DataFrame([{
        'burst_time': process['burst_time'],
        'waiting_time': process['waiting_time'],
        'remaining_time': process['remaining_time'],
        'arrival_time': process['arrival_time'],
        'task_type': process['task_type']
    }])

    prediction = model.predict(features)
    probability = model.predict_proba(features)

    return {
        "priority": int(prediction[0]),
        "confidence": float(probability.max())
    }