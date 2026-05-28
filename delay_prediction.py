# ============================================================
#  MODULE  : Delay Prediction
#  MEMBER  : Abhay Singh (Student ID: 240111781) — Team Lead
#  ROLE    : Machine Learning & Dataset Module
#  METHOD  : Random Forest Regression (100 Decision Trees)
# ============================================================

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

FEATURES = ["stops","distance","hour","day","is_monsoon","is_holiday"]

def create_dataset(n=1000):
    np.random.seed(42)
    s, d, h, dy = (np.random.randint(1,15,n), np.random.randint(50,2000,n),
                   np.random.randint(0,24,n),  np.random.randint(0,7,n))
    im, ih = np.random.randint(0,2,n), np.random.randint(0,2,n)
    delay  = np.clip(
        s*2.5 + d*0.01
        + ((h>=8)&(h<=10))*8 + ((h>=17)&(h<=20))*10
        + im*15 + ih*8 + np.random.normal(0,5,n), 0, 120)
    df = pd.DataFrame({"stops":s,"distance":d,"hour":h,"day":dy,
                       "is_monsoon":im,"is_holiday":ih,"delay":delay.round(1)})
    df.to_csv("dataset.csv", index=False)
    return df

def train_model():
    df = create_dataset()
    X, y = df[FEATURES], df["delay"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(Xtr, ytr)
    yp = model.predict(Xte)
    print(f"MAE: {mean_absolute_error(yte,yp):.2f}  R2: {r2_score(yte,yp):.3f}")
    return model

def predict_delay(model, stops, distance, hour=10):
    return max(0, round(model.predict([[stops,distance,hour,1,0,0]])[0], 1))

def get_model_metrics(model):
    df = create_dataset()
    yp = model.predict(df[FEATURES])
    return round(mean_absolute_error(df["delay"],yp),2), round(r2_score(df["delay"],yp),3)

def get_feature_importance(model):
    return dict(zip(FEATURES, model.feature_importances_))
