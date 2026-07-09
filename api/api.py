import os
import joblib
import pandas as pd
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel  # <-- Fixed missing import here

app = FastAPI(title="Belgian Property Price Predictor API")

# Setup safe dynamic path tracking
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..")) if os.path.basename(CURRENT_DIR) == "api" else CURRENT_DIR
MODEL_PATH = os.path.join(PROJECT_ROOT, "model", "immo_property_sale_XGBoost_model.pkl")

# Data Models
class PropertyDetails(BaseModel):
    latitude: Optional[float]=None  
    longitude: Optional[float]=None 
    bedrooms: int = 1
    livable_surface: float
    bathrooms: int = 1
    toilets: int = 1
    category: str
    province: str
    epc: Optional[str]="unknown"
    building_state: Optional[str]="unknown"
    has_parking: int = 0

class PredictionInput(BaseModel):
    data: PropertyDetails

# Inference Logic
def predict(data: pd.DataFrame) -> float:
    pipeline = joblib.load(MODEL_PATH)
    
    # Force the exact column order your pipeline was trained on
    features = [
        "latitude", "longitude", "bedrooms", "livable_surface",
        "bathrooms", "toilets", "has_parking", "category",
        "province", "epc", "building_state"
    ]
    
    # Select and reorder columns explicitly
    ordered_data = data[features]
    
    return float(pipeline.predict(ordered_data)[0]) # Added [0] to extract scalar value


# API Routes
@app.get("/")
def read_root():
    return "alive"

@app.post("/predict")
def get_prediction(payload: PredictionInput):
    try:
        # Flatten Pydantic dictionary into a 1-row Pandas DataFrame matrix array
        df_dict = {key: [val] for key, val in payload.data.model_dump().items()}
        predicted_price = predict(pd.DataFrame(df_dict))
        
        return {
            "prediction": round(predicted_price, 2),
            "status_code": 200
        }
    except Exception:
        return {
            "prediction": None,
            "status_code": 500
        }
