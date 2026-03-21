import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score


def create_dataset():
    np.random.seed(42)
    n = 1000

    stops      = np.random.randint(1, 15, n)
    distance   = np.random.randint(50, 2000, n)
    hour       = np.random.randint(0, 24, n)
    day        = np.random.randint(0, 7, n)
    is_monsoon = np.random.randint(0, 2, n)
    is_holiday = np.random.randint(0, 2, n)

    delay = (
        stops      * 2.5
        + distance   * 0.01
        + ((hour >= 8)  & (hour <= 10)) * 8
        + ((hour >= 17) & (hour <= 20)) * 10
        + is_monsoon * 15
        + is_holiday * 8
        + np.random.normal(0, 5, n)
    )
    delay = np.clip(delay, 0, 120)

    df = pd.DataFrame({
        "stops":      stops,
        "distance":   distance,
        "hour":       hour,
        "day":        day,
        "is_monsoon": is_monsoon,
        "is_holiday": is_holiday,
        "delay":      delay.round(1)
    })

    df.to_csv("dataset.csv", index=False)
    return df


def train_model():
    df = create_dataset()

    X = df[["stops", "distance", "hour", "day", "is_monsoon", "is_holiday"]]
    y = df["delay"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f} min")
    print(f"R²:  {r2_score(y_test, y_pred):.3f}")

    return model


def predict_delay(model, stops, distance, hour=10):
    features = np.array([[stops, distance, hour, 1, 0, 0]])
    delay = model.predict(features)[0]
    return max(0, round(delay, 1))
