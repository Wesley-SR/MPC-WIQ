# -*- coding: utf-8 -*-
# ============================================================================#
# PROJETO V2G: ALGORITMO DE OTIMIZAÇÃO E CONTROLE PREDITIVO
# Otimização utilizando MILP com a biblioteca PulP (Solver: CBC)
# ============================================================================#




import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import load_workbook

import time
import numpy as np
# from forecast_NNet import run_forecast_NNet 
from forecast_mm import run_forecast_mm
# from forecast_MMPL import run_forecast_MMPL
from estimate_SOC import bike_use
from online_optimization import run_online_optimization
from offline_optimization import run_offline_optimization
# from plot_online_charts import run_online_plot_charts
# from plot_offline_charts import run_offline_plot_charts


# ==================== LEGENDA DAS PRINCIPAIS MATRIZES =======================#
# M = Matriz com os valores totais dos dados de entrada (Main)
# P = Dados passado + medição atual (Past)
# F_PV = Dados de previsão do PV + medição atual (Forecast)
# I = Dados de entrada para a otimização (Input to optmization)
# R = Resultado da otimização (Result)
# C = Sinais de Controle (Control signal)






# ============================================================================#
# CONSTANTS
# ============================================================================#
constants = pd.DataFrame({'Np': [288],
                          'qtd_ciclos_para_rodar_MPC': [288],
                          'ts': [0.083],
                          'Q_bat_est': [12], # kWh
                          'soc_max_est': [0.95],
                          'soc_min_est': [0.2],
                          'soc_ini_est': [0.90],
                          'p_max_bat_est': [12],
                          'soc_ref_est': [0.90],
                          'Q_SC': [0.289], # kWh
                          'soc_max_SC': [0.95],
                          'soc_min_SC': [0.05],
                          'soc_ini_SC': [0.5],
                          'p_max_SC': [13],
                          'soc_ref_SC': [0.5],
                          'eff_conv_est': [1],
                          'eff_conv_SC': [1],
                          'p_max_inv_ac': [20],
                          'p_max_rede_exp': [20],
                          'p_max_rede_imp': [20],
                          'bay_pass_PV_forecast': 1,
                          'k_pv_ref': 1,
                          'Peso_k_pv': 0.05,
                          'Peso_delta_est': 0.45,
                          'Peso_ref_est': 0.45,
                          'Peso_ref_SC': 0.05})

Np                        = constants.loc[0, 'Np'] # Horizonte de previsão, 24 horas com 96 amostras com intervalo de 15 minutos
qtd_ciclos_para_rodar_MPC = constants.loc[0, 'qtd_ciclos_para_rodar_MPC'] # Tempo em que é rodado o MPC (96 = 1 dia, 1 = 15 minutos)
ts                        = constants.loc[0, 'ts']
num_bikes                 = constants.loc[0, 'num_bikes']
Q_bike                    = constants.loc[0, 'Q_bike']
Q_bat_est                 = constants.loc[0, 'Q_bat_est'] # Deve ser o ch e dc constante
eff_conv_bikes            = constants.loc[0, 'eff_conv_bikes']
eff_conv_est              = constants.loc[0, 'eff_conv_est']
kM                       = Np # Esse é o "k" que vai percorrer na matriz M

soc_max_est             = constants.loc[0, 'soc_max_est'] # soc Maximo da bateria
soc_min_est             = constants.loc[0, 'soc_min_est'] # soc minimo da bateria
sta_bat_cost            = constants.loc[0, 'sta_bat_cost'] # (R$)
N_cycles_est            = constants.loc[0, 'N_cycles_est'] # Numer of battery cycles
lin_bat_degra_cost_est  = (sta_bat_cost/Q_bat_est)/(2*N_cycles_est*(soc_max_est-soc_min_est))

bay_pass_PV_forecast    = constants.loc[0, 'bay_pass_PV_forecast']
# FIM CONSTANTS
# ============================================================================#












# ============================================================================#
# EXECUTA O ALGORITMO OFFLINE
# ============================================================================#
# M_offline_out = pd.read_csv('Matrizes_for_MPC/M_offline_out.csv', index_col=['tempo'], sep=";")
print("--------------------------------------------------------")
print("Executando Otimização OFFLINE")




