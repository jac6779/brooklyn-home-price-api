from fastapi import FastAPI
from pydantic import BaseModel, Field
import joblib
import pandas as pd

app = FastAPI(
    title="Brooklyn Home Price Prediction API",
    description="Predict Brooklyn home prices from raw property inputs.",
    version="1.0.0"
)

pipeline = joblib.load("models/brooklyn_price_pipeline_raw_inputs.joblib")


class PredictionRequest(BaseModel):
    neighborhood: str = Field(..., description="Neighborhood name used by the model")
    building_class_category: str = Field(..., description="Grouped building class category")
    gross_sqft: float = Field(..., description="Gross square footage of the property")
    dist_to_station: float = Field(..., description="Distance to nearest subway station in miles")
    build_age_yrs: float = Field(..., description="Building age in years")
    within_half_mi: int = Field(..., description="1 if property is within 0.5 miles of a subway station, otherwise 0")

    model_config = {
        "json_schema_extra": {
            "example": {
                "neighborhood": "bay_ridge",
                "building_class_category": "one_family_dwellings",
                "gross_sqft": 2500,
                "dist_to_station": 0.3,
                "build_age_yrs": 75,
                "within_half_mi": 1
            }
        }
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(payload: PredictionRequest):
    df = pd.DataFrame([payload.model_dump()])
    predicted_log_price = float(pipeline.predict(df)[0])
    predicted_price = float(10 ** predicted_log_price)

    return {
        "predicted_price_usd": round(predicted_price, 2)
    }