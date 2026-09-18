# Wine Quality Prediction Using Machine Learning

**Team:** BDA  
**Members:** Soumitra Deshpande, Prathamesh Swami, Pranav Kale, R Virshin, Raj Koli

## Abstract

This project develops a machine learning system that predicts a red wine quality score from physicochemical measurements. Decision Tree and Random Forest regression models are trained, evaluated, compared, and deployed through Streamlit.

## Introduction

Wine quality is influenced by measurable chemical properties. A predictive model can learn relationships between these properties and historical quality scores and provide an educational estimate for a new wine sample.

## Problem Statement

Predict the quality score of red wine using acidity, sugar, chlorides, sulfur dioxide, density, pH, sulphates, and alcohol measurements.

## Objectives

- Understand the wine quality dataset.
- Clean and preprocess the data.
- Explore feature relationships and quality distribution.
- Train and compare two regression models.
- Identify important input features.
- Deploy the selected model with Streamlit.

## Dataset Description

The dataset is the red wine portion of the UCI Machine Learning Repository Wine Quality Dataset. It contains 11 physicochemical input features and a numerical `quality` target.

## Preprocessing

The data is read from a semicolon-separated CSV file. The quality column is separated from the input features. The data is split into training and testing sets using an 80:20 split with a fixed random seed. The training pipeline imputes missing values with feature medians and standardizes the numeric inputs.

## Exploratory Data Analysis

The project generates a quality distribution plot and a feature correlation matrix. These outputs are stored in the `artifacts` directory and support analysis of the target distribution and relationships between chemical properties.

## Model Development

The project trains a Decision Tree Regressor and a Random Forest Regressor. Both models use the same preprocessing pipeline. The model with the lower test RMSE is selected for deployment.

## Evaluation

The models are evaluated using Mean Absolute Error, Mean Squared Error, Root Mean Squared Error, and R². The complete comparison is stored in `artifacts/metrics.json`.

| Model | MAE | MSE | RMSE | R² |
|---|---:|---:|---:|---:|
| Decision Tree Regressor | 0.5069 | 0.4359 | 0.6602 | 0.3330 |
| Random Forest Regressor | 0.4297 | 0.3113 | 0.5580 | 0.5236 |

## Results

The current run selected the Random Forest Regressor because it achieved the lower test RMSE. Alcohol, sulphates, volatile acidity, and total sulfur dioxide were the most important features in the selected model. The complete feature ranking is stored in `artifacts/feature_importance.csv`.

## Streamlit Deployment

The Streamlit application accepts the 11 physicochemical measurements, loads the saved model, and displays the predicted quality score. It also displays the model comparison table and feature importance chart.

## Limitations

Quality scores are subjective and reflect historical ratings. The application provides an educational estimate and should not be treated as an official wine certification system.

## Conclusion

The project demonstrates the complete machine learning workflow from dataset preparation and exploratory analysis to model comparison, model persistence, and Streamlit deployment.

## References

- UCI Machine Learning Repository, Wine Quality Dataset: https://archive.ics.uci.edu/dataset/186/wine+quality
- Scikit-learn documentation: https://scikit-learn.org/stable/
- Streamlit documentation: https://docs.streamlit.io/
