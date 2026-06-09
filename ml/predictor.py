import os
import pickle
import pandas as pd
from config import MODEL_PATH, PREPROCESSOR_PATH, MODEL_FEATURES, OUTLIER_FEATURES

def predict_customer(input_values: list) -> int:
    """
    Loads preprocessor and model, shapes the inputs, preprocesses them, and runs model prediction.
    First tries loading from the main artifacts paths, falls back to ml/ model paths if unavailable.
    """
    model_path = MODEL_PATH
    preprocessor_path = PREPROCESSOR_PATH
    
    # Check fallback paths
    if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
        fallback_model = os.path.join("ml", "model.pkl")
        fallback_preprocessor = os.path.join("ml", "preprocessor.pkl")
        if os.path.exists(fallback_model) and os.path.exists(fallback_preprocessor):
            model_path = fallback_model
            preprocessor_path = fallback_preprocessor
        else:
            raise FileNotFoundError("Trained model or preprocessor artifacts not found. Please run training first.")
            
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(preprocessor_path, "rb") as f:
        preprocessor = pickle.load(f)
        
    # Shape input list into a DataFrame with MODEL_FEATURES columns
    input_df = pd.DataFrame([input_values], columns=MODEL_FEATURES)
    
    # Cast input columns to float/int
    for col in input_df.columns:
        input_df[col] = pd.to_numeric(input_df[col])
        
    # Transform using preprocessor
    X_preprocessed = preprocessor.transform(input_df)
    
    # Reorder transformer output columns to original order
    numeric_features = [col for col in input_df.columns if input_df[col].dtype != 'O']
    std_features = [x for x in numeric_features if x not in OUTLIER_FEATURES]
    transformed_cols = std_features + OUTLIER_FEATURES
    
    X_preprocessed_df = pd.DataFrame(X_preprocessed, columns=transformed_cols)
    X_preprocessed_df = X_preprocessed_df[MODEL_FEATURES]
    
    # Run prediction
    prediction = model.predict(X_preprocessed_df)
    return int(prediction[0])
