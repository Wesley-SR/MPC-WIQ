# import csv
import pandas as pd
# from sklearn.preprocessing import MinMaxScaler
# from keras.models import model_from_json
import matplotlib.pyplot as plt

# import os
# # Crie uma pasta para armazenar as imagens, se ainda não existir
# output_dir = 'imagens_previsao'
# os.makedirs(output_dir, exist_ok=True)


def mmpw(P, Np):
    F = pd.DataFrame({'data' : [0.0]*(Np-1)})
    
    k = 0
    w1, w2, w3, w4, w5, w6 = 10, 2, 2, 1, 1, 1
    F.loc[k, 'data'] = (P.iloc[Np-1, 0]*w1 + P.iloc[Np-2, 0]*w2 + P.iloc[Np-3, 0]*w3 +
                     P.iloc[0   , 0]*w4 + P.iloc[1, 0]*w5 + P.iloc[2, 0]*w6)/(w1+w2+w3+w4+w5+w6)
    
    k = 1
    w1, w2, w3, w4, w5, w6 = 10, 2, 2, 1, 1, 1
    F.loc[k, 'data'] = (F.iloc[k-1, 0]*w1 + P.iloc[Np-1, 0]*w2 + P.iloc[Np-2, 0]*w3 +
                     P.iloc[0   , 0]*w4 + P.iloc[1, 0]*w5 + P.iloc[2, 0]*w6)/(w1+w2+w3+w4+w5+w6)    
    
    k = 2
    w1, w2, w3, w4, w5, w6 = 6, 5, 2, 1, 1, 1
    F.loc[k, 'data'] = (F.iloc[k-1, 0]*w1 + F.iloc[k-2, 0]*w2 + 
                     P.iloc[1  , 0]*w3 + P.iloc[2  , 0]*w4 + P.iloc[3, 0]*w5 + P.iloc[4, 0]*w6)/(w1+w2+w3+w4+w5+w6)    
    
    k = 3 
    w1, w2, w3, w4, w5, w6 = 5, 2, 1, 1, 1, 1
    F.loc[k, 'data'] = (F.iloc[k-1, 0]*w1 + F.iloc[k-2, 0]*w2 + F.iloc[k-3, 0]*w3 +
                     P.iloc[2  , 0]*w4 + P.iloc[3, 0]*w5 + P.iloc[4, 0]*w6)/(w1+w2+w3+w4+w5+w6)    

    k = 4 
    w1, w2, w3, w4, w5, w6 = 4, 2, 1, 1, 1, 1
    F.loc[k, 'data'] = (F.iloc[k-1, 0]*w1 + F.iloc[k-2, 0]*w2 + F.iloc[k-3, 0]*w3 +
                     P.iloc[3  , 0]*w4 + P.iloc[4, 0]*w5 + P.iloc[5, 0]*w6)/(w1+w2+w3+w4+w5+w6)    

    k = 5
    w1, w2, w3, w4, w5, w6 = 4, 2, 1, 1, 1, 1
    F.loc[k, 'data'] = (F.iloc[k-1, 0]*w1 + F.iloc[k-2, 0]*w2 + 
                     P.iloc[4  , 0]*w3 + P.iloc[5  , 0]*w4 + P.iloc[6, 0]*w5 + P.iloc[7, 0]*w6)/(w1+w2+w3+w4+w5+w6)
    
    k = 6
    w1, w2, w3, w4, w5, w6 = 4, 1, 1, 1, 1, 1
    F.loc[k, 'data'] = (F.iloc[k-1, 0]*w1 +
                     P.iloc[4  , 0]*w2 + P.iloc[5  , 0]*w3 + P.iloc[6, 0]*w4 + P.iloc[7, 0]*w5 + P.iloc[7, 0]*w6)/(w1+w2+w3+w4+w5+w6)
    
    w1, w2, w3, w4, w5, w6 = 6, 1, 1, 1, 1, 1
    for k in range(7, Np-1): # range(7, Np) actually goes up to Np - 1
        F.loc[k, 'data'] = (F.iloc[k-1, 0]*w1 +
                     P.iloc[k-2  , 0]*w2 + P.iloc[k-1  , 0]*w3 + P.iloc[k, 0]*w4 + P.iloc[k+1, 0]*w5 + P.iloc[k+1, 0]*w6)/(w1+w2+w3+w4+w5+w6)

    return F

if __name__ == "__main__":
    print("Previsao")
    
    # Carregar os dados
    wights = pd.DataFrame({'wights': [3, 2]})
    
    # Rodando pelo Sypder, estou na pasta MPC-WIQ. Rodou normal
    # Rodando pelo VS Code, estou na pasta MPC-WIQ. Rodou normal
    datas = pd.read_csv(".\A-Modelos_Previsao\Dados_PV_15_min_1ano.csv")


    # Definir o intervalo de amostras
    Np = 96
    
    
    # Teste de posição
    # value2 = past.loc[Np-1, 'p_pv']
    
    rodadas = 1
    for N in range(0, rodadas):
        beginning = 400 + N
        past = datas.iloc[beginning:beginning+Np]
        
        real_future = datas.iloc[beginning+Np:beginning+Np+Np]
        
        
        forecast = mmpw(past, Np)      
        
        
        enable_plot = 0
        if (enable_plot):
            # Configurar os passos de tempo e plotar
            time_steps = list(range(Np))
            plt.figure(figsize=(12, 6))
        
            # Plotar os dados
            plt.plot(time_steps, past['p_pv'].values, marker='o', linestyle='-', label='Past')
            plt.plot(time_steps, forecast['data'].values, marker='o', linestyle='-', label='Predict')
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
        
        # # Salvar a figura em um arquivo
        # plt.tight_layout()
        # plt.savefig(os.path.join(output_dir, f'previsao_{N:02d}.png'))  # Salva com o nome 'previsao_00.png', 'previsao_01.png', etc.
        # plt.close()  # Fecha a figura para liberar memória
        
        # from moviepy.editor import ImageSequenceClip

        # # Criar um vídeo a partir das imagens salvas
        # clip = ImageSequenceClip(output_dir, fps=5)  # Ajuste 'fps' conforme necessário
        # clip.write_videofile("previsao_potencia.mp4", codec='libx264')
