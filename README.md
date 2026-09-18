# Wine Quality Prediction

## Project Title

Wine Quality Prediction Using Machine Learning

## Problem Statement

This project predicts the quality score of red wine from physicochemical properties including acidity, sugar, chlorides, sulfur dioxide, density, pH, sulphates, and alcohol.

## Objective

Build and deploy a regression system that compares Decision Tree and Random Forest models and selects the better model using standard regression metrics.

## Dataset

The project uses the red wine portion of the UCI Machine Learning Repository Wine Quality Dataset.

Dataset source: https://archive.ics.uci.edu/dataset/186/wine+quality

Target variable: `quality`

Input features:

- fixed acidity
- volatile acidity
- citric acid
- residual sugar
- chlorides
- free sulfur dioxide
- total sulfur dioxide
- density
- pH
- sulphates
- alcohol

## Methodology

1. Load the semicolon-separated dataset.
2. Separate input features and the quality target.
3. Split the data into training and testing sets.
4. Impute missing values using the median and scale the features.
5. Train a Decision Tree Regressor and a Random Forest Regressor.
6. Compare MAE, MSE, RMSE, and R².
7. Save the better model and feature importance results.
8. Use the saved model in the Streamlit application.

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python train_model.py
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal.

## Repository Structure

```text
wine-quality-prediction/
├── app.py
├── train_model.py
├── requirements.txt
├── data/
│   └── winequality-red.csv
├── models/
│   ├── metadata.json
│   └── wine_quality_model.joblib
└── artifacts/
    ├── correlation_matrix.png
    ├── actual_vs_predicted.png
    ├── feature_importance.csv
    ├── metrics.json
    ├── quality_distribution.png
    └── test_predictions.csv
```

## Limitations

The model uses physicochemical measurements and historical quality scores. Wine quality scores are subjective, so the prediction should be treated as an educational estimate rather than an official assessment.
