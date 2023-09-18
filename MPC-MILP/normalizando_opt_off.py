# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 15:49:22 2022

@author: wesley
"""

import pandas as pd
import numpy as np
# from forecast_NNet import run_forecast
from forecast_mm import run_forecast_mm
from online_optimization import run_online_optimization
from offline_optimization import run_offline_optimization
from plot_online_charts import run_online_plot_charts
from plot_offline_charts import run_offline_plot_charts

off_out, off_out_to_chart, pesos = run_offline_optimization()

run_offline_plot_charts(off_out_to_chart, pesos)

