import pandas as pd
import joblib

# Load model objects
pipeline = joblib.load("preprocessing_pipeline.joblib")
model = joblib.load("home_price_model.joblib")

# Sample inputs
sample = pd.DataFrame([{
    "beds": 2,
    "baths": 1,
    "sqft": 900
}])

X = pipeline.transform(sample)
prediction = model.predict(X)

print(prediction)