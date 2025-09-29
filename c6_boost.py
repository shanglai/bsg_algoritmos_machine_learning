# app_stepwise.py
import streamlit as st
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, plot_tree
from sklearn.ensemble import AdaBoostClassifier, AdaBoostRegressor, GradientBoostingClassifier, GradientBoostingRegressor
import xgboost as xgb
import matplotlib.pyplot as plt

st.title("🌳 Interfaz Interactiva - Boosting y Árboles Paso a Paso")

# -------------------------------
# Dataset de juguete
# -------------------------------
st.header("1. Dataset de Juguete")
n_total = st.slider("Tamaño para entrenar (se muestran 10)", 10, 200, 80, step=10)

rng = np.random.default_rng(42)
X_full = pd.DataFrame({
    "dosis_mg": rng.integers(10, 100, n_total),
    "edad": rng.integers(18, 70, n_total),
    "tiempo_tratamiento_dias": rng.integers(5, 30, n_total)
})
y_full = (np.sin(X_full["dosis_mg"]/10) + (X_full["edad"]/100) + rng.normal(0, 0.15, n_total) > 1).astype(int)

st.write("**Muestra (10 filas):**")
st.write(X_full.head(10))
st.write("**y (muestra):**", y_full[:10].tolist())

X_train, X_test, y_train, y_test = train_test_split(
    X_full, y_full, test_size=0.3, random_state=42, stratify=y_full
)

# -------------------------------
# Selección de modelo
# -------------------------------
st.header("2. Selección de Modelo")
problem_type = st.radio("Tipo de problema", ["Clasificación", "Regresión"])
model_name = st.selectbox("Modelo", ["AdaBoost", "Gradient Boosting", "XGBoost"])

# -------------------------------
# Parámetros
# -------------------------------
st.header("3. Parámetros del Modelo")
params = {}
if model_name == "AdaBoost":
    params["n_estimators"] = st.slider("Número de stumps", 5, 50, 10)
    params["learning_rate"] = st.slider("Learning rate", 0.01, 2.0, 1.0)

elif model_name == "Gradient Boosting":
    params["n_estimators"] = st.slider("Número de etapas", 5, 50, 10)
    params["learning_rate"] = st.slider("Learning rate", 0.01, 2.0, 0.1)
    params["max_depth"] = st.slider("Profundidad máxima", 1, 5, 2)

elif model_name == "XGBoost":
    params["n_estimators"] = st.slider("Número de árboles", 5, 50, 10)
    params["learning_rate"] = st.slider("Learning rate", 0.01, 2.0, 0.1)
    params["max_depth"] = st.slider("Profundidad máxima", 1, 5, 2)
    params["reg_lambda"] = st.slider("Lambda (L2)", 0.0, 5.0, 1.0)
    params["gamma"] = st.slider("Gamma (mínimo gain)", 0.0, 5.0, 0.0)

# -------------------------------
# Entrenamiento paso a paso
# -------------------------------
st.header("4. Entrenamiento Paso a Paso")

if st.button("Entrenar paso a paso"):

    # --- AdaBoost ---
    if model_name == "AdaBoost":
        st.subheader("AdaBoost - evolución de stumps")
        base = DecisionTreeClassifier(max_depth=1) if problem_type=="Clasificación" else DecisionTreeRegressor(max_depth=1)
        model = AdaBoostClassifier(estimator=base, **params) if problem_type=="Clasificación" else AdaBoostRegressor(estimator=base, **params)
        model.fit(X_train, y_train)

        staged_scores = []
        for i, y_pred in enumerate(model.staged_predict(X_test)):
            if problem_type=="Clasificación":
                score = accuracy_score(y_test, y_pred)
            else:
                score = mean_squared_error(y_test, y_pred)
            staged_scores.append(score)

            if i < 3:
                st.write(f"**Stump {i+1}**")
                fig, ax = plt.subplots(figsize=(6, 3))
                plot_tree(model.estimators_[i], filled=True, feature_names=X_full.columns, ax=ax)
                st.pyplot(fig)

        st.line_chart(staged_scores)

    # --- Gradient Boosting ---
    elif model_name == "Gradient Boosting":
        st.subheader("Gradient Boosting - evolución de etapas")
        model = GradientBoostingClassifier(**params) if problem_type=="Clasificación" else GradientBoostingRegressor(**params)
        model.fit(X_train, y_train)

        staged_scores = []
        for i, y_pred in enumerate(model.staged_predict(X_test)):
            if problem_type=="Clasificación":
                score = accuracy_score(y_test, y_pred)
            else:
                score = mean_squared_error(y_test, y_pred)
            staged_scores.append(score)

            if i < 3:
                st.write(f"**Árbol {i+1}**")
                fig, ax = plt.subplots(figsize=(6, 3))
                plot_tree(model.estimators_[i][0], filled=True, feature_names=X_full.columns, ax=ax)
                st.pyplot(fig)

        st.line_chart(staged_scores)

    # --- XGBoost ---
    elif model_name == "XGBoost":
        st.subheader("XGBoost - importancia, regularización y curvas")

        xgb_common = dict(
            n_estimators=params["n_estimators"],
            learning_rate=params["learning_rate"],
            max_depth=params["max_depth"],
            reg_lambda=params.get("reg_lambda", 0.0),
            gamma=params.get("gamma", 0.0),
            min_child_weight=0,
            subsample=1.0,
            colsample_bytree=1.0,
            tree_method="exact",
            random_state=42
        )

        if problem_type == "Clasificación":
            model = xgb.XGBClassifier(
                eval_metric="logloss",
                use_label_encoder=False,
                **xgb_common
            )
            metric = "logloss"
        else:
            model = xgb.XGBRegressor(
                eval_metric="rmse",
                **xgb_common
            )
            metric = "rmse"

        model.fit(
            X_train, y_train,
            eval_set=[(X_train, y_train), (X_test, y_test)],
            verbose=False
        )

        evals_result = model.evals_result()
        train_curve = evals_result['validation_0'][metric]
        test_curve  = evals_result['validation_1'][metric]

        st.write("**Importancia (gain)**")
        importance = model.get_booster().get_score(importance_type="gain")
        st.write(importance if importance else "(Sin splits: baja gamma/λ o usa más datos)")

        try:
            fig, ax = plt.subplots(figsize=(7, 4))
            xgb.plot_tree(model, num_trees=0, ax=ax)
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"No se pudo graficar el árbol con Graphviz: {e}")
            fig, ax = plt.subplots(figsize=(7, 4))
            xgb.plot_importance(model, importance_type="gain", ax=ax)
            st.pyplot(fig)

        st.write("**Curvas de entrenamiento (train vs test)**")
        curve_df = pd.DataFrame({
            f"train_{metric}": train_curve,
            f"test_{metric}": test_curve
        })
        st.line_chart(curve_df)

        st.info(
            "💡 Si ves una sola hoja o curvas planas: "
            "1) baja λ/gamma, 2) sube max_depth/n_estimators, 3) min_child_weight=0, "
            "4) aumenta el tamaño del dataset."
        )
