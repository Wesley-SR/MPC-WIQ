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
import matplotlib.pyplot as plt

def run_forecast_mm(P, Np):
   
    previous_data = []
    for k in range(0, Np):

        previous_data.append([0])
        previous_data[k] = P.loc[k,'potencia_PV']
        
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


if __name__ == "__main__":
    path = "C:\\Dados\\Wesley\\Mestrado\\Desenvolvimento\\Codigos\\MPC-WIQ\\A-Modelos_Previsao"
    file = "\\Dados_PV_15_min_1ano.csv"
    path_and_file = "{}{}".format(path, file)
    original_series = pd.read_csv(path_and_file)
    Np = 96
    teste_dif_period = 42
    
    to_test_1 = original_series.head(Np)
    to_test_2 = original_series.iloc[teste_dif_period:teste_dif_period+96].reset_index(drop=True)
    
    forecasted_1 = run_forecast_mm(to_test_1, Np)
    forecasted_2 = run_forecast_mm(to_test_2, Np)
    
    # Dados reais futuros
    real_obscuro_1 = original_series.iloc[96:2*Np].reset_index(drop=True)
    real_obscuro_2 = original_series.iloc[teste_dif_period+Np:teste_dif_period+2*Np].reset_index(drop=True)
    
    # Plotting to_test_1 and forecasted_1
    plt.figure(figsize=(10, 5))
    plt.subplot(2, 1, 1)  # Subplot for to_test_1 and forecasted_1
    plt.plot(to_test_1['potencia_PV'], label='Dados de entrada 1')
    plt.plot(forecasted_1['PV_previsao'], label='Previsão 1')
    plt.plot(real_obscuro_1['potencia_PV'], label='Obscuro 1')

    # Adding labels and title for subplot 1
    plt.xlabel('Time')
    plt.ylabel('Power')
    plt.title('Actual vs Forecasted Data - Set 1')
    plt.legend()

    # Plotting to_test_2 and forecasted_2
    plt.subplot(2, 1, 2)  # Subplot for to_test_2 and forecasted_2
    plt.plot(to_test_2['potencia_PV'], label='Dados de entrada 2')
    plt.plot(forecasted_2['PV_previsao'], label='Previsão 2')
    plt.plot(real_obscuro_2['potencia_PV'], label='Obscuro 2')

    # Adding labels and title for subplot 2
    plt.xlabel('Time')
    plt.ylabel('Power')
    plt.title('Actual vs Forecasted Data - Set 2')
    plt.legend()

    # Adjust layout to prevent clipping
    plt.tight_layout()

    # Show the plot
    plt.show()
    
    
    
    