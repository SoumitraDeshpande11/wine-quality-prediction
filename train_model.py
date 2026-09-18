import json
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "winequality-red.csv"
MODEL_DIR = ROOT / "models"
ARTIFACT_DIR = ROOT / "artifacts"


def load_data():
    return pd.read_csv(DATA_PATH, sep=";")


def make_pipeline(model):
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", model),
        ]
    )


def calculate_metrics(actual, predicted):
    return {
        "MAE": round(float(mean_absolute_error(actual, predicted)), 6),
        "MSE": round(float(mean_squared_error(actual, predicted)), 6),
        "RMSE": round(float(np.sqrt(mean_squared_error(actual, predicted))), 6),
        "R2": round(float(r2_score(actual, predicted)), 6),
    }


def save_eda(data):
    quality_counts = data["quality"].value_counts().sort_index()
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.bar(quality_counts.index.astype(str), quality_counts.values, color="#7c3aed")
    axis.set_title("Wine Quality Distribution")
    axis.set_xlabel("Quality Score")
    axis.set_ylabel("Number of Wines")
    figure.tight_layout()
    figure.savefig(ARTIFACT_DIR / "quality_distribution.png", dpi=160)
    plt.close(figure)

    correlation = data.corr(numeric_only=True)
    figure, axis = plt.subplots(figsize=(10, 8))
    image = axis.imshow(correlation, cmap="coolwarm", vmin=-1, vmax=1)
    axis.set_xticks(range(len(correlation.columns)), correlation.columns, rotation=90)
    axis.set_yticks(range(len(correlation.columns)), correlation.columns)
    axis.set_title("Feature Correlation Matrix")
    figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    figure.tight_layout()
    figure.savefig(ARTIFACT_DIR / "correlation_matrix.png", dpi=160)
    plt.close(figure)


def main():
    MODEL_DIR.mkdir(exist_ok=True)
    ARTIFACT_DIR.mkdir(exist_ok=True)

    data = load_data()
    feature_names = [column for column in data.columns if column != "quality"]
    features = data[feature_names]
    target = data["quality"]

    train_features, test_features, train_target, test_target = train_test_split(
        features, target, test_size=0.2, random_state=42
    )

    model_definitions = {
        "Decision Tree Regressor": DecisionTreeRegressor(
            max_depth=5, min_samples_leaf=3, random_state=42
        ),
        "Random Forest Regressor": RandomForestRegressor(
            n_estimators=300, min_samples_leaf=2, random_state=42, n_jobs=-1
        ),
    }

    trained_models = {}
    comparison = {}
    for name, estimator in model_definitions.items():
        pipeline = make_pipeline(estimator)
        pipeline.fit(train_features, train_target)
        predictions = pipeline.predict(test_features)
        trained_models[name] = pipeline
        comparison[name] = calculate_metrics(test_target, predictions)

    best_name = min(comparison, key=lambda name: comparison[name]["RMSE"])
    best_model = trained_models[best_name]
    joblib.dump(best_model, MODEL_DIR / "wine_quality_model.joblib")

    feature_importance = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": best_model.named_steps["model"].feature_importances_,
        }
    ).sort_values("importance", ascending=False)
    feature_importance.to_csv(ARTIFACT_DIR / "feature_importance.csv", index=False)

    test_output = test_features.copy()
    test_output["actual_quality"] = test_target.to_numpy()
    test_output["predicted_quality"] = best_model.predict(test_features)
    test_output.to_csv(ARTIFACT_DIR / "test_predictions.csv", index=False, float_format="%.6f")

    figure, axis = plt.subplots(figsize=(7, 5))
    axis.scatter(test_output["actual_quality"], test_output["predicted_quality"], alpha=0.55, color="#7c3aed")
    axis.plot([test_target.min(), test_target.max()], [test_target.min(), test_target.max()], color="#b23a48", linewidth=2)
    axis.set_title("Actual vs Predicted Quality")
    axis.set_xlabel("Actual Quality")
    axis.set_ylabel("Predicted Quality")
    figure.tight_layout()
    figure.savefig(ARTIFACT_DIR / "actual_vs_predicted.png", dpi=160)
    plt.close(figure)

    bounds = {
        feature: {
            "min": float(features[feature].min()),
            "max": float(features[feature].max()),
            "median": float(features[feature].median()),
        }
        for feature in feature_names
    }
    metadata = {
        "target": "quality",
        "features": feature_names,
        "best_model": best_name,
        "dataset": "UCI Machine Learning Repository Wine Quality Dataset - Red Wine",
        "bounds": bounds,
    }
    (MODEL_DIR / "metadata.json").write_text(json.dumps(metadata, indent=2))
    (ARTIFACT_DIR / "metrics.json").write_text(
        json.dumps({"models": comparison, "best_model": best_name}, indent=2)
    )
    save_eda(data)

    print(json.dumps({"models": comparison, "best_model": best_name}, indent=2))


if __name__ == "__main__":
    main()
