import pandas as pd
import numpy as np
import seaborn as sns

import matplotlib.pyplot as plt
from scalecast.Forecaster import Forecaster

from scripts.mainDataLoader import mainDataLoader

class SKLearnModelsResearch(mainDataLoader):
    def __init__(self):
        super().__init__()

    @mainDataLoader.cache_df
    def lasso_test(self, t_name, p_name):
        fig, ax = plt.subplot(figsize=(12, 6))
        self._fs[t_name].set_estimator('lasso')
        lasso_grid = {'alpha':np.linspace(0,2,100)}
        self._fs[t_name].ingest_grid(lasso_grid)
        self._fs[t_name].cross_validate(k=3)
        self._fs[t_name].auto_forecast(call_me="lasso_cv")

        self._fs[t_name].plot_test_set(ci=True, models='lasso_cv')
        return fig