""" ===========================================================================

                                OTIMIZAÇÃO OFFLINE

============================================================================"""
M_to_off = pd.read_csv('Matrices_for_offline_optimization/M.csv', index_col=['tempo'],sep=",") # 288 amostras = 3 dias, 1 anterior e 2 futuros
I_to_off = pd.read_csv('Matrices_for_offline_optimization/I.csv', index_col=['tempo'],sep=",") # 192 amostras = 2 dias futuros
R_to_off = pd.read_csv('Matrices_for_offline_optimization/R.csv', index_col=['tempo'],sep=",") # 288 amostras
P_to_off = pd.read_csv('Matrices_for_offline_optimization/P.csv', index_col=['tempo'],sep=",")
# pesos = pd.read_csv('Matrices_for_offline_optimization/pesos.csv',sep=",")
mult_bikes_to_off = pd.read_csv('Matrices_for_offline_optimization/multiplicador_bikes.csv', index_col=['tempo'], sep=",")

start_off = time.perf_counter()

# RUN
M_offline_out, R_offline_out, I_offline, resultado_final_custos_e_receitas_offline  = run_offline_optimization(constants, M_to_off, I_to_off, R_to_off, P_to_off) # OFFLINE
# After use, del DataFrames
del M_to_off, I_to_off, R_to_off, P_to_off

total_time_off = time.perf_counter() - start_off

print("Tempo total de execução do offline: {} segundos".format(total_time_off))
print("--------------------------------------------------------")
print("\n\n")

# FIM DO ALGORITMO OFFLINE
# ============================================================================#












# ============================================================================#
# PREPARA OS DADOS PARA PODER RODAR O LOOP DO MPC QUE CHAMA A OTIMIZAÇÃO ONLINE
# ============================================================================#

M = pd.read_csv('Matrizes_for_MPC/M.csv', index_col=['tempo'], sep=",")
I = pd.read_csv('Matrizes_for_MPC/I.csv', index_col=['tempo'], sep=",")
R = pd.read_csv('Matrizes_for_MPC/R.csv', index_col=['tempo'], sep=",")
C = pd.read_csv('Matrizes_for_MPC/C.csv', index_col=['tempo'], sep=",")
F_bikes = pd.read_csv('Matrizes_for_MPC/F_bikes.csv', index_col=['tempo'], sep=",")
real_use_bikes = pd.read_csv('Matrices_for_offline_optimization/F_bikes.csv', index_col=['tempo'], sep=",")
F_load = pd.read_csv('Matrizes_for_MPC/F_load.csv', index_col=['tempo'], sep=",")
F_PV_after = pd.read_csv('Matrizes_for_MPC/Previsoes_PV.csv', index_col=['tempo'], sep=",")
F_bikes_after = pd.read_csv('Matrizes_for_MPC/Previsoes_bike_1.csv', index_col=['tempo'], sep=",")
pesos_mpc = pd.read_csv('Matrizes_for_MPC/pesos.csv',sep=",")
mult_bikes = pd.read_csv('Matrizes_for_MPC/multiplicador_bikes.csv', index_col=['tempo'], sep=",")



# ============================================================================#
# ATUALIZA A MATRIZ M COM OS DADOS DE SAÍDA DO ALGORITMO DE OTIMIZAÇÃO OFFLINE
M.loc[:, 'PV_previsao_off'] = M_offline_out.loc[:, 'PV_previsao']
M.loc[:, 'PV_real'] = M_offline_out.loc[:, 'PV_real'] # Para alterar o PV real do online mexe no M do offline
M.loc[:, 'p_rede_imp_ref'] = R_offline_out.loc[:, 'p_rede_imp_ref'] # Sinal de referência
M.loc[:, 'p_rede_exp_ref'] = R_offline_out.loc[:, 'p_rede_exp_ref'] # Sinal de referência
M.loc[:, 'soc_est_ref'] = R_offline_out.loc[:, 'soc_est_ref'] # Sinal de referência para o SOC da estacionaria (depois usar no R_offline_out)



# ============================================================================#
# MATRIZ PARA SALVAR OS VALORES DAS FUNÇÃO OBJETIVO
FO = pd.DataFrame({"FO_value":[0], "FO_status":['Inicio']})
salvar_iteracao_de_numero_X = qtd_ciclos_para_rodar_MPC
R_x_iteracao = R
I_x_iteracao = I











