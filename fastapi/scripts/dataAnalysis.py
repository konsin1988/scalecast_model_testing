import pandas as pd
from pandas.plotting import autocorrelation_plot
from pandas.plotting import lag_plot
import numpy as np
import seaborn as sns

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
        self.__dataset_dict_title = {
            "co2": "CO2 amount", 
            "air_passengers": "Air passengers",
            "bitcoin": "Bitcoin exchange rate",
            "bike": "Rented bike count"
                }
        self.__column_dict = {
            "co2": "co2", 
            "air_passengers": "passengers",
            "bitcoin": "close",
            "bike": "count"
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
            result = self.__redis.get(f'{t_name}-{plot_name}')
            if result is None:
                fig = func(self, t_name, plot_name)
                img_buf = BytesIO()
                plt.savefig(img_buf, format='png')
                plt.close(fig)
                self.__redis.set(f'{t_name}-{plot_name}', img_buf.getvalue())
                result = img_buf.getvalue()
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
        plt.title(f"{self.__dataset_dict_title[t_name]}", size=18)
        return fig
    
    @cache_plot
    def get_seasonal_decompose_plot(self, t_name, plot_name):
        fig, ax = plt.subplots(1, 1, figsize=(12, 6), dpi=120)
        plt.title(f"{self.__dataset_dict_title[t_name]}", size=18)
        self.__fs[t_name].seasonal_decompose().plot()
        return fig
    
    @cache_plot
    def get_test_seasonality_plot(self, t_name, plot_name):
        column = self.__column_dict[t_name]
        data = self.__get_data(t_name).query(f'{column} > 0')
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 7))
        ax1.set_title("Test for seasonality", fontsize=16)
        autocorrelation_plot(data[column].tolist(), ax=ax1)

        additive_decomposition = seasonal_decompose(data[column], model="multiplicative", period=12)
        deseasonalized = data[column].values / additive_decomposition.seasonal

        ax2.plot(deseasonalized)
        ax2.set_title(f"{self.__dataset_dict_title[t_name]} Deseasonalized", fontsize=16)
        return fig
    
    @cache_plot
    def get_month_boxplots(self, t_name, plot_name):
        data_with_month_number = self.__get_data(t_name).reset_index().assign(month_name = lambda x: x['date'].astype("datetime64[ns]").dt.strftime("%b"))
        column = self.__column_dict[t_name]
        fig, ax = plt.subplots(1, 1, figsize=(10, 5))
        ax.set_xlabel("Months")
        ax.set_ylabel(self.__dataset_dict_title[t_name])
        ax.set_title(f"Boxplot of {self.__dataset_dict_title[t_name]}")
        sns.boxplot(data=data_with_month_number[["month_name", column]], x='month_name', y =f"{column}", ax=ax, hue='month_name')
        return fig

    @cache_plot
    def get_acf_pacf_plots(self, t_name, plot_name):
        f = self.__get_forecaster(t_name, 12, 0.2)
        fig, (ax1, ax2) = plt.subplots(2, 1,figsize=(9,9))
        f.plot_acf(ax=ax1, title='ACF', lags=40, color='black')
        f.plot_pacf(ax=ax2, title='PACF', lags=40, color='#B2C248', method='ywm')
        return fig

    @cache_plot
    def get_lag_plots(self, t_name, plot_name):
        column = self.__column_dict[t_name]
        plt.rcParams.update({'ytick.left' : False, 'axes.titlepad':10})
        fig, axes = plt.subplots(1, 4, figsize=(10,3), sharex=True, sharey=True, dpi=100)
        data = self.__get_data(t_name)[column]
        for i, ax in enumerate(axes.flatten()[:4]):
            lag_plot(data, lag=i+1, ax=ax, c='firebrick')
            ax.set_title('Lag ' + str(i+1))
        fig.suptitle(f'Lag Plots of {self.__dataset_dict_title[t_name]}', y=1.05) 
        return fig
    
    def get_adf_test(self, t_name):
        adf, pval, usedlag, nobs, crit_vals, icbest = self.__fs[t_name].adf_test(full_res=True)
        crit_val_string = ''
        for key, val in crit_vals.items():
            crit_val_string += f'\n\t\t- {key}:\t\t\t\t {val}'
        return {"result": f"""
- ADF test statistic:            \t\t\t\t{adf}
- ADF p-value:                   \t\t\t\t\t{pval}
- Number of lags used:           \t\t\t{usedlag}
- Number of observations:        \t\t\t{nobs}
- Critical values: {crit_val_string}
- Best information criterion:    \t\t\t{icbest}
        """}
    
    @cache_plot
    def get_detrended_plot(self, t_name, plot_name):
        detrended = (self.__get_data(t_name)[self.__column_dict[t_name]].values - self.__fs[t_name].seasonal_decompose().trend)
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        ax.plot(pd.DataFrame(detrended))
        ax.set_title(f'{self.__dataset_dict_title[t_name]} detrended by subtracting the trend component', fontsize=16)
        return fig
        
#     def test(self):
#         return self.__fs

# analyser = DataAnalysis()
# print(analyser.test())