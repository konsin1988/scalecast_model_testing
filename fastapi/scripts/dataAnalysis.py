import pandas as pd
from pandas.plotting import autocorrelation_plot
from pandas.plotting import lag_plot
import numpy as np

from sqlalchemy import create_engine, text
import redis, json
from dotenv import load_dotenv
import os
from io import BytesIO, StringIO

import matplotlib.pyplot as plt

from scalecast.Forecaster import Forecaster
from scalecast import GridGenerator
from scalecast.util import plot_reduction_errors
from scalecast.SeriesTransformer import SeriesTransformer
from scalecast.auxmodels import auto_arima

from statsmodels.tsa.seasonal import seasonal_decompose

class DataAnalysis:
    def __init__(self):
        self.__set_engine_n_redis()
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
                "database": os.getenv("DB_NAME"),
                "redis_user": os.getenv("REDIS_USER"),
                "redis_password": os.getenv("REDIS_PASSWORD"),
                "redis_host": os.getenv("REDIS_HOST"),
                "redis_port": os.getenv("REDIS_PORT")
                }

    def __set_engine_n_redis(self):
        EV = self.__get_environ()
        self.__engine = create_engine(f"postgresql+psycopg2://{EV['user']}:{EV['password']}@{EV['host']}:{EV['port']}/{EV['database']}")
        self.__redis = redis.from_url(f"redis://{EV['redis_user']}:{EV['redis_password']}@{EV['redis_host']}:{EV['redis_port']}/0")

    def cache_df(func):
        def wrapper(self, t_name):
            res = self.__redis.get(t_name)
            if res is None: 
                res = func(self, t_name)
                csv_buffer = StringIO()
                res.to_csv(csv_buffer, index=False)
                self.__redis.set(t_name, csv_buffer.getvalue())
            else:
                res = pd.read_csv(StringIO(res.decode('utf-8')))
            return res
        return wrapper
    
    def cache_plot(func):
        def wrapper(self, t_name, plot_name):
            result = result = self.__redis.get(f'{t_name}-{plot_name}')
            if result is None:
                fig = func(self, t_name, plot_name)
                img_buf = BytesIO()
                plt.savefig(img_buf, format='png')
                plt.close(fig)
                self.__redis.set(f'{t_name}-{plot_name}', img_buf.getvalue())
                result = img_buf.getvalue()
            else:
                result = self.__redis.get(f'{t_name}-{plot_name}')
            return result
        return wrapper

    @cache_df
    def __get_data(self, t_name):
        query = text(f'select * from {t_name}')
        return pd.read_sql_query(query, self.__engine)

    def __get_forecaster(self, t_name, future_dates, test_length):
        data = (
            self.__get_data(t_name)
            .set_index('date')
        )
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
        df = self.__get_data(t_name).head()
        return dict(zip(df.columns, [df[x].to_list() for x in df.columns]))

    @cache_plot
    def get_main_plot(self, t_name, plot_name):
        fig, ax = plt.subplots(1, 1, figsize=(10, 5), dpi=120)
        self.__fs[t_name].plot()
        plt.title(f"{self.__dataset_dict[t_name]}", size=18)
        return fig
    
    @cache_plot
    def get_seasonal_decompose_plot(self, t_name, plot_name):
        fig, ax = plt.subplots(1, 1, figsize=(12, 6), dpi=120)
        plt.title(f"{self.__dataset_dict[t_name]}", size=18)
        self.__fs[t_name].seasonal_decompose().plot()
        return fig
        
#     def test(self):
#         return self.__fs

# analyser = DataAnalysis()
# print(analyser.test())