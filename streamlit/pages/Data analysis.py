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



# st.subheader("Plot the data")
# res = rq.get(f'http://fastapi:8000/main_plot/{dataset_dict[dataset]}')
# st.image(res.content)

# st.header("Seasonality, trand and residuals")
# res = rq.get(f'http://fastapi:8000/seasonal_decompose/{dataset_dict[dataset]}')
# st.image(res.content)

# st.header("Test for seasonality. Deseasonalized plot")
# res = rq.get(f'http://fastapi:8000/get_test_seasonality_plot/{dataset_dict[dataset]}')
# st.image(res.content)

# st.header("Boxplot of month distributions")
# res = rq.get(f'http://fastapi:8000/get_month_boxplots/{dataset_dict[dataset]}')
# st.image(res.content)


