import os
import pickle
import pandas as pd
from config import MODEL_PATH, PREPROCESSOR_PATH, MODEL_FEATURES, OUTLIER_FEATURES

# Whitelist of allowed classes to mitigate insecure deserialization (RCE)
ALLOWED_CLASSES = {
    "sklearn.linear_model._logistic.LogisticRegression",
    "sklearn.compose._column_transformer.ColumnTransformer",
    "sklearn.compose._column_transformer._RemainderColsList",
    "sklearn.pipeline.Pipeline",
    "sklearn.impute._base.SimpleImputer",
    "sklearn.preprocessing._data.StandardScaler",
    "sklearn.preprocessing._data.PowerTransformer",
    "numpy.core.multiarray._reconstruct",
    "numpy.core.multiarray.scalar",
    "numpy.ndarray",
    "numpy.dtype",
    "builtins.slice",
}

class SafeUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        class_path = f"{module}.{name}"
        if class_path not in ALLOWED_CLASSES:
            raise pickle.UnpicklingError(f"Unsafe class/module '{class_path}' blocked during unpickling.")
        return super().find_class(module, name)

def safe_load_pickle(file_path: str):
    # Enforce MODEL_TRUSTED environment variable check
    if os.getenv("MODEL_TRUSTED", "0") != "1":
        raise ValueError(
            "Security policy violation: Loading serialized model and preprocessor objects is disabled "
            "unless the environment variable MODEL_TRUSTED is set to '1' in your environment configuration."
        )
    with open(file_path, "rb") as f:
        return SafeUnpickler(f).load()

def predict_customer(input_values: list) -> int:
    """
    Loads preprocessor and model, shapes the inputs, preprocesses them, and runs model prediction.
    First tries loading from the main artifacts paths, falls back to ml/ model paths if unavailable.
    """
    model_path = MODEL_PATH
    preprocessor_path = PREPROCESSOR_PATH
    
    # Check fallback paths
    if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
        fallback_model = os.path.abspath(os.path.join(os.path.dirname(__file__), "model.pkl"))
        fallback_preprocessor = os.path.abspath(os.path.join(os.path.dirname(__file__), "preprocessor.pkl"))
        if os.path.exists(fallback_model) and os.path.exists(fallback_preprocessor):
            model_path = fallback_model
            preprocessor_path = fallback_preprocessor
        else:
            raise FileNotFoundError("Trained model or preprocessor artifacts not found. Please run training first.")
            
    model = safe_load_pickle(model_path)
    preprocessor = safe_load_pickle(preprocessor_path)
        
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
