import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.utils import resample
from sklearn.model_selection import train_test_split

st.title("🌲 Random Forest Pedagógico con 10 Árboles")
st.markdown("""
Este demo muestra cómo **Random Forest reduce la varianza** al promediar múltiples árboles de decisión entrenados sobre distintos subconjuntos (bootstrap).
""")

# Cargar y reducir el dataset
housing = fetch_california_housing()
X_full, y_full = housing.data, housing.target

# Submuestreo
X, y = resample(X_full, y_full, n_samples=200, random_state=987654)
feature = 0  # elegimos solo una feature para simplificar visualmente

# Entrenar el bosque
n_estimators = 10
trees = []
predictions = []

X_train, X_test, y_train, y_test = train_test_split(X[:, [feature]], y, test_size=0.3, random_state=42)

# Entrenamos árboles independientes
for i in range(n_estimators):
    Xi, yi = resample(X_train, y_train, random_state=i)
    tree = RandomForestRegressor(n_estimators=1, max_depth=5, bootstrap=True, random_state=i)
    tree.fit(Xi, yi)
    trees.append(tree)
    predictions.append(tree.predict(X_test))

# Convertimos a array (n_trees x n_samples)
predictions = np.array(predictions)

# Promedio del bosque
ensemble_pred = predictions.mean(axis=0)


# Varianza individual por árbol
tree_variances_individual = [np.var(pred) for pred in predictions]

st.subheader("📊 Varianza por Árbol Individual")
for i, var in enumerate(tree_variances_individual):
    st.write(f"Árbol {i+1}: varianza = {var:.4f}")

# Gráfico de varianzas individuales
fig_var, ax_var = plt.subplots()
ax_var.bar(range(1, n_estimators + 1), tree_variances_individual, color='lightblue')
ax_var.axhline(np.var(ensemble_pred), color='black', linestyle='--', label='Varianza del Ensamble')
ax_var.set_xlabel("Árbol")
ax_var.set_ylabel("Varianza")
ax_var.set_title("Varianza por Árbol vs Ensamble")
ax_var.legend()
st.pyplot(fig_var)



# Visualización
st.subheader("📉 Predicciones de árboles individuales vs Ensamble")

fig, ax = plt.subplots(figsize=(10, 5))
x_axis = np.arange(len(X_test))

# Cada árbol individual
for i in range(n_estimators):
    ax.plot(x_axis, predictions[i], linestyle="--", alpha=0.5, label=f'Árbol {i+1}')

# Ensamble
ax.plot(x_axis, ensemble_pred, color='black', linewidth=2, label='🧠 Ensamble (Promedio)', zorder=10)

# Real
ax.plot(x_axis, y_test, color='green', linewidth=2, linestyle=':', label='🎯 Real')

ax.set_xlabel("Índice de muestra")
ax.set_ylabel("Valor Predicho")
ax.set_title("Predicciones de cada árbol y del ensamble")
ax.legend()
st.pyplot(fig)
