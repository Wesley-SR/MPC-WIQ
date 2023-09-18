import csv
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import model_from_json
import matplotlib.pyplot as plt


def run_forecast_NNet(U_2):
    
    previous_data = []
    for p in range(0, 96):
        previous_data.append([0])
        previous_data[p] = U_2.loc[p,'PV_real']
    
    previous_data = np.array([previous_data]).T
    
    #========================================================================================================================#
    # CARREGAR MODELO DE PREVISÃO E NORMALIZAR OS DADOS DE ENTRADA:
    arquivo_2 = open('Forecast/PV_model_with_NN/previsao_PV_15_min.json', 'r')
    estrutura_rede_PV = arquivo_2.read()
    arquivo_2.close()
    classificador_PV = model_from_json(estrutura_rede_PV)
    classificador_PV.load_weights('Forecast/PV_model_with_NN/LSTM_PV_96.h5')
    
    n_steps_in = 96
    n_features = 1
    
    # FAZER PREVISÃO DO PRIMEIRO DIA:
    
    # Normalizar os dados de entrada:
    scaler = MinMaxScaler(feature_range=(0, 1))
    normalized_previous_data = scaler.fit_transform(previous_data)
    
    # DEIXAR NA FORMA: (1,144,1)
    formatted_previous_data = normalized_previous_data.reshape((1, n_steps_in, n_features))
    
    # FAZER A PREVISÃO:
    future_data = classificador_PV.predict(formatted_previous_data, verbose=0)
    
    # DEIXAR A PREVISÃO EM kW:
    future_data = scaler.inverse_transform(future_data).T
    
    #========================================================================================================================#
    # # Comparar previsão com os dados reais:
    # # Dados reais do PV do dia 14:
    # dia_26_PV = []
    # for p in range(0, 96):
    #     dia_26_PV.append([0])
        
    # for l in range(96,192):
    #     dia_26_PV[l-96] = U_2.loc[l,'potencia_PV']
    
    # dia_26_PV = np.array([float(i) for i in dia_26_PV]).T
    
    # # plt.plot(dia_26_PV)
    # # plt.plot(future_data)
    # # plt.xlabel('Instante de tempo')
    # # plt.ylabel('Potência [kW]')
    
    
    
    ''' WRITE RESULTS IN SCV '''
    p_rede_df = pd.DataFrame(future_data, columns = ['PV_previsao'])

        
    p_rede_df.to_csv("online_forecast_pv.csv", index=False)
    
    return p_rede_df