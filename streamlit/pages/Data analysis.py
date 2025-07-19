import streamlit as st
import requests as rq

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

st.subheader("Head of dataset")
res = rq.get(f'http://fastapi:8000/dfhead/{dataset_dict[dataset]}').json()
st.dataframe(res)

st.subheader("Plot the data")
res = rq.get(f'http://fastapi:8000/main_plot/{dataset_dict[dataset]}')
st.image(res.content)

st.header("Seasonality, trand and residuals")
res = rq.get(f'http://fastapi:8000/seasonal_decompose/{dataset_dict[dataset]}')
st.image(res.content)
