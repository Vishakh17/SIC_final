import numpy as np
from sklearn.ensemble import RandomForestRegressor

def train_model(data):
    X = data[["hour", "day", "month"]]
    y = data["energy"]

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X, y)
    return model

def predict_next_24(model):
    future = {
        "hour": np.arange(24),
        "day": [1]*24,
        "month": [1]*24
    }

    import pandas as pd
    df = pd.DataFrame(future)
    df["prediction"] = model.predict(df)
    return df