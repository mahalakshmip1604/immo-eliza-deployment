import os
import joblib
import pandas as pd

# 1. ESTABLISH ABSOLUTE REUSABLE DIRECTORY PATHS
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "model", "immo_property_sale_XGBoost_model.pkl"))


def load_prediction_pipeline(export_path: str):
    """Loads the pre-trained, unified scikit-learn binary object wrapper from disk."""
    if not os.path.exists(export_path):
        raise FileNotFoundError(
            f"\n[ERROR] Model artifact missing! Checked absolute path:\n"
            f"👉 {export_path}\n"
            f"Please run your training script to generate the model file first."
        )
    return joblib.load(export_path)


def preprocess(data: pd.DataFrame) -> pd.DataFrame:
    """Preprocesses input data. Ensures it is a DataFrame and handles basic validation."""
    # Convert dict to DataFrame if a single property is passed as a dictionary
    if isinstance(data, dict):
        data = pd.DataFrame([data])
    
    # Add any explicit programming validation or feature engineering here if needed
    return data


def predict(data: pd.DataFrame) -> float:
    """Accepts property data, preprocesses it, and returns the predicted price."""
    # 1. Load the pipeline
    pipeline = load_prediction_pipeline(MODEL_PATH)
    
    # 2. Run preprocessing steps
    cleaned_data = preprocess(data)
    
    # 3. Generate prediction array
    predictions = pipeline.predict(cleaned_data)
    
    # 4. Return single float or list of floats
    return float(predictions[0]) if len(predictions) == 1 else predictions.tolist()


def generate_unseen_property() -> pd.DataFrame:
    """Generates a structured DataFrame containing a new Belgian property profile."""
    new_listing = {
        # Numeric Features
        "latitude": [50.8503],
        "longitude": [4.3517],
        "bedrooms":2,
        "livable_surface": [100.0],
        "bathrooms":1,
        "toilets":1,  
        "has_parking":1,
        
        # Categorical Features
        "category": ["apartment"],
        "province": ["Brussels"],
        "epc": ["E"],
        "building_state": ["good"]
    }
    return pd.DataFrame(new_listing)


def main():
    """Execution orchestrator wrapper for streaming property price predictions."""
    # 1. Acquire sample live feature data
    new_data = generate_unseen_property()
    print("\n--- Input Property Features ---")
    print(new_data.to_string(index=False))
    
    # 2. Direct calculation inference via required predict() function
    predicted_price = predict(new_data)
    
    # 3. Output validation logs
    print("\n" + "=" * 40)
    print("         PRICE PREDICTION RESULT        ")
    print("=" * 40)
    print(f"Estimated Market Value: {predicted_price:,.2f} EUR")
    print("=" * 40)


if __name__ == "__main__":
    main()
