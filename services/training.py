import os
import pickle
import json
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, PowerTransformer
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering, DBSCAN, KMeans
from sklearn.mixture import GaussianMixture
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    calinski_harabasz_score,
    confusion_matrix,
    davies_bouldin_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    silhouette_score,
)
from sklearn.model_selection import GridSearchCV, train_test_split

from database.connection import get_customer_dataframe
from config import (
    MODEL_FEATURES, OUTLIER_FEATURES, MODEL_PATH, PREPROCESSOR_PATH,
    PCA_COMPONENTS, KMEANS_CLUSTERS, GRID_SEARCH_PARAM_GRID, SPLIT_RATIO,
    ARTIFACTS_DIR
)

try:
    import hdbscan
except ImportError:
    hdbscan = None

EVALUATION_DIR = os.path.join(ARTIFACTS_DIR, "evaluation")
CLUSTERING_RESULTS_JSON = os.path.join(EVALUATION_DIR, "clustering_comparison.json")
CLUSTERING_RESULTS_CSV = os.path.join(EVALUATION_DIR, "clustering_comparison.csv")

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and generates custom features for the ML model.
    """
    dataset = df.copy()
    
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

def _performance_label(score: float) -> str:
    if score >= 0.85:
        return "good"
    if score >= 0.65:
        return "average"
    return "poor"

def _gap_label(train_score: float, test_score: float) -> str:
    gap = train_score - test_score
    if gap > 0.10:
        return "possible overfitting"
    if train_score < 0.65 and test_score < 0.65:
        return "possible underfitting"
    return "no strong overfitting/underfitting signal"

def _print_classification_metrics(model, X_train, X_test, y_train, y_test):
    train_predictions = model.predict(X_train)
    test_predictions = model.predict(X_test)

    train_accuracy = accuracy_score(y_train, train_predictions)
    test_accuracy = accuracy_score(y_test, test_predictions)
    precision = precision_score(y_test, test_predictions, average="weighted", zero_division=0)
    recall = recall_score(y_test, test_predictions, average="weighted", zero_division=0)
    f1 = f1_score(y_test, test_predictions, average="weighted", zero_division=0)
    matrix = confusion_matrix(y_test, test_predictions)

    roc_auc = None
    if hasattr(model, "predict_proba") and len(np.unique(y_test)) > 1:
        try:
            probabilities = model.predict_proba(X_test)
            roc_auc = roc_auc_score(y_test, probabilities, multi_class="ovr", average="weighted")
        except ValueError:
            roc_auc = None

    print("\n[EVALUATION] Classification metrics for Logistic Regression")
    print("-" * 62)
    print(f"Training accuracy : {train_accuracy:.4f}")
    print(f"Testing accuracy  : {test_accuracy:.4f} ({_performance_label(test_accuracy)})")
    print(f"Precision         : {precision:.4f} ({_performance_label(precision)})")
    print(f"Recall            : {recall:.4f} ({_performance_label(recall)})")
    print(f"F1 score          : {f1:.4f} ({_performance_label(f1)})")
    print(f"ROC-AUC           : {roc_auc:.4f}" if roc_auc is not None else "ROC-AUC           : not applicable")
    print("Confusion matrix  :")
    print(matrix)
    print(f"Fit diagnosis     : {_gap_label(train_accuracy, test_accuracy)}")
    print("\nMetric guide:")
    print("Accuracy measures the share of correct cluster classifications.")
    print("Precision measures how reliable each predicted class is.")
    print("Recall measures how many true class members are found.")
    print("F1 balances precision and recall in one score.")
    print("ROC-AUC measures class separability when probability scores are available.")
    print("The confusion matrix shows true labels by row and predicted labels by column.")

    return {
        "train_accuracy": train_accuracy,
        "test_accuracy": test_accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
        "confusion_matrix": matrix,
    }

def _print_clustering_metrics(X_pca, cluster_labels):
    silhouette = silhouette_score(X_pca, cluster_labels)
    davies_bouldin = davies_bouldin_score(X_pca, cluster_labels)
    calinski_harabasz = calinski_harabasz_score(X_pca, cluster_labels)

    print("\n[EVALUATION] Clustering metrics for K-Means")
    print("-" * 62)
    print(f"Silhouette score        : {silhouette:.4f} ({_performance_label((silhouette + 1) / 2)})")
    print(f"Davies-Bouldin index    : {davies_bouldin:.4f} ({'good' if davies_bouldin < 0.75 else 'average' if davies_bouldin < 1.50 else 'poor'})")
    print(f"Calinski-Harabasz score : {calinski_harabasz:.4f}")
    print("\nMetric guide:")
    print("Silhouette ranges from -1 to 1; higher means better separated clusters.")
    print("Davies-Bouldin is better when lower; it penalizes overlapping clusters.")
    print("Calinski-Harabasz is better when higher; compare it across experiments on the same data.")

    return {
        "silhouette_score": silhouette,
        "davies_bouldin_index": davies_bouldin,
        "calinski_harabasz_score": calinski_harabasz,
    }

def _score_clustering_result(row: dict) -> float:
    if not row["valid"]:
        return float("-inf")

    silhouette_component = row["silhouette_score"]
    davies_component = 1 / (1 + row["davies_bouldin_index"])
    ch_component = min(row["calinski_harabasz_score"] / 10000, 1)
    noise_penalty = row["noise_ratio"] * 0.25
    tiny_cluster_penalty = 0.10 if row["min_cluster_size"] < max(10, int(row["sample_count"] * 0.01)) else 0

    return (0.65 * silhouette_component) + (0.25 * davies_component) + (0.10 * ch_component) - noise_penalty - tiny_cluster_penalty

def _cluster_labels_are_valid(labels: np.ndarray) -> tuple[bool, np.ndarray, int, float, int]:
    labels = np.asarray(labels)
    non_noise_mask = labels != -1
    valid_labels = labels[non_noise_mask]
    unique_labels = np.unique(valid_labels)
    noise_ratio = 1 - (non_noise_mask.sum() / len(labels))
    cluster_count = len(unique_labels)
    min_cluster_size = 0

    if cluster_count:
        min_cluster_size = min(int((valid_labels == label).sum()) for label in unique_labels)

    valid = cluster_count >= 2 and non_noise_mask.sum() > cluster_count
    return valid, non_noise_mask, cluster_count, noise_ratio, min_cluster_size

def _evaluate_cluster_labels(algorithm: str, params: dict, X: np.ndarray, labels: np.ndarray) -> dict:
    valid, non_noise_mask, cluster_count, noise_ratio, min_cluster_size = _cluster_labels_are_valid(labels)
    row = {
        "algorithm": algorithm,
        "params": params,
        "cluster_count": cluster_count,
        "noise_ratio": noise_ratio,
        "min_cluster_size": min_cluster_size,
        "sample_count": int(len(labels)),
        "valid": valid,
        "silhouette_score": None,
        "davies_bouldin_index": None,
        "calinski_harabasz_score": None,
        "objective_score": float("-inf"),
    }

    if not valid:
        return row

    X_valid = X[non_noise_mask]
    labels_valid = labels[non_noise_mask]
    row["silhouette_score"] = float(silhouette_score(X_valid, labels_valid))
    row["davies_bouldin_index"] = float(davies_bouldin_score(X_valid, labels_valid))
    row["calinski_harabasz_score"] = float(calinski_harabasz_score(X_valid, labels_valid))
    row["objective_score"] = float(_score_clustering_result(row))
    return row

def _run_clustering_search(X_preprocessed_df: pd.DataFrame) -> tuple[pd.DataFrame, dict | None]:
    max_components = min(X_preprocessed_df.shape[1], 8)
    pca_component_options = sorted({2, 3, 5, max_components})
    results = []

    for component_count in pca_component_options:
        pca = PCA(n_components=component_count, random_state=42)
        X_reduced = pca.fit_transform(X_preprocessed_df)

        for n_clusters in range(2, 11):
            for n_init in (10, 25):
                params = {"pca_components": component_count, "n_clusters": n_clusters, "n_init": n_init}
                labels = KMeans(n_clusters=n_clusters, n_init=n_init, random_state=42).fit_predict(X_reduced)
                results.append(_evaluate_cluster_labels("KMeans", params, X_reduced, labels))

            for covariance_type in ("full", "tied", "diag"):
                params = {"pca_components": component_count, "n_components": n_clusters, "covariance_type": covariance_type}
                labels = GaussianMixture(
                    n_components=n_clusters,
                    covariance_type=covariance_type,
                    random_state=42,
                ).fit_predict(X_reduced)
                results.append(_evaluate_cluster_labels("GaussianMixture", params, X_reduced, labels))

            for linkage in ("ward", "complete", "average"):
                params = {"pca_components": component_count, "n_clusters": n_clusters, "linkage": linkage}
                labels = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage).fit_predict(X_reduced)
                results.append(_evaluate_cluster_labels("AgglomerativeClustering", params, X_reduced, labels))

        for eps in (0.25, 0.35, 0.50, 0.75, 1.00, 1.25, 1.50, 2.00):
            for min_samples in (5, 10, 20):
                params = {"pca_components": component_count, "eps": eps, "min_samples": min_samples}
                labels = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(X_reduced)
                results.append(_evaluate_cluster_labels("DBSCAN", params, X_reduced, labels))

        if hdbscan is not None:
            for min_cluster_size in (10, 20, 35, 50, 75, 100):
                for min_samples in (None, 5, 10, 20):
                    params = {
                        "pca_components": component_count,
                        "min_cluster_size": min_cluster_size,
                        "min_samples": min_samples,
                    }
                    labels = hdbscan.HDBSCAN(
                        min_cluster_size=min_cluster_size,
                        min_samples=min_samples,
                    ).fit_predict(X_reduced)
                    results.append(_evaluate_cluster_labels("HDBSCAN", params, X_reduced, labels))

    results_df = pd.DataFrame(results)
    valid_results = results_df[results_df["valid"]].copy()
    best_result = None

    if not valid_results.empty:
        valid_results.sort_values(
            by=["objective_score", "silhouette_score", "davies_bouldin_index", "calinski_harabasz_score"],
            ascending=[False, False, True, False],
            inplace=True,
        )
        best_result = valid_results.iloc[0].to_dict()

    return results_df, best_result

def _save_clustering_search_results(results_df: pd.DataFrame, best_result: dict | None):
    os.makedirs(EVALUATION_DIR, exist_ok=True)

    serializable_df = results_df.copy()
    serializable_df["params"] = serializable_df["params"].apply(json.dumps)
    serializable_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    serializable_df.to_csv(CLUSTERING_RESULTS_CSV, index=False)

    json_df = results_df.copy()
    json_df["params"] = json_df["params"].apply(lambda value: {key: _to_jsonable(val) for key, val in value.items()})
    json_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    payload = {
        "best_result": _to_jsonable(best_result),
        "results": _to_jsonable(json_df.where(pd.notna(json_df), None).to_dict(orient="records")),
    }
    with open(CLUSTERING_RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

def _to_jsonable(value):
    if isinstance(value, dict):
        return {key: _to_jsonable(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if pd.isna(value) if not isinstance(value, (dict, list, tuple, np.ndarray)) else False:
        return None
    return value

def _print_clustering_search_summary(results_df: pd.DataFrame, best_result: dict | None):
    print("\n[EVALUATION] Clustering algorithm comparison")
    print("-" * 100)

    valid_results = results_df[results_df["valid"]].copy()
    if valid_results.empty:
        print("No valid clustering configurations were found.")
        return

    valid_results.sort_values(
        by=["objective_score", "silhouette_score", "davies_bouldin_index", "calinski_harabasz_score"],
        ascending=[False, False, True, False],
        inplace=True,
    )

    display_columns = [
        "algorithm",
        "cluster_count",
        "noise_ratio",
        "silhouette_score",
        "davies_bouldin_index",
        "calinski_harabasz_score",
        "objective_score",
        "params",
    ]
    print(valid_results[display_columns].head(15).to_string(index=False))

    algorithm_summary = (
        valid_results
        .sort_values(by="objective_score", ascending=False)
        .groupby("algorithm", as_index=False)
        .first()[display_columns]
        .sort_values(by="objective_score", ascending=False)
    )

    print("\n[EVALUATION] Best configuration per algorithm")
    print("-" * 100)
    print(algorithm_summary.to_string(index=False))

    if best_result:
        print("\n[RECOMMENDATION] Best objective clustering configuration")
        print("-" * 100)
        print(f"Algorithm          : {best_result['algorithm']}")
        print(f"Parameters         : {best_result['params']}")
        print(f"Clusters           : {best_result['cluster_count']}")
        print(f"Noise ratio        : {best_result['noise_ratio']:.4f}")
        print(f"Silhouette score   : {best_result['silhouette_score']:.4f}")
        print(f"Davies-Bouldin     : {best_result['davies_bouldin_index']:.4f}")
        print(f"Calinski-Harabasz  : {best_result['calinski_harabasz_score']:.4f}")
        print(f"Objective score    : {best_result['objective_score']:.4f}")
        print("Selection rule     : maximize silhouette and objective score, reduce Davies-Bouldin, penalize heavy noise/tiny clusters.")
        print("Production note    : existing prediction artifacts still use the configured 4-cluster K-Means labels to preserve API/UI compatibility.")

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

    # 4. Compare clustering algorithms and hyperparameters without changing production artifacts.
    print("[TRAIN] Running clustering model selection search...")
    clustering_results_df, best_clustering_result = _run_clustering_search(X_preprocessed_df)
    _save_clustering_search_results(clustering_results_df, best_clustering_result)
    _print_clustering_search_summary(clustering_results_df, best_clustering_result)
    print(f"[SUCCESS] Saved clustering comparison JSON to: {CLUSTERING_RESULTS_JSON}")
    print(f"[SUCCESS] Saved clustering comparison CSV to: {CLUSTERING_RESULTS_CSV}")
    
    # 5. Generate configured production cluster labels using PCA and KMeans.
    print("[TRAIN] Generating production-compatible customer clusters via PCA & KMeans...")
    pca = PCA(n_components=PCA_COMPONENTS, random_state=42)
    X_pca = pca.fit_transform(X_preprocessed_df)
    
    kmeans = KMeans(n_clusters=KMEANS_CLUSTERS, random_state=42)
    cluster_labels = kmeans.fit_predict(X_pca)

    _print_clustering_metrics(X_pca, cluster_labels)
    
    # 6. Split data for classification evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X_preprocessed_df,
        cluster_labels,
        test_size=SPLIT_RATIO,
        random_state=42,
        stratify=cluster_labels,
    )
    print(f"[TRAIN] Dataset split: {len(X_train)} training rows, {len(X_test)} testing rows")

    # 7. Fit LogisticRegression classifier using GridSearchCV
    print("[TRAIN] Running GridSearch hyperparameter tuning for Logistic Regression...")
    lr = LogisticRegression()
    grid_search = GridSearchCV(
        estimator=lr,
        param_grid=GRID_SEARCH_PARAM_GRID,
        cv=3,
        verbose=1
    )
    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_
    print(f"[TRAIN] Best model cross-validation score: {grid_search.best_score_:.4f}")

    _print_classification_metrics(best_model, X_train, X_test, y_train, y_test)
    
    # Refit the selected model on all clustered records before saving for production inference.
    best_model.fit(X_preprocessed_df, cluster_labels)

    # 8. Save model and preprocessor to artifacts
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(PREPROCESSOR_PATH), exist_ok=True)
    
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(best_model, f)
    with open(PREPROCESSOR_PATH, "wb") as f:
        pickle.dump(preprocessor, f)
        
    # Copy/Save them to ml/ directory as backup
    os.makedirs("ml", exist_ok=True)
    with open(os.path.join("ml", "model.pkl"), "wb") as f:
        pickle.dump(best_model, f)
    with open(os.path.join("ml", "preprocessor.pkl"), "wb") as f:
        pickle.dump(preprocessor, f)
        
    print(f"[SUCCESS] Saved model to: {MODEL_PATH}")
    print(f"[SUCCESS] Saved preprocessor to: {PREPROCESSOR_PATH}")
    print("[TRAIN] Model training completed successfully!")
