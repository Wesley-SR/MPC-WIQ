# -*- coding: utf-8 -*-
"""
Created on Sat Oct 30 20:17:00 2023

@author: Wesley Rodrigues
"""


# import csv
import numpy as np
import pandas as pd
# from sklearn.preprocessing import MinMaxScaler
# from keras.models import model_from_json
# import matplotlib.pyplot as plt

def run_forecast_mm(P, Np):
   
    previous_data = []
    for k in range(0, Np):

        previous_data.append([0])
        previous_data[k] = P.loc[k,'PV_real']
        
    # P = P.to_numpy()
    # PREVISÃO PV:
    window_size = 3
    numbers_series_2 = pd.Series(previous_data)
    windows2 = numbers_series_2.rolling(window_size,min_periods=1)
    moving_averages_2 = windows2.mean()
    future_data = np.array(moving_averages_2)
    # print(type(future_data))
    
    
    ''' WRITE RESULTS IN SCV'''
    forecast = pd.DataFrame(future_data, columns = ['PV_previsao'])
    # p_rede_df.to_csv("online_forecast_pv.csv", index=False)
    
    return forecast