""" ===========================================================================
             
                                   LOOP DO MPC

============================================================================"""
for k in range(0, qtd_ciclos_para_rodar_MPC): # k=0 é o instante inicial, equivalente a M[96] = M[kM]

    # Lembrar que M carrega um dia anterior
    if k == 0:
        print("Entrando no LOOP do MPC")
    
    print("--------------------------------------------------------")
    print('k = {}'.format(k))
    
    
    
    
    
    
    """ =======================================================================
    1º) FAZER MEDIDAS
    
    I[0] = medições
    Coloca na primeira linha da matriz I as medições reais do instante atual
    Obs.: Por mais que na nomenclatura da matriz I contenha a palavra "previsão",
    a primeira linha tem dados reais medidos
    ======================================================================= """ 

    # Coloca a potência do PV atual na matriz I
    I.loc[0,'PV_previsao'] = M.loc[kM,'PV_real']
    
    # Atualiza a demanda atual na matriz I
    I.loc[0,'load_previsao'] = M.loc[kM,'load_real']
                   
    
    
    # Atualiza o SOC atual da bateria ESTACIONÁRIA na matriz I
    if k == 0:
        # Não mexe na matriz M
        I.loc[0,'soc_est'] = constants.loc[0, 'soc_ini_est'] # M.loc[kM,'soc_est']
        if (M.loc[kM,'soc_est'] < 0.2 or M.loc[kM,'soc_est'] > 0.8):
            print("SoC inicial da bateria estacionária fora do range")
    else:
        M.loc[kM,'soc_est'] =  M.loc[kM-1,'soc_est'] + ((M.loc[kM-1,'p_ch_est_cps']*eff_conv_est - M.loc[kM-1,'p_dc_est_cps']/eff_conv_est)*ts)/Q_bat_est        
        I.loc[0,'soc_est']   =  M.loc[kM,'soc_est']

        
        
        
        
        

    
    """ =======================================================================
    2º) FAZER PREVISÕES
    
    Primeiro, monta-se a matriz com os dados do dia anterior. Inclui-se as
    leituras atuais e reais, pois são serão levadas em condideração na previsão
    
    Segundo, faz as previsões
    
    Terceiro, coloca-se as previsõe na matriz I
    ======================================================================= """ 
    
    # (2.1) MONTA A MATRIZ P COM DADOS DO DIA ANTETIOR
    # P RECEBE 96 AMOSTRAS DA MATRIZ M
    
    P = M.loc[kM-(Np-1): kM] # Pega o instante atual + 95 amostras do dia anterior. Quando k = 0, P recebe M[1:96]
    # A ultima amostra de P é a do instante atual
    P = P.reset_index() # Renumera o index (atualiza o tempo)
    # P = P.drop('tempo',axis=1) # Deleta a coluna tempo
    P = P.rename(columns={'tempo': 'tempo_ant'}) # Renomeia a coluna tempo
    P.index.name = 'tempo' # Coloca nome no index
       
  
    # 2.2) PREVISÃO DO PV
    # Depois é descartado a última posição do vetor F_PV e então concatena o 
    # que sobrou com a medição atual
    if bay_pass_PV_forecast:
        print("Bypassou a previsão do PV")
        F_PV = pd.DataFrame({'PV_previsao': [0]*Np})
        for i in range(0, F_PV.shape[0]):
            F_PV.loc[i, 'PV_previsao'] = M.loc[i+kM+1,'PV_real']  
    else:
        print("Revisar previsão para ver se o instante atual permanece")
        F_PV = run_forecast_mm(P) # Chama o algoritmo de previsão com média movel
        # F_PV = run_forecast_NNet(P) # Chama o algoritmo de previsão com redes neurais
        # F_PV = run_forecast_MMPL(P) # Chama o algoritmo de MMPL
        # F_PV = M.loc[kM+1:kM+Np,'PV_real'].reset_index() # Utiliza para previsão os dados reais
    
    
    # Salva o real e o que foi previsto do PV para cada iteração
    for i in range(0, Np):
        F_PV_after.loc[i,'F_PV_{}'.format(k)] = F_PV.loc[i,'PV_previsao']
        F_PV_after.loc[i,'P_{}'.format(k)] = M.loc[i+kM+1,'PV_real']
        
    
    # Guarda a previsão em M. Salva apenas o primerio termo de F_PV
    # O primeiro termo de F_PV é a previsão do próximo instante, por isso kM+1
    if k < 95:
        M.loc[kM+1, 'PV_previsao'] = np.float64(F_PV.loc[0,'PV_previsao'])
    
    
    # 2.4) PREVISÃO DA DEMANDA
    for a in range(0,96):
        I.loc[a, 'load_previsao'] = F_load.loc[a, 'load_previsao']
    
    
    
    
        
    
    
    
    
    """ =======================================================================
    3º) ATUALIZA A MATRIZ I COM AS PREVISÕES
    
    I[0] já foi preenchido com as medições reais
    
    Agora vamos preencher I[1:Np-1]
    
    (a+1) é para pular o I[0]
    ======================================================================= """
   
    for a in range(0, Np-1):
        # Colocar a previsão do PV na matriz I
        I.loc[a+1,'PV_previsao'] = np.float64(F_PV.loc[a,'PV_previsao'])
        
    
    
    
    
    
    
    
    """ =======================================================================
    4º) 
            ATUALIZA A MATRIZ I COM AS REFERÊNCIAS
    ======================================================================= """
    for i in range(0, Np):
        
        # Colocar as curvas de referências de imp., exp. na matriz I e SOC da estacionária
        I.loc[i,'p_rede_imp_ref'] = M.loc[i+kM,'p_rede_imp_ref']
        I.loc[i,'p_rede_exp_ref'] = M.loc[i+kM,'p_rede_exp_ref']
        
        # Option SOC ref. est.
        # SOC ref from offline
        # I.loc[i,'soc_est_ref'] = M.loc[i+kM,'soc_est_ref']
        # SOC ref fixed
        I.loc[i,'soc_est_ref'] = constants.loc[0, 'soc_est_ref']
        
        # Colocar o custo de energia na matriz I
        I.loc[i, 'custo_energia_imp'] = M.loc[i+kM,'custo_energia_imp']
        I.loc[i, 'custo_energia_exp'] = M.loc[i+kM,'custo_energia_exp']

    

    
    
    
    """ =======================================================================
    5º) 
        RESOLVER O PROBLEMA DE OTIMIZAÇÃO ONLINE
    ======================================================================= """
    start_on = time.perf_counter()
    R, FO_value, FO_status, I_online = run_online_optimization(constants, I, R, pesos_mpc)
    # R, FO_value, FO_status = run_online_optimization(I, R, pesos_mpc, mult_bikes)
    total_time_on = time.perf_counter() - start_on
    
    # Valor da função objetivo
    FO.loc[k, 'FO_value'] = FO_value
    FO.loc[k, 'FO_status'] = FO_status
    print("Tempo total otim. ON: {}".format(total_time_on))
    print("--------------------------------------------------------")
    
    
    
    
    
    
    
    """ =======================================================================
    6º) 
        ATUALIZA A MATRIZ M COM OS DADOS OBTIDOS DA OTIMIZAÇÃO
    ======================================================================= """
    # Sinal de controle para potência da rede para o instante k+1
    M.loc[kM,'p_rede_imp'] = R.loc[0,'p_rede_imp']
    M.loc[kM,'p_rede_exp'] = R.loc[0,'p_rede_exp']
    
        
    # Sinal de controle para a estacionária para o instante k+1
    M.loc[kM,'p_ch_est_cps'] =  R.loc[0,'p_ch_est_cps']
    M.loc[kM,'p_dc_est_cps'] =  R.loc[0,'p_dc_est_cps']
    
    C.iloc[k] = R.loc[0]
    
    kM += 1
    
    
    
    
    """ =======================================================================
    7º) 
        SALVANDO DADOS DE CADA ITERAÇÁO PARA ANALISAR
    ======================================================================= """
    
    if k == 0:
        salvando_iteracoes = I.add_suffix(f'_{k}')
        novas_colunas = R.add_suffix(f'_{k}')
        salvando_iteracoes = pd.concat([salvando_iteracoes, novas_colunas], axis = 1)
        
    else:
        novas_colunas = I.add_suffix(f'_{k}')
        salvando_iteracoes = pd.concat([salvando_iteracoes, novas_colunas], axis = 1)   
        
        novas_colunas = R.add_suffix(f'_{k}')
        salvando_iteracoes = pd.concat([salvando_iteracoes, novas_colunas], axis = 1)
    
    if k == salvar_iteracao_de_numero_X: 
        R_x_iteracao = R
        I_x_iteracao = I
    
    """ =======================================================================
             Aqui acaba o loop do MPC
    ======================================================================="""







