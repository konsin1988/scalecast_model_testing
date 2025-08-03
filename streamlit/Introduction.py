import streamlit as st
import pandas as pd
import requests as rq 


st.sidebar.page_link("https://konsin1988.dataresearch.ml/mlflow/", label="Mlflow")

st.title("Scalecast focasting in different data")
st.header("Data overview")

dataset_info = {
    "subheader": {
        "co2": "CO2 amount",
        "air_passengers": "Air passengers",
        "bitcoin": "Bitcoin exchange rate",
        "bike": "Rented bike count",
    },
    "text": {
        "co2": "This dataset provides observations of atmospheric carbon dioxide (CO2) amounts obtained from observations collected by several current and historical satellite instruments. Carbon dioxide is a naturally occurring Greenhouse Gas (GHG), but one whose abundance has been increased substantially above its pre-industrial value of some 280 ppm by human activities, primarily because of emissions from combustion of fossil fuels, deforestation and other land-use change. The annual cycle (especially in the northern hemisphere) is primarily due to seasonal uptake and release of atmospheric CO2 by terrestrial vegetation.",
        "air_passengers": "This dataset provides monthly totals of a US airline passengers from 1949 to 1960. This dataset is taken from an inbuilt dataset of R called AirPassengers.",
        "bitcoin": "Bitcoin, the pioneering cryptocurrency, has captured the world's attention as a decentralized digital asset with a fluctuating market value. This dataset offers a comprehensive record of Bitcoin's price evolution, spanning from August 2017 to July 2023. The data has been meticulously collected from the Binance API, with price data captured at one-minute intervals. Each record includes essential information such as the open, high, low, and close prices, alongside associated trading volume. This dataset provides an invaluable resource for those interested in studying Bitcoin's price trends and market dynamics.",
        "bike": "The 'Bike Sharing Demand' dataset typically describes the hourly or daily count of rented bikes in a bike-sharing system, along with associated weather and seasonal information. It's often used to analyze and predict bike rental demand based on various factors. The data is valuable for understanding urban mobility patterns and can be used for tasks like predicting bike rentals or detecting significant events" },
    "link_name": {
        "co2": "https://cds.climate.copernicus.eu",
        "air_passengers": "www.kaggle.com",
        "bitcoin": "www.kaggle.com",
        "bike": "www.kaggle.com"
    },
    "link_content": {
        "co2": "https://cds.climate.copernicus.eu/datasets/satellite-carbon-dioxide?tab=overview",
        "air_passengers": "https://www.kaggle.com/datasets/chirag19/air-passengers",
        "bitcoin": "https://www.kaggle.com/datasets/jkraak/bitcoin-price-dataset",
        "bike": "https://www.kaggle.com/datasets/marklvl/bike-sharing-dataset"
    }
}

def show_info(t_name):
    st.subheader(dataset_info['subheader'][t_name])
    st.text(dataset_info['text'][t_name])
    res = rq.get(f'http://fastapi:8000/plot/main_plot/{t_name}')
    st.image(res.content)
    l, link = st.columns([0.6, 0.4])
    link.link_button(dataset_info['link_name'][t_name], dataset_info['link_content'][t_name])

for t_name in ('co2', 'air_passengers', 'bitcoin', 'bike'):
    show_info(t_name)
