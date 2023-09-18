'''============================================================================
PROJETO V2G
MODELO DE OTIMIZAÇÃO - MILP
#==========================================================================='''

import time
import pulp as pl
import pandas as pd
from forecast_mm import run_forecast_mm
# from forecast_MMPL import run_forecast_MMPL


def run_offline_optimization(constants, M_to_off, I_to_off, R_to_off, P_to_off):
    
    
    
    """ =======================================================================
    1º) RECEBER ENTRADAS
    
    ======================================================================= """ 
    M = M_to_off
    I = I_to_off
    R = R_to_off
    P = P_to_off
    time_array = I.index
    
    
    
    
    
    """ =======================================================================
    2º) CARREGAR CONSTANTES DO PROBLEMA
    
    ======================================================================= """ 
    Np = constants.loc[0, 'Np']*2
    ts                      = constants.loc[0, 'ts'] # Intervalo da amostra (0.083h = 5 min)
    num_amostras            = time_array.size
    window                  = constants.loc[0, 'Np']
    
    # FOTOVOLTAICO
    k_pv_ref                = constants.loc[0, 'k_pv_ref']
   
    # BATERIA ESTACIONÁRIA
    soc_max_est             = constants.loc[0, 'soc_max_est'] # soc Maximo da bateria
    soc_min_est             = constants.loc[0, 'soc_min_est'] # soc minimo da bateria
    soc_ini_est             = constants.loc[0, 'soc_ini_est']
    p_max_bat_est           = constants.loc[0, 'p_max_bat_est'] # Deve ser o ch e dc constante (antes = 3)
    Q_bat_est               = constants.loc[0, 'Q_bat_est'] # Energia total da bateria estacionária (kWh) (antes = 9.6)
    soc_ref_est             = constants.loc[0, 'soc_ref_est']
    
    
    
    # SUPERCAPACITOR
    soc_max_SC             = constants.loc[0, 'soc_max_SC'] # soc Maximo da bateria
    soc_min_SC             = constants.loc[0, 'soc_min_SC'] # soc minimo da bateria
    soc_ini_SC             = constants.loc[0, 'soc_ini_SC']
    p_max_SC               = constants.loc[0, 'p_max_SC'] # Deve ser o ch e dc constante (antes = 3)
    Q_SC                   = constants.loc[0, 'Q_SC'] # Energia total da bateria estacionária (kWh) (antes = 9.6)
    soc_ref_SC             = constants.loc[0, 'soc_ref_SC']
    
    
    
    # INVERSORES
    eff_conv_est            = constants.loc[0, 'eff_conv_est']
    eff_conv_SC            = constants.loc[0, 'eff_conv_SC']
    
    bay_pass_PV_forecast    = constants.loc[0, 'bay_pass_PV_forecast']
    
    # PENALIDADES
    # PENALIDADES
    Peso_k_pv = constants.loc[0, 'Peso_k_pv']
    Peso_delta_est = constants.loc[0, 'Peso_delta_est']
    Peso_ref_est = constants.loc[0, 'Peso_ref_est']
    Peso_ref_SC = constants.loc[0, 'Peso_ref_SC']

    
    
    
    
    
    """ =======================================================================
    4º) REALIZAR AS PREVISÕES
    - Insere na matriz I
    
    ======================================================================= """    
    # Colocar o custo de energia na matriz I
    I.loc[:,'custo_energia_imp'] = M.loc[window:3*window-1,'custo_energia_imp'].reset_index() # 2 últimos dias da matriz M da tarifa de energia
    I.loc[:,'custo_energia_exp'] = M.loc[window:3*window-1,'custo_energia_exp'].reset_index() # 2 últimos dias da matriz M da tarifa de energia
    
    
    # PV
    # Utiliza o dia anterior para fazer a previsão de 2 dias seguintes
    # P[0] se refere a 00:15 do dia anterior
    # P[95] se refere a 00:00 de agora, ou seja, o instante atual
    
    # Monta a matriz P de M[1] até M[288], incluindo a medição atual 
    for k in range(0, P.shape[0]):
        P.loc[k,'PV_real'] = M.loc[k+1,'PV_real']
        
    if bay_pass_PV_forecast:
        print("Bypassou a previsão do PV")
        F = pd.DataFrame({'PV_previsao': [0]*(P.shape[0])})
        for i in range(0, I.shape[0]-1):
            F.loc[i, 'PV_previsao'] = M.loc[i+window+1,'PV_real'] # Index 1 do segundo dia de M[97] (index 0 depois vem da medida)
        
    else:
        F = run_forecast_mm(P)
    
    # F = run_forecast_MMPL(P)
    
    # Coloca a previsão na matriz I (Matriz I contêm 2 dias)
    # Atualmente, copia a previsão para o dia 1 e depois para o dia 2
    for k in range(0, I.shape[0]): # 0 a 2*288 = 576
        
        # PREVISÃO: DEMANDA
        # Assumimos uma previsão da carga, no entanto no online vai ocorrer a
        # carga real, ou seja, não vai ter erro de previsão
        I.loc[k,'load_previsao'] = M.loc[k+window,'load_real']
        
        # Salva o que foi previsto para a carga
        M.loc[k+window,'load_previsao'] = I.loc[k,'load_previsao']
        
        
        # MEDIÇÃO ATUAL: PV
        # Para k=0 e k=window, previsão recebe a medição real !!!
        if (k == 0 or k == window):
            # PV
            I.loc[k,'PV_previsao'] = M.loc[window,'PV_real']
            M.loc[k+window,'PV_previsao'] = F.loc[0,'PV_previsao'] # Para salvar
                
        
        # Copia a previsão para o primeiro dia
        # Em F contem as previsões, mas não vamos pegar em k=0, pois entra a medição
        elif k <= Np-1:
            # PV
            # Inicia pegando de F[0]
            I.loc[k,'PV_previsao'] = F.loc[k-1,'PV_previsao']
            M.loc[k+window,'PV_previsao'] = F.loc[k-1,'PV_previsao'] # Para salvar
                
        # Copia a previsão para o segundo dia
        elif k >= Np+1:
            # PV
            I.loc[k,'PV_previsao'] = F.loc[k-window-1,'PV_previsao']
            M.loc[k+window,'PV_previsao'] = F.loc[k-window-1,'PV_previsao']
            
        else:
            print('Out of range')
    
    
    
    """ =======================================================================
    5º) CRIAR OBJETO PULP
    
    ======================================================================= """ 
    
    opt_objective = pl.LpMinimize
    # opt_objective = pl.LpMaximize
    prob = pl.LpProblem("otimizacao_V2G", opt_objective)
    solver = pl.PULP_CBC_CMD(msg=False, timeLimit=60*5, gapRel= 0.0001)
    # solver = pl.SCIP_CMD(msg=False, timeLimit=60*5, gapRel=0.001)
    
    # Solver Disponívels
    # ['PULP_CBC_CMD', 'MIPCL_CMD', 'SCIP_CMD']
    # Solver Possíveis
    # ['GLPK_CMD', 'PYGLPK', 'CPLEX_CMD', 'CPLEX_PY', 'CPLEX_DLL', 'GUROBI', 
    # 'GUROBI_CMD', 'MOSEK', 'XPRESS', 'PULP_CBC_CMD', 'COIN_CMD', 'COINMP_DLL', 
    # 'CHOCO_CMD', 'MIPCL_CMD', 'SCIP_CMD']
    
    
    
    
    
    
    """ =======================================================================
    6º) CRIAR VARIÁVEIS DO PROBLEMA
    
    ======================================================================= """ 
    
    k_pv = pl.LpVariable.dicts('k_pv',
                               range(num_amostras),
                               lowBound=0, upBound=1,
                               cat='Continuous')
    
    # BATERIA ESTACIONÁRIA:
    # Charge power in stationary battery side
    p_ch_bat_est_bs = pl.LpVariable.dicts('p_ch_bat_est_bs',
                                          range(num_amostras),
                                          lowBound=0, upBound=p_max_bat_est,
                                          cat='Continuous')
    
    # Dicharge power in stationary battery side
    p_dc_bat_est_bs = pl.LpVariable.dicts('p_dc_bat_est_bs',
                                          range(num_amostras),
                                          lowBound=0, upBound=p_max_bat_est,
                                          cat='Continuous')
    # # Charge power in coupling point side
    p_ch_bat_est_cps = pl.LpVariable.dicts('p_ch_bat_est_cps',
                                           range(num_amostras),
                                           lowBound=0, upBound=p_max_bat_est,
                                           cat='Continuous')
    # Discharge power in coupling point side
    p_dc_bat_est_cps = pl.LpVariable.dicts('p_dc_bat_est_cps',
                                           range(num_amostras),
                                           lowBound=0, upBound=p_max_bat_est,
                                           cat='Continuous')
    
    flag_ch_bat_est = pl.LpVariable.dicts('flag_ch_bat_est',
                                          range(num_amostras),
                                          cat='Binary')
    flag_dc_bat_est = pl.LpVariable.dicts('flag_dc_bat_est',
                                          range(num_amostras),
                                          cat='Binary')
    
    soc_est = pl.LpVariable.dicts('soc_est',
                                  range(num_amostras),
                                  lowBound=soc_min_est, upBound=soc_max_est,
                                  cat='Continuous')
    
    # Seguimento SOC da estacionária
    mod_SOC_est_1 = pl.LpVariable.dicts('mod_SOC_est_1', range(num_amostras), lowBound= 0, upBound=1, cat='Continuous')
    mod_SOC_est_2 = pl.LpVariable.dicts('mod_SOC_est_2', range(num_amostras), lowBound= 0, upBound=1, cat='Continuous')
    flag_mod_SOC_est_1 = pl.LpVariable.dicts('flag_mod_SOC_est_1', range(num_amostras), cat='Binary')
    flag_mod_SOC_est_2 = pl.LpVariable.dicts('flag_mod_SOC_est_2', range(num_amostras), cat='Binary')
    # Variação da estacionária
    mod_dif_est_1 = pl.LpVariable.dicts('mod_dif_est_1', range(num_amostras), lowBound= 0, upBound=1, cat='Continuous')
    mod_dif_est_2 = pl.LpVariable.dicts('mod_dif_est_2', range(num_amostras), lowBound= 0, upBound=1, cat='Continuous')
    flag_mod_dif_est_1 = pl.LpVariable.dicts('flag_mod_dif_est_1', range(num_amostras), cat='Binary')
    flag_mod_dif_est_2 = pl.LpVariable.dicts('flag_mod_dif_est_2', range(num_amostras), cat='Binary')

    
    # SUPERCAPACITOR:
    # Charge power
    p_ch_SC_scs = pl.LpVariable.dicts('p_ch_SC_scs',
                                        range(num_amostras),
                                        lowBound=0, upBound=p_max_SC,
                                        cat='Continuous')
    
    # Dicharge power in stationary battery side
    p_dc_SC_scs = pl.LpVariable.dicts('p_dc_SC_scs',
                                        range(num_amostras),
                                        lowBound=0, upBound=p_max_SC,
                                        cat='Continuous')
    # Charge power in coupling point side
    p_ch_SC_cps = pl.LpVariable.dicts('p_ch_SC_cps',
                                        range(num_amostras),
                                        lowBound=0, upBound=p_max_SC,
                                        cat='Continuous')
    # Discharge power in coupling point side
    p_dc_SC_cps = pl.LpVariable.dicts('p_dc_SC_cps',
                                        range(num_amostras),
                                        lowBound=0, upBound=p_max_SC,
                                        cat='Continuous')
    
    flag_ch_SC = pl.LpVariable.dicts('flag_ch_SC',
                                          range(num_amostras),
                                          cat='Binary')
    flag_dc_SC = pl.LpVariable.dicts('flag_dc_SC',
                                          range(num_amostras),
                                          cat='Binary')
    
    soc_SC = pl.LpVariable.dicts('soc_SC',
                                  range(num_amostras),
                                  lowBound=soc_min_SC, upBound=soc_max_SC,
                                  cat='Continuous')
    
    # Seguimento SOC do SC
    mod_SOC_SC_1 = pl.LpVariable.dicts('mod_SOC_SC_1', range(num_amostras), lowBound= 0, upBound=1, cat='Continuous')
    mod_SOC_SC_2 = pl.LpVariable.dicts('mod_SOC_SC_2', range(num_amostras), lowBound= 0, upBound=1, cat='Continuous')
    flag_mod_SOC_SC_1 = pl.LpVariable.dicts('flag_mod_SOC_SC_1', range(num_amostras), cat='Binary')
    flag_mod_SOC_SC_2 = pl.LpVariable.dicts('flag_mod_SOC_SC_2', range(num_amostras), cat='Binary')
    
    
    min_p = 0
    max_p = 10000
    
    P1 = pl.LpVariable('P1', lowBound=(min_p), upBound=(max_p))
    P2 = pl.LpVariable('P2', lowBound=(min_p), upBound=(max_p))

    P3 = pl.LpVariable('P3', lowBound=(min_p), upBound=(max_p))
    P4 = pl.LpVariable('P4', lowBound=(min_p), upBound=(max_p))
    
    
    # BALANÇO DE POTÊNCIA
    balanco_potencia = pl.LpVariable.dicts('balanco_potencia',
                                            range(num_amostras), 
                                            lowBound=0, upBound=0, cat='Continuous')
    
    
    
    
    
    
    """ =======================================================================
    7º) CRIAR FUNÇÃO OBJETIVO
    
    ======================================================================= """ 

    objective_function = (P1 + P2 + P3 + P4)
    
    prob.setObjective(objective_function)
    
    
    
    
    """ =======================================================================
    
    8º) CRIAR RESTRIÇÕES AO LONGO DO HORIZONTE DE PREVISÃO
    
    ======================================================================= """ 
    
    ''' --------------------------- RESTRIÇÕES ---------------------------- '''
    for k in I.index:
                  
       # POTÊNCIA BATERIA ESTACIONÁRIA:
       prob += p_ch_bat_est_bs[k] <= p_max_bat_est * flag_ch_bat_est[k]
       prob += p_dc_bat_est_bs[k] <= p_max_bat_est * flag_dc_bat_est[k]
       prob += flag_ch_bat_est[k] + flag_dc_bat_est[k] <= 1 # simultaneity
       
       
       # POTÊNICA SUPERCAPACITOR:
       prob += p_ch_SC_scs[k] <= p_max_SC * flag_ch_SC[k]
       prob += p_dc_SC_scs[k] <= p_max_SC * flag_dc_SC[k]
       prob += flag_ch_SC[k] + flag_dc_SC[k] <= 1 # simultaneity
       
       # PERDAS NOS INVERSORES DA ESTACIONÁRIA E NO TRAFO
       prob += p_ch_bat_est_bs[k] == p_ch_bat_est_cps[k] * eff_conv_est # battery <-- CP * n
       prob += p_dc_bat_est_cps[k] == p_dc_bat_est_bs[k] * eff_conv_est # battery * n --> CP
       prob += p_ch_SC_scs[k] == p_ch_SC_cps[k] * eff_conv_SC # battery <-- CP * n
       prob += p_dc_SC_cps[k] == p_dc_SC_scs[k] * eff_conv_SC # battery * n --> CP
       
       # SOC estacionaria
       if k == 0:
           # Estacionaria
           prob += soc_est[k] == soc_ini_est
           prob += soc_SC[k] == soc_ini_SC
       else:
           # Estacionaria
           prob += soc_est[k] ==  (soc_est[k-1] + ((p_ch_bat_est_bs[k-1] - p_dc_bat_est_bs[k-1])*ts/Q_bat_est))
           prob += soc_SC[k] ==  (soc_SC[k-1] + ((p_ch_SC_scs[k-1] - p_dc_SC_scs[k-1])*ts/Q_SC))
           
           # Variação de potência da estacionária
           prob += mod_dif_est_1[k] - mod_dif_est_2[k] == (p_ch_bat_est_bs[k] - p_ch_bat_est_bs[k-1]) - (p_dc_bat_est_bs[k] - p_dc_bat_est_bs[k-1]) 
           prob += mod_dif_est_1[k] <= flag_mod_dif_est_1[k]
           prob += mod_dif_est_2[k] <= flag_mod_dif_est_2[k]
           prob += flag_mod_dif_est_1[k] + flag_mod_dif_est_2[k] <= 1
       
       
       # BALANÇO DE POTÊNCIA NO BARRAMENTO DC    
       prob += balanco_potencia[k] == 0
       prob += balanco_potencia[k] == (  p_dc_bat_est_cps[k]
                                       + p_dc_SC_cps[k]
                                       + k_pv[k]*I.loc[k,'PV_previsao']
                                       - p_ch_bat_est_cps[k]
                                       - p_ch_SC_cps[k]
                                       - I.loc[k,'load_previsao'])
       
       # MÓDULOS PARA A FUNÇÃO OBJETIVO
       # Seguimento de referência da estacionária
       prob += mod_SOC_est_1[k] - mod_SOC_est_2[k] == (soc_ref_est - soc_est[k])
       prob += mod_SOC_est_1[k] <= flag_mod_SOC_est_1[k]
       prob += mod_SOC_est_2[k] <= flag_mod_SOC_est_2[k]
       prob += flag_mod_SOC_est_1[k] + flag_mod_SOC_est_2[k] <= 1

       # Seguimento de referência do Supercapacitor      
       prob += mod_SOC_SC_1[k] - mod_SOC_SC_2[k] == (soc_ref_SC - soc_SC[k])
       prob += mod_SOC_SC_1[k] <= flag_mod_SOC_SC_1[k]
       prob += mod_SOC_SC_2[k] <= flag_mod_SOC_SC_2[k]
       prob += flag_mod_SOC_SC_1[k] + flag_mod_SOC_SC_2[k] <= 1
    
    
    # FO
    prob += P1 == Peso_k_pv      * pl.lpSum([(k_pv_ref - k_pv[k]) for k in range(num_amostras)])/280 # k PV
    prob += P2 == Peso_delta_est * pl.lpSum([((mod_dif_est_1[k] + mod_dif_est_2[k])) for k in range(num_amostras)])/250 # Delta est
    prob += P3 == Peso_ref_est   * pl.lpSum([((mod_SOC_est_1[k] + mod_SOC_est_2[k])) for k in range(num_amostras)])/61 # Ref est
    prob += P4 == Peso_ref_SC    * pl.lpSum([((mod_SOC_SC_1[k] + mod_SOC_SC_2[k])) for k in range(num_amostras)])/123 # Ref SC
    
    
    
    
    
    
    
    """ =======================================================================
    9º) EXECUTAR OTIMIZAÇÃO
    
    ======================================================================= """ 
    print('Iniciou otimização offline')
    solution  = prob.solve(solver)
    print('Finalizou otimização offline')

    # print("Status:", pl.LpStatus[prob.status])
    
    print("Status: {}\n".format(pl.LpStatus[solution]))
    
    if not pl.LpStatus[solution] == 'Optimal':
        raise("Offline Infactivel")
    
    
    
    
    
    
    """ =======================================================================
    10º) SALVAR DADOS DA OTIMIZAÇÃO
    
    ======================================================================= """ 
    for k in I.index:
        # ESTACIONÁRIA
        M.loc[k+window,'p_ch_bat_est_cps'] = p_ch_bat_est_cps[k].varValue
        M.loc[k+window,'p_dc_bat_est_cps'] = p_dc_bat_est_cps[k].varValue
        M.loc[k+window,'p_est_total_cps'] = p_dc_bat_est_cps[k].varValue - p_ch_bat_est_cps[k].varValue
        M.loc[k+window,'soc_est'] = soc_est[k].varValue
        # SUPERCAPACITOR
        M.loc[k+window,'p_dc_SC_cps'] = p_dc_SC_cps[k].varValue
        M.loc[k+window,'p_ch_SC_cps'] = p_ch_SC_cps[k].varValue
        M.loc[k+window,'p_SC_total_cps'] = p_dc_SC_cps[k].varValue - p_ch_SC_cps[k].varValue
        M.loc[k+window,'soc_SC'] = soc_SC[k].varValue
        
        M.loc[k+window,'k_pv'] = k_pv[k].varValue
        M.loc[k+window,'k_pv_x_PV'] = k_pv[k].varValue*I.loc[k,'PV_previsao']
        
        
        
        
    print('P1 (k_PV)       = {}'.format(P1.varValue))
    print('P2 (dif. pot. est.)       = {}'.format(P2.varValue))
    print('P3 (ref. SOC est.)       = {}'.format(P3.varValue))
    print('P4 (ref. SOC SC)       = {}'.format(P4.varValue))
    
   
    print('FO = P1 + P2 + P3 + P4 = {}'.format(P1.varValue + P2.varValue + P3.varValue + P4.varValue))
    print("Valor da FO: {}\n".format(pl.value(prob.objective)))
    
    
    
    
    
    """ ================== ESCREVER OS RESULTADOS EM UM CSV =============== """
    # The problem data is written to an .lp file
    # prob.writeLP("WhiskasModel.lp")
    # return M, R, I, degradacao, result
    return M, R, I