# ============================================================================#
# EXTRAÇÃO DE DADOS DA OTIMIZAÇÃO ONLINE
# ============================================================================#
for k in range(0,96):
    soc_total_real = 0
    cx_total_real = 0
    soc_total_previsao = 0
    cx_total_previsao = 0

    est_degradation = 0

    
    
    M.loc[:,'p_est_total'] = M.loc[:,'p_dc_est_cps'] - M.loc[:,'p_ch_est_cps']
    
    M.loc[k+Np,'p_rede'] = M.loc[k+Np,'p_rede_imp'] - M.loc[k+Np,'p_rede_exp']
    M.loc[k+Np,'p_rede_ref'] = M.loc[k+Np,'p_rede_imp_ref'] - M.loc[k+Np,'p_rede_exp_ref']


bike_use_class = bike_use()
real_use_bikes, N_out_total = bike_use_class.run_estimate_SOC_and_degradation(real_use_bikes)

P1 = sum([M.loc[k,'p_rede_exp']*M.loc[k,'custo_energia_exp'] for k in range(M.shape[0])])*ts

P2 = M.loc[2*Np-1,'revenue_accumulated_rental'] # 2*Np-1 é para pegar o acumulado até o final do dia, k = 191

P3 = sum([M.loc[k,'p_rede_imp']*M.loc[k,'custo_energia_imp'] for k in range(M.shape[0])])*ts

