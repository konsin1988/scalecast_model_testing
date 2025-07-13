import pandas as pd
from pandas.plotting import autocorrelation_plot
from pandas.plotting import lag_plot
import numpy as np

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from io import BytesIO

import matplotlib.pyplot as plt

from scalecast.Forecaster import Forecaster
from scalecast import GridGenerator
from scalecast.util import plot_reduction_errors
from scalecast.SeriesTransformer import SeriesTransformer
from scalecast.auxmodels import auto_arima

from statsmodels.tsa.seasonal import seasonal_decompose

class DataAnalysis:
    def __init__(self):
        self.__set_engine()
        self.__set_data()
        self.__set_forecasters()
        self.__dataset_dict = {"co2": "CO2 amount", 
                "air_passengers": "Air passengers",
                "bitcoin": "Bitcoin exchange rate",
                "bike": "Rented bike count"
                }

    def __get_environ(self):
        load_dotenv()
        return {"user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "host": os.getenv("DB_HOST"),
                "port": os.getenv("DB_PORT"),
                "database": os.getenv("DB_NAME")}

    def __set_engine(self):
        EV = self.__get_environ()
        self.__engine = create_engine(f"postgresql+psycopg2://{EV['user']}:{EV['password']}@{EV['host']}:{EV['port']}/{EV['database']}")

    def __get_list_tables(self):
        query = text("select tablename from pg_catalog.pg_tables where schemaname='public';")
        return pd.read_sql_query(query, self.__engine)['tablename'].to_list()

    def __set_data(self):
        tables = []
        table_list = self.__get_list_tables()
        for t_name in table_list:
            query = text(f'select * from {t_name}')
            tables.append(pd.read_sql_query(query, self.__engine))
        self.__data = dict(zip(table_list, tables))

    def __get_forecaster(self, t_name, future_dates, test_length):
        data = self.__data[t_name].set_index('date')
        return Forecaster(
            y = data.iloc[:,0],
            current_dates=data.index,
            future_dates=future_dates,
            test_length=test_length,
            # metrics = ['rmse','mae','mape','r2'],
            cis=True
        )
    
    def __set_forecasters(self):
        self.__fs = {
            "co2": self.__get_forecaster('co2', 12, 24),
            "air_passengers": self.__get_forecaster("air_passengers", 12, 0.2),
            "bitcoin": self.__get_forecaster("bitcoin", 12, 0.2),
            "bike": self.__get_forecaster("bike", 12, 0.2)
        }

    def get_dfhead(self, t_name):
        df = self.__data[t_name].head()
        return dict(zip(df.columns, [df[x].to_list() for x in df.columns]))
    
    def get_main_plot(self, t_name):
        fig, ax = plt.subplots(1, 1, figsize=(10, 5), dpi=120)
        self.__fs[t_name].plot()
        plt.title(f"{self.__dataset_dict[t_name]}", size=18)

        img_buf = BytesIO()
        plt.savefig(img_buf, format='png')
        plt.close(fig) 
        img_buf.seek(0)
        return img_buf  
    
    def get_seasonal_decompose_plot(self, t_name):
        fig = plt.figure(figsize=(12, 6), dpi=120)
        plt.title(f"{self.__dataset_dict[t_name]}", size=18)
        self.__fs[t_name].seasonal_decompose().plot()

        img_buf = BytesIO()
        plt.savefig(img_buf, format='png')
        plt.close(fig) 
        img_buf.seek(0)
        return img_buf  
        
#     def test(self):
#         return self.__fs

# analyser = DataAnalysis()
# print(analyser.test())