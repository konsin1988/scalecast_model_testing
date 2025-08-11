import streamlit as st
import requests as rq


st.sidebar.page_link("https://konsin1988.dataresearch.ml/mlflow/", label="Mlflow")

st.title("Linear Scikit-Learn Models")

dataset = st.sidebar.radio(
    "Select dataset",
    ("CO2 amount", "Air passengers", "Bitcoin exchange rate", "Rented bike count")
)

model = st.sidebar.radio(
    "Select regression model",
    ("mlr", "lasso", "ridge", "elasticnet", "sgd", "all")
)

dataset_dict = {"CO2 amount": "co2", 
                "Air passengers": "air_passengers",
                "Bitcoin exchange rate": "bitcoin",
                "Rented bike count": "bike"
                }

def draw_plot(plot_name, plot_func):
    st.subheader(plot_name)
    res = rq.get(f'http://fastapi:8000/plot/{plot_func}/{dataset_dict[dataset]}')
    st.image(res.content)

draw_plot("Lasso test", "lasso_test")