P4 = sum([(lin_bat_degra_cost_est*(M.loc[k,'p_dc_est_cps'] + M.loc[k,'p_ch_est_cps'])*ts) for k in range(M.shape[0])])

P5 = sum([sum([real_use_bikes.loc[k, 'degrad_bike_previsao_{}'.format(b)] for b in range(num_bikes)]) for k in range(real_use_bikes.shape[0])])


resultado_final_custos_e_receitas_online = pd.DataFrame({  'R1': [0]*1,
                                                           'R2': [0]*1,
                                                           'C1': [0]*1,
                                                           'C2': [0]*1,
                                                           'C3': [0]*1,
                                                           'C4': [0]*1,
                                                           'FO': [0]*1})
    
resultado_final_custos_e_receitas_online.loc[0, 'R1'] = P1
resultado_final_custos_e_receitas_online.loc[0, 'R2'] = P2
resultado_final_custos_e_receitas_online.loc[0, 'C1'] = P3
resultado_final_custos_e_receitas_online.loc[0, 'C2'] = P4
resultado_final_custos_e_receitas_online.loc[0, 'C4'] = P5
resultado_final_custos_e_receitas_online.loc[0, 'FO'] = P1 + P2 + P3 + P4 + P5













# =============================================================================
# IMPRIME RESULTADOS
# =============================================================================

print("\n\n\n\n")
print("=============================================================================")
print("=============================================================================")
print("Final results")

print("----- Offline -----")
print('R1 = {}'.format(resultado_final_custos_e_receitas_offline.loc[0, 'R1']/2))
print('R2 = {}'.format(resultado_final_custos_e_receitas_offline.loc[0, 'R2']/2))
print('C1 = {}'.format(resultado_final_custos_e_receitas_offline.loc[0, 'C1']/2))
print('C2 = {}'.format(resultado_final_custos_e_receitas_offline.loc[0, 'C2']/2))
print('C3 = {}'.format(resultado_final_custos_e_receitas_offline.loc[0, 'C3']/2))
print('C4 = {}'.format(resultado_final_custos_e_receitas_offline.loc[0, 'C4']/2))
print('FO = {}'.format(resultado_final_custos_e_receitas_offline.loc[0, 'FO']/2))

print("----- Online -----")
print('R1 = {}'.format(resultado_final_custos_e_receitas_online.loc[0, 'R1']))
print('R2 = {}'.format(resultado_final_custos_e_receitas_online.loc[0, 'R2']))
print('C1 = {}'.format(resultado_final_custos_e_receitas_online.loc[0, 'C1']))
print('C2 = {}'.format(resultado_final_custos_e_receitas_online.loc[0, 'C2']))
print('C3 = {}'.format(resultado_final_custos_e_receitas_online.loc[0, 'C3']))
print('C4 = {}'.format(resultado_final_custos_e_receitas_online.loc[0, 'C4']))
print('FO = {}'.format(resultado_final_custos_e_receitas_online.loc[0, 'FO']))

