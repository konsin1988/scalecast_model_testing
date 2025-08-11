import pandas as pd
from pandas.plotting import autocorrelation_plot
from pandas.plotting import lag_plot
import numpy as np
import seaborn as sns

import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

from scripts.mainDataLoader import mainDataLoader

class DataAnalysis(mainDataLoader):
    def __init__(self):
        super().__init__()

    def get_dfhead(self, t_name):
        df = self._get_data(t_name).head()
        return dict(zip(df.columns, [df[x].to_list() for x in df.columns]))

    @mainDataLoader.cache_plot
    def get_main_plot(self, t_name, plot_name):
        fig, ax = plt.subplots(1, 1, figsize=(10, 5), dpi=120)
        self._fs[t_name].plot()
        plt.title(f"{self._dataset_dict_title[t_name]}", size=18)
        return fig
    
    @mainDataLoader.cache_plot
    def get_seasonal_decompose_plot(self, t_name, plot_name):
        fig, ax = plt.subplots(1, 1, figsize=(12, 6), dpi=120)
        plt.title(f"{self._dataset_dict_title[t_name]}", size=18)
        self._fs[t_name].seasonal_decompose().plot()
        return fig
    
    @mainDataLoader.cache_plot
    def get_test_seasonality_plot(self, t_name, plot_name):
        column = self._column_dict[t_name]
        data = self._get_data(t_name).query(f'{column} > 0')
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 7))
        ax1.set_title("Test for seasonality", fontsize=16)
        autocorrelation_plot(data[column].tolist(), ax=ax1)

        additive_decomposition = seasonal_decompose(data[column], model="multiplicative", period=12)
        deseasonalized = data[column].values / additive_decomposition.seasonal

        ax2.plot(deseasonalized)
        ax2.set_title(f"{self._dataset_dict_title[t_name]} Deseasonalized", fontsize=16)
        return fig
    
    @mainDataLoader.cache_plot
    def get_month_boxplots(self, t_name, plot_name):
        data_with_month_number = self._get_data(t_name).reset_index().assign(month_name = lambda x: x['date'].astype("datetime64[ns]").dt.strftime("%b"))
        column = self._column_dict[t_name]
        fig, ax = plt.subplots(1, 1, figsize=(10, 5))
        ax.set_xlabel("Months")
        ax.set_ylabel(self._dataset_dict_title[t_name])
        ax.set_title(f"Boxplot of {self._dataset_dict_title[t_name]}")
        sns.boxplot(data=data_with_month_number[["month_name", column]], x='month_name', y =f"{column}", ax=ax, hue='month_name')
        return fig

    @mainDataLoader.cache_plot
    def get_acf_pacf_plots(self, t_name, plot_name):
        f = self._fs[t_name]
        fig, (ax1, ax2) = plt.subplots(2, 1,figsize=(9,9))
        f.plot_acf(ax=ax1, title='ACF', lags=40, color='black')
        f.plot_pacf(ax=ax2, title='PACF', lags=40, color='#B2C248', method='ywm')
        return fig

    @mainDataLoader.cache_plot
    def get_lag_plots(self, t_name, plot_name):
        column = self._column_dict[t_name]
        plt.rcParams.update({'ytick.left' : False, 'axes.titlepad':10})
        fig, axes = plt.subplots(1, 4, figsize=(10,3), sharex=True, sharey=True, dpi=100)
        data = self._get_data(t_name)[column]
        for i, ax in enumerate(axes.flatten()[:4]):
            lag_plot(data, lag=i+1, ax=ax, c='firebrick')
            ax.set_title('Lag ' + str(i+1))
        fig.suptitle(f'Lag Plots of {self._dataset_dict_title[t_name]}', y=1.05) 
        return fig
    
    def get_adf_test(self, t_name):
        adf, pval, usedlag, nobs, crit_vals, icbest = self._fs[t_name].adf_test(full_res=True)
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
    
    @mainDataLoader.cache_plot
    def get_detrended_plot(self, t_name, plot_name):
        detrended = (self._get_data(t_name)[self._column_dict[t_name]].values - self._fs[t_name].seasonal_decompose().trend)
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        ax.plot(pd.DataFrame(detrended))
        ax.set_title(f'{self._dataset_dict_title[t_name]} detrended by subtracting the trend component', fontsize=16)
        return fig
        