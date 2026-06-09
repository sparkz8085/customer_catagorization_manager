import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, PowerTransformer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV

from database.connection import get_customer_dataframe
from config import (
    MODEL_FEATURES, OUTLIER_FEATURES, MODEL_PATH, PREPROCESSOR_PATH,
    PCA_COMPONENTS, KMEANS_CLUSTERS, GRID_SEARCH_PARAM_GRID, ARTIFACTS_DIR
)

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and generates custom features for the ML model.
    """
    dataset = df.copy()
    
    # Age of the customer
    dataset['Age'] = 2022 - dataset['Year_Birth']
    
    # Categorical encoding
    dataset["Education"].replace({"Basic": 0, "2n Cycle": 1, "Graduation": 2, "Master": 3, "PhD": 4}, inplace=True)
    dataset['Marital_Status'].replace({"Married": 1, "Together": 1, "Absurd": 0, "Widow": 0, "YOLO": 0, "Divorced": 0, "Single": 0, "Alone": 0}, inplace=True)
    
    # Family stats
    dataset['Children'] = dataset['Kidhome'] + dataset['Teenhome']
    dataset['Family_Size'] = dataset['Marital_Status'] + dataset['Children'] + 1
    dataset["Parental Status"] = np.where(dataset["Children"] > 0, 1, 0)
    
    # Spending & Promotions
    dataset['Total_Spending'] = (dataset["MntWines"] + dataset["MntFruits"] + 
                                 dataset["MntMeatProducts"] + dataset["MntFishProducts"] + 
                                 dataset["MntSweetProducts"] + dataset["MntGoldProds"])
    
    dataset["Total Promo"] = (dataset["AcceptedCmp1"] + dataset["AcceptedCmp2"] + 
                              dataset["AcceptedCmp3"] + dataset["AcceptedCmp4"] + 
                              dataset["AcceptedCmp5"])
    
    # Days as customer
    dataset['Dt_Customer'] = pd.to_datetime(dataset['Dt_Customer'], format='mixed', dayfirst=True)
    dataset['Days_as_Customer'] = (datetime.today() - dataset['Dt_Customer']).dt.days
    
    dataset['Offers_Responded_To'] = (dataset['AcceptedCmp1'] + dataset['AcceptedCmp2'] + 
                                      dataset['AcceptedCmp3'] + dataset['AcceptedCmp4'] + 
                                      dataset['AcceptedCmp5'] + dataset['Response'])
    
    # Rename columns to match schema expectations
    dataset.rename(columns={
        "Marital_Status": "Marital Status",
        "MntWines": "Wines",
        "MntFruits": "Fruits",
        "MntMeatProducts": "Meat",
        "MntFishProducts": "Fish",
        "MntSweetProducts": "Sweets",
        "MntGoldProds": "Gold",
        "NumWebPurchases": "Web",
        "NumCatalogPurchases": "Catalog",
        "NumStorePurchases": "Store",
        "NumDealsPurchases": "Discount Purchases"
    }, inplace=True)
    
    # Filter only model features
    dataset = dataset[MODEL_FEATURES]
    return dataset

def train_model():
    """
    Runs the entire training pipeline: Ingestion -> Preprocessing -> KMeans labels -> LogisticRegression fitting.
    """
    print("[TRAIN] Starting model training pipeline...")
    
    # 1. Fetch data
    df = get_customer_dataframe()
    
    # 2. Extract features
    features_df = extract_features(df)
    
    # 3. Create preprocessing pipelines
    # Divide features into standard numeric and outlier numeric
    numeric_features = [col for col in features_df.columns if features_df[col].dtype != 'O']
    std_features = [x for x in numeric_features if x not in OUTLIER_FEATURES]
    
    std_pipeline = Pipeline(steps=[
        ("Imputer", SimpleImputer(strategy="constant", fill_value=0)),
        ("StandardScaler", StandardScaler())
    ])
    
    outlier_pipeline = Pipeline(steps=[
        ("Imputer", SimpleImputer(strategy="constant", fill_value=0)),
        ("PowerTransformer", PowerTransformer(standardize=True))
    ])
    
    preprocessor = ColumnTransformer(transformers=[
        ("Standard Pipeline", std_pipeline, std_features),
        ("Outlier Pipeline", outlier_pipeline, OUTLIER_FEATURES)
    ])
    
    # Fit preprocessor
    print("[TRAIN] Fitting preprocessing pipeline...")
    X_preprocessed = preprocessor.fit_transform(features_df)
    
    # Reconstruct preprocessed DataFrame in the correct feature order
    transformed_cols = std_features + OUTLIER_FEATURES
    X_preprocessed_df = pd.DataFrame(X_preprocessed, columns=transformed_cols)
    X_preprocessed_df = X_preprocessed_df[MODEL_FEATURES]
    
    # 4. Generate cluster labels using PCA and KMeans
    print("[TRAIN] Generating customer clusters via PCA & KMeans...")
    pca = PCA(n_components=PCA_COMPONENTS, random_state=42)
    X_pca = pca.fit_transform(X_preprocessed_df)
    
    kmeans = KMeans(n_clusters=KMEANS_CLUSTERS, random_state=42)
    cluster_labels = kmeans.fit_predict(X_pca)
    
    # 5. Fit LogisticRegression classifier using GridSearchCV
    print("[TRAIN] Running GridSearch hyperparameter tuning for Logistic Regression...")
    lr = LogisticRegression()
    grid_search = GridSearchCV(
        estimator=lr,
        param_grid=GRID_SEARCH_PARAM_GRID,
        cv=3,
        verbose=1
    )
    grid_search.fit(X_preprocessed_df, cluster_labels)
    best_model = grid_search.best_estimator_
    print(f"[TRAIN] Best model cross-validation score: {grid_search.best_score_:.4f}")
    
    # 6. Save model and preprocessor to artifacts
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(best_model, f)
    with open(PREPROCESSOR_PATH, "wb") as f:
        pickle.dump(preprocessor, f)
        
    print(f"[SUCCESS] Saved model to: {MODEL_PATH}")
    print(f"[SUCCESS] Saved preprocessor to: {PREPROCESSOR_PATH}")
    print("[TRAIN] Model training completed successfully!")
