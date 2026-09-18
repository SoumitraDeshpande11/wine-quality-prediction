import json
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "wine_quality_model.joblib"
METRICS_PATH = ROOT / "artifacts" / "metrics.json"
IMPORTANCE_PATH = ROOT / "artifacts" / "feature_importance.csv"
METADATA_PATH = ROOT / "models" / "metadata.json"
QUALITY_PLOT_PATH = ROOT / "artifacts" / "quality_distribution.png"
CORRELATION_PLOT_PATH = ROOT / "artifacts" / "correlation_matrix.png"
PREDICTIONS_PATH = ROOT / "artifacts" / "test_predictions.csv"

st.set_page_config(page_title="Wine Quality Predictor", page_icon="🍷", layout="wide")

st.markdown(
    """
    <style>
    .block-container {max-width: 1180px; padding-top: 2.2rem; padding-bottom: 3rem;}
    .hero {padding: 1.7rem 2rem; border-radius: 24px; background: linear-gradient(135deg, #301934 0%, #6d214f 52%, #b23a48 100%); color: white; margin-bottom: 1.5rem; box-shadow: 0 12px 32px rgba(48, 25, 52, 0.18);}
    .hero h1 {font-size: 2.65rem; margin: 0 0 0.4rem 0; letter-spacing: -0.04em;}
    .hero p {font-size: 1.03rem; margin: 0; color: #f8e9f0; max-width: 760px;}
    .eyebrow {font-size: 0.78rem; letter-spacing: 0.16em; text-transform: uppercase; font-weight: 700; color: #f7c9d6; margin-bottom: 0.5rem;}
    .result-card {padding: 1.35rem 1.5rem; border-radius: 18px; background: #fff7fa; border: 1px solid #f2d8e2; margin: 0.8rem 0 1rem 0;}
    .result-label {font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.12em; color: #8f5870; font-weight: 700;}
    .result-score {font-size: 3.2rem; line-height: 1.05; font-weight: 800; color: #5a1740; margin: 0.15rem 0;}
    .result-band {font-size: 1.05rem; color: #6d214f; font-weight: 600;}
    .info-card {padding: 1rem 1.1rem; border-radius: 15px; background: #faf8fc; border: 1px solid #ece6f1; min-height: 118px;}
    .section-note {color: #6b6470; margin-top: -0.35rem; margin-bottom: 1rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_json(path):
    return json.loads(path.read_text())


@st.cache_data
def load_importance():
    return pd.read_csv(IMPORTANCE_PATH)


@st.cache_data
def load_predictions():
    return pd.read_csv(PREDICTIONS_PATH)


def clamp(value, feature, bounds):
    return max(bounds[feature]["min"], min(bounds[feature]["max"], value))


def display_input(label, feature, bounds, value):
    return st.number_input(
        label,
        min_value=float(bounds[feature]["min"]),
        max_value=float(bounds[feature]["max"]),
        value=float(value),
        step=0.01,
        format="%.4f",
        help=f"Training range: {bounds[feature]['min']:.4f} to {bounds[feature]['max']:.4f}",
    )


def quality_band(score):
    if score < 5:
        return "Lower predicted range"
    if score < 7:
        return "Middle predicted range"
    return "Higher predicted range"


def show_info_card(label, value, detail):
    st.markdown(
        f'<div class="info-card"><strong>{label}</strong><br><span style="font-size:1.65rem;font-weight:800;color:#301934">{value}</span><br><span style="color:#6b6470">{detail}</span></div>',
        unsafe_allow_html=True,
    )


if not MODEL_PATH.exists() or not METADATA_PATH.exists():
    st.error("The trained model is missing. Run `python train_model.py` first.")
    st.stop()

model = load_model()
metadata = load_json(METADATA_PATH)

with st.sidebar:
    st.header("About this project")
    st.write("A machine learning model estimates the quality score of red wine from laboratory measurements.")
    st.divider()
    st.write("**Selected model**")
    st.write(metadata["best_model"])
    st.write("**Dataset**")
    st.write("UCI Red Wine Quality")
    st.link_button("View source code", "https://github.com/SoumitraDeshpande11/wine-quality-prediction")
    st.caption("Educational estimate only. Quality scores are subjective.")

st.markdown(
    '<div class="hero"><div class="eyebrow">Machine Learning Fundamentals</div><h1>Wine Quality Predictor</h1><p>Explore how physicochemical properties relate to wine quality and generate an instant model-based estimate.</p></div>',
    unsafe_allow_html=True,
)

predict_tab, insights_tab, guide_tab = st.tabs(["Predict quality", "Model insights", "Project guide"])

with predict_tab:
    st.subheader("Enter wine properties")
    st.markdown('<div class="section-note">Use a sample profile or adjust the measurements within the training-data range.</div>', unsafe_allow_html=True)
    bounds = metadata["bounds"]
    median_values = {feature: details["median"] for feature, details in bounds.items()}
    presets = {
        "Custom profile": median_values,
        "Typical red wine": median_values,
        "Higher alcohol profile": {
            **median_values,
            "alcohol": clamp(median_values["alcohol"] + 1.2, "alcohol", bounds),
            "volatile acidity": clamp(median_values["volatile acidity"] - 0.08, "volatile acidity", bounds),
        },
        "Higher acidity profile": {
            **median_values,
            "fixed acidity": clamp(median_values["fixed acidity"] + 1.0, "fixed acidity", bounds),
            "pH": clamp(median_values["pH"] - 0.12, "pH", bounds),
        },
    }

    preset = st.selectbox("Load an example profile", list(presets))
    selected_values = presets[preset]
    input_values = {}
    with st.form("wine_prediction_form"):
        input_columns = st.columns(3)
        for index, feature in enumerate(metadata["features"]):
            with input_columns[index % 3]:
                input_values[feature] = display_input(
                    feature.replace("_", " ").title(),
                    feature,
                    bounds,
                    selected_values[feature],
                )
        submitted = st.form_submit_button("Predict wine quality", type="primary", width="stretch")

    if submitted:
        input_frame = pd.DataFrame([input_values], columns=metadata["features"])
        if input_frame.isna().any().any():
            st.error("Please provide a value for every property.")
        else:
            prediction = float(model.predict(input_frame)[0])
            prediction = max(0.0, min(10.0, prediction))
            st.session_state["prediction"] = prediction

    if "prediction" in st.session_state:
        prediction = st.session_state["prediction"]
        st.markdown(
            f'<div class="result-card"><div class="result-label">Predicted quality score</div><div class="result-score">{prediction:.2f}<span style="font-size:1.25rem;color:#8f5870"> / 10</span></div><div class="result-band">{quality_band(prediction)}</div></div>',
            unsafe_allow_html=True,
        )
        st.progress(prediction / 10, text="Predicted score on a 0 to 10 scale")
        st.caption(f"Prediction generated by the {metadata['best_model']}.")

with insights_tab:
    metrics = load_json(METRICS_PATH)
    best_metrics = metrics["models"][metrics["best_model"]]
    st.subheader("Model performance")
    st.markdown('<div class="section-note">The final model was selected using the lowest test RMSE.</div>', unsafe_allow_html=True)
    metric_columns = st.columns(4)
    metric_columns[0].metric("Best model", metrics["best_model"].replace(" Regressor", ""))
    metric_columns[1].metric("MAE", f"{best_metrics['MAE']:.4f}")
    metric_columns[2].metric("RMSE", f"{best_metrics['RMSE']:.4f}")
    metric_columns[3].metric("R²", f"{best_metrics['R2']:.4f}")

    st.subheader("Model comparison")
    metric_frame = pd.DataFrame(metrics["models"]).T
    st.dataframe(metric_frame.style.format("{:.4f}"), width="stretch")

    importance_column, chart_column = st.columns([1, 1.35])
    with importance_column:
        st.subheader("Important features")
        importance = load_importance()
        st.dataframe(importance.style.format({"importance": "{:.4f}"}), width="stretch", hide_index=True)
    with chart_column:
        st.subheader("Feature importance")
        st.bar_chart(importance.set_index("feature")["importance"], horizontal=True)

    st.subheader("Dataset exploration")
    plot_columns = st.columns(2)
    with plot_columns[0]:
        st.image(QUALITY_PLOT_PATH, caption="Distribution of observed quality scores", width="stretch")
    with plot_columns[1]:
        st.image(CORRELATION_PLOT_PATH, caption="Correlation between input features and quality", width="stretch")

    with st.expander("View sample test predictions"):
        st.dataframe(load_predictions().head(10).style.format("{:.3f}"), width="stretch", hide_index=True)

with guide_tab:
    st.subheader("How the project works")
    guide_columns = st.columns(3)
    with guide_columns[0]:
        show_info_card("1. Input", "11 properties", "Laboratory measurements are entered by the user.")
    with guide_columns[1]:
        show_info_card("2. Model", "Random Forest", "The saved best-performing regression pipeline makes the estimate.")
    with guide_columns[2]:
        show_info_card("3. Output", "Quality score", "The predicted score is shown on a 0 to 10 scale.")

    st.subheader("Project scope")
    st.write("The project compares a Decision Tree Regressor and a Random Forest Regressor using the UCI red wine quality dataset. The training workflow includes median imputation, feature scaling, a held-out test split, standard regression metrics, and feature-importance analysis.")
    st.subheader("Limitations")
    st.write("The model learns from historical physicochemical measurements and subjective quality ratings. It provides an educational estimate and should not be treated as an official wine certification system.")
