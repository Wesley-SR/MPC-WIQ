# -*- coding: utf-8 -*-
'''============================================================================
                               PROJETO V2G
#==========================================================================='''

import pulp as pl


''' MAIN DATA '''
# I = pd.read_csv('M.csv', index_col=['tempo'], sep=";")

def run_online_optimization(constants, Input, Output, pesos, mult_bikes):
    
    I = Input # The Input matrix include forecast, energy cost, bike connection, etc
    R = Output # Only the model matrix to output optimization
    ''' -------------------- DEFINIÇÃO DO PROBLEMA ---------------------------- '''
    prob = pl.LpProblem("otimizacao_online_V2G", pl.LpMinimize) # LpMinimize e LpMaximize
    solver = pl.PULP_CBC_CMD(msg=False, timeLimit=60*1)
    # Solver Disponívels (gratuitos)
    # ['PULP_CBC_CMD', 'SCIP_CMD']
    
    # Solver Possíveis (pagos)
    # ['GLPK_CMD', 'PYGLPK', 'CPLEX_CMD', 'CPLEX_PY', 'CPLEX_DLL', 'GUROBI', 
    # 'GUROBI_CMD', 'MOSEK', 'XPRESS', 'PULP_CBC_CMD', 'COIN_CMD', 'COINMP_DLL', 
    # 'CHOCO_CMD', 'MIPCL_CMD', 'SCIP_CMD']
    
    time_array = I.index
    
    ''' --------------------- CONSTANTES E PARÂMETROS ------------------------- ''' 
    ts              = constants.loc[0, 'ts'] # Intervalo de tempo (0.25h = 15 min)
    Np    = constants.loc[0, 'Np']
    
    # REDE
    p_max_rede_imp  = constants.loc[0, 'p_max_rede_imp']
    p_max_rede_exp  = constants.loc[0, 'p_max_rede_exp']
    
    # BATERIA BICICLETA
    num_bikes       = constants.loc[0, 'num_bikes']
    soc_max_bike    = constants.loc[0, 'soc_max_bike'] # soc Maximo da bateria
    soc_min_bike    = constants.loc[0, 'soc_min_bike'] # soc minimo da bateria
    p_max_bat_bike  = constants.loc[0, 'p_max_bat_bike'] # (kW) -> ch/dc a 500 W
    Q_bike          = constants.loc[0, 'Q_bike'] # kWh por bateria, sendo 12 V, são de 52.5 Ah = 630 Wh
    
    # BATERIA ESTACIONÁRIA
    soc_max_est     = constants.loc[0, 'soc_max_est'] # soc Maximo da bateria
    soc_min_est     = constants.loc[0, 'soc_min_est'] # soc minimo da bateria
    p_max_bat_est   = constants.loc[0, 'p_max_bat_est'] # Deve ser o ch e dc constante
    Q_bat_est       = constants.loc[0, 'Q_bat_est'] # Energia total da bateria estacionária (kWh)
    
    # INVERSORES
    eff_conv_bikes  = constants.loc[0, 'eff_conv_bikes'] #
    # eff_conv_ac     = constants.loc[0, 'eff_conv_ac'] # 0.96
    eff_conv_est    = constants.loc[0, 'eff_conv_est']
    # Maximum power of inverters
    p_max_inv_ac    = constants.loc[0, 'p_max_inv_ac'] # (kW)    
    
    # PENALIDADES
    peso_imp    = pesos.loc[0, 'peso_imp'] # Parcela 1
    peso_exp    = pesos.loc[0, 'peso_exp'] # Parcela 2
    peso_est    = pesos.loc[0, 'peso_est'] # Parcela 3
    peso_bikes  = pesos.loc[0, 'peso_bikes'] # Parcela 4
    print("Pesos online")
    print("Peso imp : {}".format(peso_imp))
    print("Peso exp : {}".format(peso_exp))
    print("Peso est : {}".format(peso_est))
    print("Peso bikes : {}".format(peso_bikes))
    # peso_dif_est = 0
    
    # pesos.loc[0, 'peso_imp']    = peso_imp
    # pesos.loc[0, 'peso_exp']    = peso_exp
    # pesos.loc[0, 'peso_est']    = peso_est
    # pesos.loc[0, 'peso_bikes']  = peso_bikes
    
    maximo_parcela_1 = 1 # 960 # Imp
    maximo_parcela_2 = 1 # 960 # Exp
    # maximo_parcela_3 = 1 # 48 # Est
    # maximo_parcela_4 = 1 # 960 # Bicicletas
    
    
    
    
    ''' ------------------------- VARIÁVEIS DO PROBLEMA ----------------------- '''
    # REDE -> Não está sendo considerado eficiência
    p_rede_exp = pl.LpVariable.dicts('p_rede_exp', range(Np),lowBound=0, upBound=p_max_rede_exp,cat='Continuous')
    p_rede_imp = pl.LpVariable.dicts('p_rede_imp', range(Np),lowBound=0, upBound=p_max_rede_imp,cat='Continuous')
    
    # Flags for network export
    flag_rede_exp = pl.LpVariable.dicts('flag_rede_exp',range(Np),cat='Binary')
    
    # Flags for network import
    flag_rede_imp = pl.LpVariable.dicts('flag_rede_imp',range(Np),cat='Binary')
    
    # BATERIA BIKES:
    p_ch_bikes_bs = pl.LpVariable.dicts('p_ch_bikes_bs', (range(Np),range(num_bikes)),lowBound=0, upBound=p_max_bat_bike,cat='Continuous')
    p_dc_bikes_bs = pl.LpVariable.dicts('p_dc_bikes_bs', (range(Np),range(num_bikes)),lowBound=0, upBound=p_max_bat_bike,cat='Continuous')
    p_ch_bikes_cps = pl.LpVariable.dicts('p_ch_bikes_cps', (range(Np),range(num_bikes)),lowBound=0, upBound=p_max_bat_bike/eff_conv_bikes,cat='Continuous')
    p_dc_bikes_cps = pl.LpVariable.dicts('p_dc_bikes_cps', (range(Np),range(num_bikes)),lowBound=0, upBound=p_max_bat_bike*eff_conv_bikes,cat='Continuous')
    
    # Flags for bike battery
    flag_ch_bat_bikes = pl.LpVariable.dicts('flag_ch_bat_bike', (range(Np),range(num_bikes)),cat='Binary')
    flag_dc_bat_bikes = pl.LpVariable.dicts('flag_dc_bat_bike', (range(Np),range(num_bikes)),cat='Binary')
    
    # State Of Charge
    soc_bikes = pl.LpVariable.dicts('soc_bike', (range(Np), range(num_bikes)), lowBound=soc_min_bike, upBound=soc_max_bike, cat='Continuous') 
    
    # BATERIA ESTACIONÁRIA:
    p_ch_est_bs = pl.LpVariable.dicts('p_ch_est_bs',range(Np),lowBound=0, upBound=p_max_bat_est,cat='Continuous')
    p_dc_est_bs = pl.LpVariable.dicts('p_dc_est_bs',range(Np),lowBound=0, upBound=p_max_bat_est,cat='Continuous')
    p_ch_est_cps = pl.LpVariable.dicts('p_ch_est_cps',range(Np),lowBound=0, upBound=p_max_bat_est/eff_conv_est,cat='Continuous')
    p_dc_est_cps = pl.LpVariable.dicts('p_dc_est_cps',range(Np),lowBound=0, upBound=p_max_bat_est*eff_conv_est,cat='Continuous')
    flag_ch_bat_est = pl.LpVariable.dicts('flag_ch_bat_est',range(Np),cat='Binary')
    flag_dc_bat_est = pl.LpVariable.dicts('flag_dc_bat_est',range(Np),cat='Binary')
    soc_est = pl.LpVariable.dicts('soc_est',range(Np),lowBound=soc_min_est, upBound=soc_max_est,cat='Continuous')
    
    # MODULOS PARA A FUNÇÃO OBJETIVO
    # Importação da rede
    mod_imp_1 = pl.LpVariable.dicts('mod_imp_1', range(Np), lowBound= 0, upBound=p_max_rede_imp, cat='Continuous')
    mod_imp_2 = pl.LpVariable.dicts('mod_imp_2', range(Np), lowBound= 0, upBound=p_max_rede_imp, cat='Continuous')
    flag_mod_imp_1 = pl.LpVariable.dicts('flag_mod_imp_1', range(Np), cat='Binary')
    flag_mod_imp_2 = pl.LpVariable.dicts('flag_mod_imp_2', range(Np), cat='Binary')
    
    # Exportação da rede
    mod_exp_1 = pl.LpVariable.dicts('mod_exp_1', range(Np), lowBound= 0, upBound=p_max_rede_exp, cat='Continuous')
    mod_exp_2 = pl.LpVariable.dicts('mod_exp_2', range(Np), lowBound= 0, upBound=p_max_rede_exp, cat='Continuous')
    flag_mod_exp_1 = pl.LpVariable.dicts('flag_mod_exp_1', range(Np), cat='Binary')
    flag_mod_exp_2 = pl.LpVariable.dicts('flag_mod_exp_2', range(Np), cat='Binary')
    
    # Bateria estacionária
    # mod_est_1 = pl.LpVariable.dicts('mod_est_1', range(Np), lowBound= 0, upBound=1, cat='Continuous')
    # mod_est_2 = pl.LpVariable.dicts('mod_est_2', range(Np), lowBound= 0, upBound=1, cat='Continuous')
    # flag_mod_est_1 = pl.LpVariable.dicts('flag_mod_est_1', range(Np), cat='Binary')
    # flag_mod_est_2 = pl.LpVariable.dicts('flag_mod_est_2', range(Np), cat='Binary')
    # Variação da estacionária
    # mod_dif_est_1 = pl.LpVariable.dicts('mod_dif_est_1', range(Np), lowBound= 0, upBound=1, cat='Continuous')
    # mod_dif_est_2 = pl.LpVariable.dicts('mod_dif_est_2', range(Np), lowBound= 0, upBound=1, cat='Continuous')
    # flag_mod_dif_est_1 = pl.LpVariable.dicts('flag_mod_dif_est_1', range(Np), cat='Binary')
    # flag_mod_dif_est_2 = pl.LpVariable.dicts('flag_mod_dif_est_2', range(Np), cat='Binary')
    
    # Bateria das bikes
    # parcela4_aux = pl.LpVariable.dicts('parcela4_aux', (range(Np),range(num_bikes)), lowBound=0, upBound=1, cat='Continuous')
    
    
    
    
    ''' ------------------------- FUNÇÃO OBJETIVO ------------------------------'''
    
    # parcela1 = pl.lpSum([(mod_imp_1[k] + mod_imp_2[k]) for k in range(Np)])
    parcela1 = pl.lpSum([(mod_imp_1[k] + mod_imp_2[k]) for k in range(Np)]) # mod_imp_2[k]*0 para não penaliza quando P_imp < P_ref 
    
    # parcela2 = pl.lpSum([(mod_exp_1[k] + mod_exp_2[k]) for k in range(Np)])
    parcela2 = pl.lpSum([(mod_exp_1[k] + mod_exp_2[k]) for k in range(Np)]) # (mod_exp_1[k]*0 para não penaliza quando P_exp > P_ref
    
    # parcela3 = pl.lpSum([(mod_est_1[k] + mod_est_2[k]) for k in range(Np)])
    
    # parcela4 = pl.lpSum([(10-(soc_bike[k] + soc_bike1[k] + soc_bike2[k] + soc_bike3[k] +
    #                      soc_bike4[k] + soc_bike5[k] + soc_bike6[k] + soc_bike7[k] +
    #                      soc_bike8[k] + soc_bike9[k]
    #                      )) for k in range(Np)])
    
    # parcela4 = pl.lpSum([pl.lpSum([(parcela4_aux[k][b])*(mult_bikes.loc[0, 'mult_bike_{bike}'.format(bike=b)]) for b in range(num_bikes)]) for k in range(Np)])
    
    # parcela5 = pl.lpSum([(mod_dif_est_1[k] + mod_dif_est_2[k]) for k in range(Np)])
    
    objective_function =  (+ peso_imp   * parcela1 / maximo_parcela_1
                           + peso_exp   * parcela2 / maximo_parcela_2
                           # + peso_est   * parcela3 / maximo_parcela_3
                           # + peso_bikes * parcela4 / maximo_parcela_4
                           )

    
    prob.setObjective(objective_function)
    
    
    ''' --------------------------- RESTRIÇÕES -------------------------------- '''
    for k in range(Np):
    
        for b in range(0, num_bikes):
            
            # prob += soc_bikes[k][b] <= constants.loc[0, 'soc_max_bike'] - 0.01
            # prob += soc_bikes[k][b] >= constants.loc[0, 'soc_min_bike'] + 0.01
            
            if k == 0:
                # Desconectada, então soc = 0 e não pode carregar/descarregar
                if I.loc[k,'cx_bike_previsao_{}'.format(b)] == 0:
                    prob += soc_bikes[k][b] == 0
                    prob += flag_ch_bat_bikes[k][b] == 0
                    prob += flag_dc_bat_bikes[k][b] == 0
                # Faz a leitura do SOC e pode carregar/descarregar
                else:
                    prob += soc_bikes[k][b] == I.loc[k,'soc_bike_previsao_{}'.format(b)]
                        
                        
            else:
                # Desconectada, então soc = 0 e não pode carregar/descarregar
                if I.loc[k,'cx_bike_previsao_{}'.format(b)] == 0:
                    prob += soc_bikes[k][b] == 0
                    prob += flag_ch_bat_bikes[k][b] == 0
                    prob += flag_dc_bat_bikes[k][b] == 0
                # Conectada
                else:
                    # Chegou agora?
                    if I.loc[k-1,'cx_bike_previsao_{}'.format(b)] == 0:
                        prob += soc_bikes[k][b] == I.loc[k,'soc_bike_previsao_{}'.format(b)] # Leitura do protocolo Modbus
                    # Já estava conectada, então lê, nesse caso calcula e pode ch/dc
                    else:
                        prob += soc_bikes[k][b] ==  soc_bikes[k-1][b] + ((p_ch_bikes_bs[k-1][b] - p_dc_bikes_bs[k-1][b])*ts)/Q_bike
                        
                # Formulação antiga, apagar depois
                # # Chegou agora, então leitura e pode carregar/descarregar
                # elif I.loc[k,'cx_bike_previsao_{}'.format(b)] == 1 and I.loc[k-1,'cx_bike_previsao_{}'.format(b)] == 0:
                #     prob += soc_bikes[k][b] == I.loc[k,'soc_bike_previsao_{}'.format(b)] # Leitura do protocolo Modbus
                # # Já estava conectada, então lê, nesse caso calcula e pode ch/dc
                # else:
                #     prob += soc_bikes[k][b] ==  soc_bikes[k-1][b] + ((p_ch_bikes_bs[k-1][b] - p_dc_bikes_bs[k-1][b])*ts)/Q_bike
            
            # prob += flag_dc_bat_bike[k] == 0 # Forçando que as baterias não se descarreguem
            prob += p_ch_bikes_bs[k][b] <= p_max_bat_bike * flag_ch_bat_bikes[k][b]
            prob += p_dc_bikes_bs[k][b] <= p_max_bat_bike * flag_dc_bat_bikes[k][b]        
            prob += flag_ch_bat_bikes[k][b] + flag_dc_bat_bikes[k][b] <= 1 # simultaneity
            
            # PERDAS NOS INVERSORES WIRELESS
            prob += p_ch_bikes_bs[k][b] == p_ch_bikes_cps[k][b] * eff_conv_bikes # bike <-- CP * n
            prob += p_dc_bikes_cps[k][b] == p_dc_bikes_bs[k][b] * eff_conv_bikes # bike * n --> CP
        
        
            # VARIAVEL AUXILIAR PARA PARCELA 4
            # Essa parcela minimiza a função objetivo caso não tenha zero bikes conectadas
            # uma vez que é penalizada se o SOC for menor que 1
            # VARIAVEL AUXILIAR PARA PARCELA 4
            # if I.loc[k,'cx_bike_previsao_{b}'.format(b=b)] == 0: # Desconectada, então a FO é mínima
            #     prob += parcela4_aux[k][b] == 0
            # else: # Desconectada, então forçamos carregar
            #     prob += parcela4_aux[k][b] == soc_ref_bikes - soc_bikes[k][b]
        
        
        
        # BATERIA ESTACIONÁRIA:
        prob += p_ch_est_bs[k] <= p_max_bat_est * flag_ch_bat_est[k]
        prob += p_dc_est_bs[k] <= p_max_bat_est * flag_dc_bat_est[k]             
        prob += flag_dc_bat_est[k] + flag_ch_bat_est[k] <= 1 # simultaneity
        # SOC
        if k == 0:
            prob += soc_est[k] == I.loc[k,'soc_est']
        else:
            prob += soc_est[k] == soc_est[k-1] + (p_ch_est_bs[k-1] - p_dc_est_bs[k-1])*ts/Q_bat_est
        # PERDAS NO INVERSOR DA BATERIA ESTACIONÁRIA
        prob += p_ch_est_bs[k] == p_ch_est_cps[k] * eff_conv_est # battery <-- CP * n
        prob += p_dc_est_cps[k] == p_dc_est_bs[k] * eff_conv_est # battery * n --> CP
        
        # REDE
        # IMPORTAÇÃO E EXPORTAÇÃO DA REDE
        prob += p_rede_imp[k] <= p_max_inv_ac * flag_rede_imp[k]
        prob += p_rede_exp[k] <= p_max_inv_ac * flag_rede_exp[k]
        prob += flag_rede_imp[k] + flag_rede_exp[k] <= 1 # simultaneity
        
        
        ''' MODULOS PARA A FUNÇÃO OBJETIVO '''
        prob += mod_imp_1[k] - mod_imp_2[k] == (p_rede_imp[k] - I.loc[k,'p_rede_imp_ref'])
        
        prob += mod_exp_1[k] - mod_exp_2[k] == (p_rede_exp[k] - I.loc[k,'p_rede_exp_ref'])
        
        # prob += mod_est_1[k] - mod_est_2[k] == (soc_est_ref - soc_est[k])
        # prob += mod_est_1[k] - mod_est_2[k] == (soc_est[k] - I.loc[k,'soc_est_ref'])
        
        prob += mod_imp_1[k] <= flag_mod_imp_1[k] * p_max_rede_imp
        prob += mod_imp_2[k] <= flag_mod_imp_2[k] * p_max_rede_imp
        prob += mod_exp_1[k] <= flag_mod_exp_1[k] * p_max_rede_exp
        prob += mod_exp_2[k] <= flag_mod_exp_2[k] * p_max_rede_exp
        
        # Calcular o módulo do SOC da bat. est. menos a referência
        # prob += mod_est_1[k] <= flag_mod_est_1[k]
        # prob += mod_est_2[k] <= flag_mod_est_2[k]
        
        prob += flag_mod_imp_1[k] + flag_mod_imp_2[k] <= 1 # simultaneity
        prob += flag_mod_exp_1[k] + flag_mod_exp_2[k] <= 1 # simultaneity
        # prob += flag_mod_est_1[k] + flag_mod_est_2[k] <= 1 # simultaneity
        
        # BALANÇO DE POTÊNCIA NO BARRAMENTO DC
        prob += (pl.lpSum([p_dc_bikes_cps[k][b] for b in range(0,num_bikes)]) 
                 + I.loc[k,'PV_previsao'] 
                 + p_rede_imp[k]
                 + p_dc_est_cps[k]
                 == 
                 (pl.lpSum([p_ch_bikes_cps[k][b] for b in range(0,num_bikes)]))
                 + I.loc[k,'load_previsao']
                 + p_rede_exp[k] 
                 + p_ch_est_cps[k] 
                 )
        
        # prob += mod_exp_1[k] + mod_exp_2[k] <= 1.9
        
        # PERDAS NO TRAFO
        # prob += p_rede_imp_dc[k] == p_rede_imp_ac[k] * eff_conv_ac
        # prob += p_rede_exp_ac[k] == p_rede_exp_dc[k] * eff_conv_ac

    
    
    
    ''' ------------------- EXECUTA O ALGORITMO DE OTIMIZAÇÃO ---------------------------------------------------------------------------- '''
    print("\nEXECUTAR SOLVER\n")
    #prob.solve(solver)
    # prob.solve()
    
    solution  = prob.solve(solver)
    fo_status = pl.LpStatus[solution]
    fo_value = pl.value(prob.objective)
    print("Status: {}".format(fo_status))
    print("Valor da FO: {}".format(fo_value))
    
    if not pl.LpStatus[solution] == 'Optimal':
        raise("Online Infactivel")
    
    
    sum_parcela1 = 0
    sum_parcela2 = 0
    # sum_parcela3 = 0
    # sum_parcela4 = 0
    # sum_parcela5 = 0
    
    for k in range(Np):
       sum_parcela1 += mod_imp_1[k].varValue + mod_imp_2[k].varValue
       sum_parcela2 += mod_exp_1[k].varValue + mod_exp_2[k].varValue
       # sum_parcela3 += mod_est_1[k].varValue + mod_est_2[k].varValue
       # sum_parcela4 += sum([parcela4_aux[k][b].varValue for b in range(0, num_bikes)])
       # sum_parcela5 += mod_dif_est_1[k].varValue + mod_dif_est_2[k].varValue
    
    parcela1_normalizada = peso_imp  * sum_parcela1 / maximo_parcela_1
    parcela2_normalizada = peso_exp  * sum_parcela2 / maximo_parcela_2
    # parcela3_normalizada = peso_est  * sum_parcela3 / maximo_parcela_3
    # parcela4_normalizada = peso_bikes * sum_parcela4 / maximo_parcela_4
    # parcela5_normalizada = peso_dif_est * sum_parcela5 / maximo_parcela_5
    
    OF_FV =  (+ parcela1_normalizada
              + parcela2_normalizada
              # + parcela3_normalizada
              # + parcela4_normalizada
              )
              # + parcela5_normalizada
              # )
       
    # print("Parcela 1: {}".format(sum_parcela1))
    # print("Parcela 2: {}".format(sum_parcela2))
    # print("Parcela 3: {}".format(sum_parcela3))
    # print("Parcela 4: {}".format(sum_parcela4))
    # print("FO calculado: {}".format(OF_FV))
    
    # print("Parcela normalizada 1: {}".format(parcela1_normalizada))
    # print("Parcela normalizada 2: {}".format(parcela2_normalizada))
    # print("Parcela normalizada 3: {}".format(parcela3_normalizada))
    # print("Parcela  normalizada 4: {}".format(parcela4_normalizada))
    # print("FO calculado: {}".format(OF_FV))

    # print("\n\n")
    # for i in range(0, Np): 
    #     print("mod_exp_1[{}]: {}".format(i, mod_exp_1[i].varValue))
    #     print("mod_exp_2[{}]: {}".format(i, mod_exp_2[i].varValue))
    #     print("mod_exp_2[{i}] + mod_exp_2[{i}]: {mod}".format(i=i, mod=mod_exp_2[i].varValue))
        
    
    ''' ------------------ SALVAR RESULTADOS -------------------------------------------------------------------------------- '''
    # soma_parcelas = 0
    # soma_parcela_1 = 0
    # soma_parcela_2 = 0
    # soma_parcela_3 = 0
    # soma_parcela_4 = 0
    
    for i in range (0,96):
        R.loc[i,'p_rede_imp'] = p_rede_imp[i].varValue
        R.loc[i,'p_rede_exp'] = p_rede_exp[i].varValue
        
        for b in range(num_bikes):
            R.loc[i,'p_ch_bike_cps_{}'.format(b)] = p_ch_bikes_cps[i][b].varValue
            R.loc[i,'p_dc_bike_cps_{}'.format(b)] = p_dc_bikes_cps[i][b].varValue
            

        
        R.loc[i,'p_ch_est_cps'] = p_ch_est_cps[i].varValue
        R.loc[i,'p_dc_est_cps'] = p_dc_est_cps[i].varValue

        
        
        
        # print('{} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}'.format(mod_imp_1[i].varValue, mod_imp_2[i].varValue,
        #                                                    mod_exp_1[i].varValue, mod_exp_2[i].varValue,
        #                                                    mod_est_1[i].varValue, mod_est_2[i].varValue,
        #                                                    soc_bike[i].varValue, soc_bike1[i].varValue,
        #                                                    soc_bike2[i].varValue, soc_bike3[i].varValue,
        #                                                    soc_bike4[i].varValue, soc_bike5[i].varValue,
        #                                                    soc_bike6[i].varValue, soc_bike7[i].varValue,
        #                                                    soc_bike8[i].varValue, soc_bike9[i].varValue))
        
        # parcela_1 = mod_imp_1[i].varValue + mod_imp_2[i].varValue
        # parcela_2 = mod_exp_1[i].varValue + mod_exp_2[i].varValue
        # parcela_3 = mod_est_1[i].varValue + mod_est_2[i].varValue
        # parcela_4 = 10 - (soc_bike[i].varValue + soc_bike1[i].varValue + 
        #                   soc_bike2[i].varValue + soc_bike3[i].varValue + 
        #                   soc_bike4[i].varValue + soc_bike5[i].varValue + 
        #                   soc_bike6[i].varValue + soc_bike7[i].varValue + 
        #                   soc_bike8[i].varValue + soc_bike9[i].varValue)
        
        # soma_parcela_1 += parcela_1
        # soma_parcela_2 += parcela_2
        # soma_parcela_3 += parcela_3
        # soma_parcela_4 += parcela_4
        
        # soma_parcelas += (+ peso_imp  * parcela_1 / maximo_parcela_1
        #                        + peso_exp  * parcela_2 / maximo_parcela_2
        #                        + peso_est  * parcela_3 / maximo_parcela_3
        #                        + peso_bikes * parcela_4 / maximo_parcela_4
                               # )
        
        
        # print('imp {}, exp {}, est {}, bike {}'.format(parcela_1, parcela_2, parcela_3, parcela_4))
    
    # funcao_objetivo = (peso_imp  * soma_parcela_1 / maximo_parcela_1 + 
    #                    peso_exp  * soma_parcela_2 / maximo_parcela_2 + 
    #                    peso_est  * soma_parcela_3 / maximo_parcela_3 + 
    #                    peso_bikes * soma_parcela_4 / maximo_parcela_4)
    
    # print(funcao_objetivo)
    # print(soma_parcelas)
    # print('Valor Função objetivo: ', pl.value(prob.objective))
    # print('Valor Parcela 1: ', pl.value(parcela1))
    # print('Valor Parcela 2: ', pl.value(parcela2))
    # print('Valor Parcela 3: ', pl.value(parcela3))
    # print('Valor Parcela 4: ', pl.value(parcela4))
    #print(pl.value(parcela3))
    
    return R, OF_FV, fo_status, I

