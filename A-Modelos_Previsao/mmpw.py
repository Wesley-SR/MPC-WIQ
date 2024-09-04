# import csv
import numpy as np
import pandas as pd
# from sklearn.preprocessing import MinMaxScaler
# from keras.models import model_from_json
import matplotlib.pyplot as plt


def mmpw(past, Np):
    pass
    


if __name__ == "__main__":
    datas = pd.read_csv("Dados_PV_15_min_1ano.csv")
    Np = 96
    past = datas.iloc[0:Np]
    
    time_steps = list(range(Np))
    plt.figure(figsize=(10, 5))
    plt.plot(past['p_pv'], marker='o', linestyle='-', color='b', label='Past')
    # plt.xlabel('Time (h)')
    # plt.ylabel('Power (kW)')
    # plt.title('pv power')
    # plt.legend()
    # plt.grid()
    plt.show()