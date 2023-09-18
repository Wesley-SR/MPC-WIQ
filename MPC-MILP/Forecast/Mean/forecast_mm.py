# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 09:34:53 2022

@author: wesle
"""

import pandas as pd


M = pd.read_csv('M_ensolarado.csv', index_col=['tempo'], sep=";")

M['PV_previsao'] = M['PV_real'].rolling(window=3,min_periods=1).mean()


M['PV_previsao'].plot()
M['PV_real'].plot()
