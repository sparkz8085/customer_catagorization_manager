import os

# Database Configuration
MONGO_DB_URL_KEY = "MONGO_DB_URL"
DATABASE_NAME = "customer_db"
COLLECTION_NAME = "marketing_records"

# Model Artifact Paths
ARTIFACTS_DIR = "artifacts"
MODEL_FILE_NAME = "model.pkl"
PREPROCESSOR_FILE_NAME = "preprocessor.pkl"

MODEL_PATH = os.path.join(ARTIFACTS_DIR, MODEL_FILE_NAME)
PREPROCESSOR_PATH = os.path.join(ARTIFACTS_DIR, PREPROCESSOR_FILE_NAME)

# Data Schema configurations
DROP_COLUMNS = ["ID", "Z_CostContact", "Z_Revenue"]

RAW_COLUMNS = [
    "Year_Birth", "Education", "Marital_Status", "Income", "Kidhome", "Teenhome",
    "Dt_Customer", "Recency", "MntWines", "MntFruits", "MntMeatProducts",
    "MntFishProducts", "MntSweetProducts", "MntGoldProds", "NumDealsPurchases",
    "NumWebPurchases", "NumCatalogPurchases", "NumStorePurchases", "NumWebVisitsMonth",
    "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5", "AcceptedCmp1", "AcceptedCmp2",
    "Complain", "Response"
]

MODEL_FEATURES = [
    "Age", "Education", "Marital Status", "Parental Status", "Children", "Income",
    "Total_Spending", "Days_as_Customer", "Recency", "Wines", "Fruits", "Meat",
    "Fish", "Sweets", "Gold", "Web", "Catalog", "Store", "Discount Purchases",
    "Total Promo", "NumWebVisitsMonth"
]

OUTLIER_FEATURES = ["Wines", "Fruits", "Meat", "Fish", "Sweets", "Gold", "Age", "Total_Spending"]

# Training settings
EXPECTED_ACCURACY = 0.6
SPLIT_RATIO = 0.2
PCA_COMPONENTS = 2
KMEANS_CLUSTERS = 3
GRID_SEARCH_PARAM_GRID = {
    'C': [1000],
    'max_iter': [113],
    'multi_class': ['auto'],
    'penalty': ['l2'],
    'solver': ['lbfgs']
}

APP_HOST = "0.0.0.0"
APP_PORT = 5000

