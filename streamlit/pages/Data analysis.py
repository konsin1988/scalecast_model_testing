import streamlit as st
import requests as rq

st.sidebar.page_link("https://konsin1988.dataresearch.ml/mlflow/", label="Mlflow")

st.title('Data analysis')

dataset = st.sidebar.radio(
    "Select dataset",
    ("CO2 amount", "Air passengers", "Bitcoin exchange rate", "Rented bike count")
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

st.subheader("Head of dataset")
res = rq.get(f'http://fastapi:8000/dfhead/{dataset_dict[dataset]}').json()
st.dataframe(res)

draw_plot("Plot the data", "main_plot")
draw_plot("Seasonality, trand and residuals", "seasonal_decompose")
draw_plot("Test for seasonality. Deseasonalized plot", "test_seasonality")
draw_plot("Boxplot of month distributions", "month_boxplots")
draw_plot("ACF and PACF plots", "acf_pacf")
draw_plot("Lag plots", "lag_plots")

st.subheader("Stationarity. Augmented Dickey Fuller test (ADF Test)")
res = rq.get(f'http://fastapi:8000/adf_test/{dataset_dict[dataset]}').json()['result']
st.text(res)

draw_plot("Detrend a time series", "detrended_plot")


