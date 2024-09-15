# import csv
import pandas as pd
# from sklearn.preprocessing import MinMaxScaler
# from keras.models import model_from_json
import matplotlib.pyplot as plt


def mmpw(P, Np):
    F = pd.DataFrame({'F' : [0.0]*Np})
    
    k = 0
    w1, w2, w3, w4, w5, w6 = 10, 2, 2, 1, 1, 1
    F.loc[k, 'F'] = (P.iloc[Np-1, 0]*w1 + P.iloc[Np-2, 0]*w2 + P.iloc[Np-3, 0]*w3 +
                     P.iloc[0   , 0]*w4 + P.iloc[1, 0]*w5 + P.iloc[2, 0]*w6)/(w1+w2+w3+w4+w5+w6)
    
    k = 1
    w1, w2, w3, w4, w5, w6 = 10, 2, 2, 1, 1, 1
    F.loc[k, 'F'] = (F.iloc[k-1, 0]*w1 + P.iloc[Np-1, 0]*w2 + P.iloc[Np-2, 0]*w3 +
                     P.iloc[0   , 0]*w4 + P.iloc[1, 0]*w5 + P.iloc[2, 0]*w6)/(w1+w2+w3+w4+w5+w6)    
    
    k = 2
    w1, w2, w3, w4, w5, w6 = 5, 5, 2, 1, 1, 1
    F.loc[k, 'F'] = (F.iloc[k-1, 0]*w1 + F.iloc[k-2, 0]*w2 + 
                     P.iloc[1  , 0]*w3 + P.iloc[2  , 0]*w4 + P.iloc[3, 0]*w5 + P.iloc[4, 0]*w6)/(w1+w2+w3+w4+w5+w6)    
    
    k = 3 
    w1, w2, w3, w4, w5, w6 = 3, 2, 1, 1, 1, 1
    F.loc[k, 'F'] = (F.iloc[k-1, 0]*w1 + F.iloc[k-2, 0]*w2 + F.iloc[k-3, 0]*w3 +
                     P.iloc[2  , 0]*w4 + P.iloc[3, 0]*w5 + P.iloc[4, 0]*w6)/(w1+w2+w3+w4+w5+w6)    

    k = 4 
    w1, w2, w3, w4, w5, w6 = 3, 2, 1, 1, 1, 1
    F.loc[k, 'F'] = (F.iloc[k-1, 0]*w1 + F.iloc[k-2, 0]*w2 + F.iloc[k-3, 0]*w3 +
                     P.iloc[3  , 0]*w4 + P.iloc[4, 0]*w5 + P.iloc[5, 0]*w6)/(w1+w2+w3+w4+w5+w6)    

    k = 5
    w1, w2, w3, w4, w5, w6 = 3, 2, 1, 1, 1, 1
    F.loc[k, 'F'] = (F.iloc[k-1, 0]*w1 + F.iloc[k-2, 0]*w2 + 
                     P.iloc[4  , 0]*w3 + P.iloc[5  , 0]*w4 + P.iloc[6, 0]*w5 + P.iloc[7, 0]*w6)/(w1+w2+w3+w4+w5+w6)
    
    k = 6
    w1, w2, w3, w4, w5, w6 = 3, 1, 1, 1, 1, 1
    F.loc[k, 'F'] = (F.iloc[k-1, 0]*w1 +
                     P.iloc[4  , 0]*w2 + P.iloc[5  , 0]*w3 + P.iloc[6, 0]*w4 + P.iloc[7, 0]*w5 + P.iloc[7, 0]*w6)/(w1+w2+w3+w4+w5+w6)
    
    w1, w2, w3, w4, w5, w6 = 3, 1, 1, 1, 1, 1
    for k in range(7, Np-1):
        F.loc[k, 'F'] = (F.iloc[k-1, 0]*w1 +
                     P.iloc[k-2  , 0]*w2 + P.iloc[k-1  , 0]*w3 + P.iloc[k, 0]*w4 + P.iloc[k+1, 0]*w5 + P.iloc[k+1, 0]*w6)/(w1+w2+w3+w4+w5+w6)
    


    return F

if __name__ == "__main__":
    # Carregar os dados
    wights = pd.DataFrame({'wights': [3, 2]})
    datas = pd.read_csv("Dados_PV_15_min_1ano.csv")

    # Definir o intervalo de amostras
    Np = 96
    beginning = 0
    past = datas.iloc[beginning:beginning+Np]
    
    real_future = datas.iloc[beginning+Np:beginning+Np+Np]
    
    # Teste de posição
    # value2 = past.loc[Np-1, 'p_pv']
    
    
    
    forecast = mmpw(past, Np)
    
    
    
    
    
    # Configurar os passos de tempo e plotar
    time_steps = list(range(Np))
    plt.figure(figsize=(12, 6))

    # Plotar os dados
    plt.plot(time_steps, past['p_pv'].values, marker='o', linestyle='-', label='Past')
    plt.plot(time_steps, forecast['F'].values, marker='o', linestyle='-', label='Predict')
    plt.plot(time_steps, real_future['p_pv'].values, marker='o', linestyle='-', label='Real future')

    # Configurar rótulos e título
    plt.xlabel('Amostra')
    plt.ylabel('Power (kW)')
    plt.title('Dados de Potência ao Longo do Tempo')
    plt.legend()
    plt.grid(True)

    # Ajustar as marcas do eixo X para mostrar todas as amostras
    plt.xticks(ticks=time_steps, rotation=90)  # Ajuste a rotação conforme necessário
    
    # Mostrar o gráfico
    plt.tight_layout()  # Para ajustar a disposição dos elementos e evitar sobreposições
    plt.show()