""" =======================================================================
     PARA RODAR OTIMIZAÇÃO OFFLINE INDEPENDENTE DO MPC

======================================================================= """ 
if __name__ == "__main__":
    
    ''' ------------------------- INPUT DATA ------------------------------ '''
    M_to_off = pd.read_csv('Matrices_for_offline_optimization/M.csv', index_col=['amostra'],sep=",") # 288 amostras = 3 dias, 1 anterior e 2 futuros
    I_to_off = pd.read_csv('Matrices_for_offline_optimization/I.csv', index_col=['amostra'],sep=",") # 192 amostras = 2 dias futuros
    R_to_off = pd.read_csv('Matrices_for_offline_optimization/R.csv', index_col=['amostra'],sep=",") # 288 amostras
    P_to_off = pd.read_csv('Matrices_for_offline_optimization/P.csv', index_col=['amostra'],sep=",")
    # pesos = pd.read_csv('Matrices_for_offline_optimization/pesos.csv',sep=",")
    
    
    # CONSTANTS
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
    

    
    print("Init")
    start_off = time.perf_counter()
    M, R, I  = run_offline_optimization(constants, M_to_off, I_to_off, R_to_off, P_to_off) # OFFLINE
    
    # After use, del DataFrames
    del M_to_off, I_to_off, R_to_off, P_to_off
    
    
    M_1_day = M.loc[288:288*2].reset_index()
    total_time_off = time.perf_counter() - start_off
    print("Simulation time = {}".format(total_time_off))
    
    M.to_csv('Matrizes_results/M_offline_out.csv',sep=',')
    M_1_day.to_csv('Matrizes_results/M_offline_out_1_day.csv',sep=',')