# Save final results
resultado_final_custos_e_receitas_on_off = pd.DataFrame({'R1_on':  [0]*1,
                                                         'R2_on':  [0]*1,
                                                         'C1_on':  [0]*1,
                                                         'C2_on':  [0]*1,
                                                         'C3_on':  [0]*1,
                                                         'C4_on':  [0]*1,
                                                         'FO_on':  [0]*1,
                                                         'R1_off': [0]*1,
                                                         'R2_off': [0]*1,
                                                         'C1_off': [0]*1,
                                                         'C2_off': [0]*1,
                                                         'C3_off': [0]*1,
                                                         'C4_off': [0]*1,
                                                         'FO_off': [0]*1,
                                                         })

resultado_final_custos_e_receitas_on_off.loc[0, 'R1_on'] = resultado_final_custos_e_receitas_online.loc[0, 'R1']
resultado_final_custos_e_receitas_on_off.loc[0, 'R2_on'] = resultado_final_custos_e_receitas_online.loc[0, 'R2']
resultado_final_custos_e_receitas_on_off.loc[0, 'C1_on'] = resultado_final_custos_e_receitas_online.loc[0, 'C1']
resultado_final_custos_e_receitas_on_off.loc[0, 'C2_on'] = resultado_final_custos_e_receitas_online.loc[0, 'C2']
resultado_final_custos_e_receitas_on_off.loc[0, 'C3_on'] = resultado_final_custos_e_receitas_online.loc[0, 'C3']
resultado_final_custos_e_receitas_on_off.loc[0, 'C4_on'] = resultado_final_custos_e_receitas_online.loc[0, 'C4']
resultado_final_custos_e_receitas_on_off.loc[0, 'FO_on'] = resultado_final_custos_e_receitas_online.loc[0, 'FO']

resultado_final_custos_e_receitas_on_off.loc[0, 'R1_off'] = resultado_final_custos_e_receitas_offline.loc[0, 'R1']/2
resultado_final_custos_e_receitas_on_off.loc[0, 'R2_off'] = resultado_final_custos_e_receitas_offline.loc[0, 'R2']/2
resultado_final_custos_e_receitas_on_off.loc[0, 'C1_off'] = resultado_final_custos_e_receitas_offline.loc[0, 'C1']/2
resultado_final_custos_e_receitas_on_off.loc[0, 'C2_off'] = resultado_final_custos_e_receitas_offline.loc[0, 'C2']/2
resultado_final_custos_e_receitas_on_off.loc[0, 'C3_off'] = resultado_final_custos_e_receitas_offline.loc[0, 'C3']/2
resultado_final_custos_e_receitas_on_off.loc[0, 'C4_off'] = resultado_final_custos_e_receitas_offline.loc[0, 'C4']/2
resultado_final_custos_e_receitas_on_off.loc[0, 'FO_off'] = resultado_final_custos_e_receitas_offline.loc[0, 'FO']/2













# =============================================================================
# SALVA RESULTADOS
# =============================================================================

resultado_final_custos_e_receitas_on_off.to_csv('Matrizes_results/resultado_final_custos_e_receitas_on_off.csv',sep=',')


M_online_1_day = M
M_online_1_day = M_online_1_day.iloc[Np:]
M_online_1_day = M_online_1_day.iloc[:-Np]
M_online_1_day = M_online_1_day.reset_index(drop=True)


M_offline_out_1_day = M_offline_out
M_offline_out_1_day = M_offline_out_1_day.iloc[Np:]
M_offline_out_1_day = M_offline_out_1_day.iloc[:-Np]
M_offline_out_1_day = M_offline_out_1_day.reset_index(drop=True)


# Salva a saida do offline
# R_offline_out.to_csv('Matrizes_results/R_offline_out.csv',sep=';')
M_offline_out.to_csv('Matrizes_results/M_offline_out.csv',sep=',')
M_offline_out_1_day.to_csv('Matrizes_results/M_offline_out_1_day.csv',sep=',')


# Salva a saida do online
R.to_csv('Matrizes_results/R_online_out.csv',sep=',')
# M.to_csv('Matrizes_results/M_online_out.csv',sep=',')
M_online_1_day.to_csv('Matrizes_results/M_online_out_1_day.csv',sep=',')
FO.to_csv('Matrizes_results/FO_online.csv', sep=',')

I.to_csv('Matrizes_results/I_online.csv',sep=',')

salvando_iteracoes.to_csv('Matrizes_results/salvando_iteracoes.csv',sep=',')

I_x_iteracao.to_csv('Matrizes_results/I_x_iteracao.csv',sep=',')
R_x_iteracao.to_csv('Matrizes_results/R_x_iteracao.csv',sep=',')