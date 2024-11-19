# -*- coding: utf-8 -*-
'''============================================================================
                               PROJETO V2G
#==========================================================================='''

import pulp as pl
import pandas as pd


class OptimizationMILP():

    ''' ------------------------------------------------------------------------------- 
    isolated Optimization 3th
    --------------------------------------------------------------------------------'''
    @staticmethod
    def isolated_optimization_3th(Datas, pv_forecasted, load_forecasted):
        print("isolated Optimization in 3th")
        
        WEIGHT_K_PV      = 1
        WEIGHT_DELTA_BAT = 1
        WEIGHT_DELTA_BAT = 1
        WEIGHT_SOC_BAT   = 5
        
        ''' -------------------- Optimization Problem ---------------------------- '''
        prob = pl.LpProblem("OptimizationMILP", pl.LpMinimize) # LpMinimize e LpMaximize
        solver = pl.PULP_CBC_CMD(msg=False, timeLimit=60*1)
        # Solver Disponívels (gratuitos)
        # ['PULP_CBC_CMD', 'SCIP_CMD']



        ''' ------------------------- VARIÁVEIS DO PROBLEMA ----------------------- '''    
        # Battery power
        p_bat_dis        = pl.LpVariable.dicts('p_bat_dis',         range(Datas.NP_3TH),lowBound=0, upBound=Datas.P_BAT_MAX,cat='Continuous')
        p_bat_ch         = pl.LpVariable.dicts('p_bat_ch',          range(Datas.NP_3TH),lowBound=0, upBound=Datas.P_BAT_MAX,cat='Continuous')
        flag_ch_bat_est  = pl.LpVariable.dicts('flag_ch_bat_est',   range(Datas.NP_3TH),cat='Binary')
        flag_dis_bat_est = pl.LpVariable.dicts('flag_dis_bat_est',  range(Datas.NP_3TH),cat='Binary')
        soc_bat          = pl.LpVariable.dicts('soc_bat',           range(Datas.NP_3TH),lowBound=Datas.SOC_BAT_MIN, upBound=Datas.SOC_BAT_MAX,cat='Continuous')
        
        # Battery power variation module (Absolute value = A)
        # Charg
        abs_bat_a_var_ch      = pl.LpVariable.dicts('abs_bat_a_var_ch',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        abs_bat_b_var_ch      = pl.LpVariable.dicts('abs_bat_b_var_ch',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        flag_abs_bat_a_var_ch = pl.LpVariable.dicts('flag_abs_bat_a_var_ch', range(Datas.NP_3TH), cat='Binary')
        flag_abs_bat_b_var_ch = pl.LpVariable.dicts('flag_abs_bat_b_var_ch', range(Datas.NP_3TH), cat='Binary')
        # Discharge
        abs_bat_a_var_dis      = pl.LpVariable.dicts('abs_bat_a_var_dis',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        abs_bat_b_var_dis      = pl.LpVariable.dicts('abs_bat_b_var_dis',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        flag_abs_bat_a_var_dis = pl.LpVariable.dicts('flag_abs_bat_a_var_dis', range(Datas.NP_3TH), cat='Binary')
        flag_abs_bat_b_var_dis = pl.LpVariable.dicts('flag_abs_bat_b_var_dis', range(Datas.NP_3TH), cat='Binary')
        
        # Battery absolute values
        abs_bat_a_soc      = pl.LpVariable.dicts('abs_bat_a_soc',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_BAT_MAX, cat='Continuous')
        abs_bat_b_soc      = pl.LpVariable.dicts('abs_bat_b_soc',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_BAT_MAX, cat='Continuous')
        flag_abs_bat_a_soc = pl.LpVariable.dicts('flag_abs_bat_a_soc', range(Datas.NP_3TH), cat='Binary')
        flag_abs_bat_b_soc = pl.LpVariable.dicts('flag_abs_bat_b_soc', range(Datas.NP_3TH), cat='Binary')
        
        # Photovoltaic Panel
        k_pv              = pl.LpVariable.dicts('k_pv',          range(Datas.NP_3TH), lowBound=0, upBound=1, cat='Continuous')
        abs_k_pv_a_3th      = pl.LpVariable.dicts('abs_k_pv_a_3th',      range(Datas.NP_3TH), lowBound=0, upBound=1, cat='Continuous')
        abs_k_pv_b_3th      = pl.LpVariable.dicts('abs_k_pv_b_3th',      range(Datas.NP_3TH), lowBound=0, upBound=1, cat='Continuous')
        flag_abs_k_pv_a_3th = pl.LpVariable.dicts('flag_abs_k_pv_a_3th', range(Datas.NP_3TH), cat='Binary')
        flag_abs_k_pv_b_3th = pl.LpVariable.dicts('flag_abs_k_pv_b_3th', range(Datas.NP_3TH), cat='Binary')


        ''' ------------------------- FUNÇÃO OBJETIVO ------------------------------'''
        J_pv_3th          = pl.lpSum([(abs_k_pv_a_3th[k] + abs_k_pv_b_3th[k]) for k in range(Datas.NP_3TH)])
        
        J_bat_var_ch  = pl.lpSum([(abs_bat_a_var_ch[k] + abs_bat_b_var_ch[k])] for k in range(Datas.NP_3TH))
        
        J_bat_var_dis = pl.lpSum([(abs_bat_a_var_dis[k] + abs_bat_b_var_dis[k])] for k in range(Datas.NP_3TH))
        
        J_bat_var_soc = pl.lpSum([(abs_bat_a_soc[k] + abs_bat_b_soc[k])] for k in range(Datas.NP_3TH))
        
        # Divide por 2 porque sao duas parcelas referente a mesma coisa
        # TODO: Dividir pelo máximo da parcela (Deve passar por normalização)
        objective_function = ( (WEIGHT_K_PV      * J_pv_3th          / 1)
                             + (WEIGHT_DELTA_BAT * J_bat_var_ch  / 2)
                             + (WEIGHT_DELTA_BAT * J_bat_var_dis / 2)
                             + (WEIGHT_SOC_BAT   * J_bat_var_soc / 1)
                             )
        prob.setObjective(objective_function)
        
        
        
        ''' --------------------------- RESTRIÇÕES -------------------------------- '''
        '''
            No código, k = 0, é o mesmo que X(t+k|t) para k = 1, do texto.
            
            k=0 é o atual
        '''  
        for k in range(0, Datas.NP_3TH):
            
            # P_bat
            prob += p_bat_ch[k]  <= Datas.P_BAT_MAX * flag_ch_bat_est[k]
            prob += p_bat_dis[k] <= Datas.P_BAT_MAX * flag_dis_bat_est[k]
            prob += flag_ch_bat_est[k] + flag_dis_bat_est[k] <= 1 # simultaneity      
            
            # Absolute value for battery power variation
            if k > 0:
                prob += abs_bat_a_var_ch[k] - abs_bat_b_var_ch[k] == p_bat_ch[k] - p_bat_ch[k-1]
                prob += abs_bat_a_var_dis[k] - abs_bat_b_var_dis[k] == p_bat_dis[k] - p_bat_dis[k-1]
            else:
                if Datas.p_bat >= 0:
                   prob += abs_bat_a_var_ch[k] - abs_bat_b_var_dis[k] == 0
                   prob += abs_bat_a_var_dis[k] - abs_bat_b_var_dis[k] == p_bat_dis[k] - Datas.p_bat
                else:
                   prob += abs_bat_a_var_ch[k] - abs_bat_b_var_ch[k] == p_bat_ch[k] - Datas.p_bat
                   prob += abs_bat_a_var_dis[k] - abs_bat_b_var_dis[k] == p_bat_dis[k] - 0
            
            prob += abs_bat_a_var_ch[k] <= flag_abs_bat_a_var_ch[k] * Datas.P_BAT_VAR_MAX
            prob += abs_bat_b_var_ch[k] <= flag_abs_bat_b_var_ch[k] * Datas.P_BAT_VAR_MAX
            prob += flag_abs_bat_a_var_ch[k] + flag_abs_bat_b_var_ch[k] <= 1 # simultaneity
            prob += abs_bat_a_var_dis[k] <= flag_abs_bat_a_var_dis[k] * Datas.P_BAT_VAR_MAX
            prob += abs_bat_b_var_dis[k] <= flag_abs_bat_b_var_dis[k] * Datas.P_BAT_VAR_MAX
            prob += flag_abs_bat_a_var_dis[k] + flag_abs_bat_b_var_dis[k] <= 1 # simultaneity

            # Battery SOC
            if k > 0:
                prob += soc_bat[k] == soc_bat[k-1] - (p_bat_dis[k-1] - p_bat_ch[k-1])*Datas.TS_3TH/Datas.Q_BAT
            else:
                prob += soc_bat[k] == Datas.soc_bat

            # Absolute value between SOC and SOC_ref
            prob += abs_bat_a_soc[k] - abs_bat_b_soc[k] == soc_bat[k] - Datas.SOC_BAT_REF
            prob += abs_bat_a_soc[k] <= flag_abs_bat_a_soc
            prob += abs_bat_b_soc[k] <= flag_abs_bat_b_soc
            prob += flag_abs_bat_a_soc[k] + flag_abs_bat_b_soc[k] <= 1 # simultaneity

            # Absolute value between k_pv and K_PV_REF
            prob += abs_k_pv_a_3th[k] - abs_k_pv_b_3th[k] == k_pv[k] - Datas.K_PV_REF
            prob += abs_k_pv_a_3th[k] <= flag_abs_k_pv_a_3th
            prob += abs_k_pv_b_3th[k] <= flag_abs_k_pv_b_3th
            prob += flag_abs_k_pv_a_3th[k] + flag_abs_k_pv_b_3th[k] <= 1 # simultaneity
            
            
            # BALANÇO DE POTÊNCIA NO BARRAMENTO DC
            prob += (
                    k_pv[k]*pv_forecasted.loc[k, 'data'] + 
                    p_bat_dis[k]
                    ==
                    load_forecasted.loc[k, 'data'] + 
                    p_bat_ch[k]
                    )        
        
        
        
        ''' ------------------------------------------------------------------------------- 
        EXECUTA O ALGORITMO DE OTIMIZAÇÃO
        --------------------------------------------------------------------------------'''
        print("\nEXECUTAR SOLVER\n")
        solution  = prob.solve(solver)
        fo_status = pl.LpStatus[solution]
        fo_value = pl.value(prob.objective)
        print("Status: {}".format(fo_status))
        print("Valor da FO: {}".format(fo_value))
        
        if not pl.LpStatus[solution] == 'Optimal':
            raise("Infactivel optimization problem")
        
        
        
        ''' ------------------------------------------------------------------------------- 
        SALVA OS DADOS DA OTIMIZAÇÃO
        --------------------------------------------------------------------------------'''
        # for k in range(0, Datas.NP_3TH):
        #     Datas.R_3th.loc[k , 'p_bat_sch']  = p_bat_dis[k].varValue - p_bat_ch[k].varValue
        #     Datas.R_3th.loc[k , 'k_pv_sch']   = k_pv[k].varvalue
        results_3th = None
        fo_value = None
        if pl.LpStatus[solution] == 'Optimal':
            print("OTIMO")
            # Results
            results_3th = pd.DataFrame(index=range(Datas.NP_3TH), columns=['p_bat_sch', 'k_pv_sch', 'soc_bat'])
            for k in range(0, Datas.NP_3TH):
                results_3th.loc[k, 'p_bat_sch']   = p_bat_dis[k].varValue - p_bat_ch[k].varValue
                results_3th.loc[k, 'k_pv_sch']    = k_pv[k].varValue
                # results_3th.loc[0, 'p_grid_sch']  = p_grid.value[k]
                results_3th.loc[k, 'soc_bat']    = soc_bat[k].varValue
        else:
            print("ENGASGOU")

        return results_3th, fo_value


    ''' ------------------------------------------------------------------------------- 
    isolated Optimization 3th
    --------------------------------------------------------------------------------'''
    @staticmethod
    def isolated_optimization_2th(Datas, pv_forecasted, load_forecasted):
        print("isolated Optimization in 3th")
        
        WEIGHT_K_PV      = 1
        WEIGHT_DELTA_BAT = 1
        WEIGHT_DELTA_BAT = 1
        WEIGHT_SOC_BAT   = 5
        
        ''' -------------------- Optimization Problem ---------------------------- '''
        prob = pl.LpProblem("OptimizationMILP", pl.LpMinimize) # LpMinimize e LpMaximize
        solver = pl.PULP_CBC_CMD(msg=False, timeLimit=1)
        # Solver Disponívels (gratuitos)
        # ['PULP_CBC_CMD', 'SCIP_CMD']



        ''' ------------------------- VARIÁVEIS DO PROBLEMA ----------------------- '''    
        # Battery power
        p_bat_dis        = pl.LpVariable.dicts('p_bat_dis',         range(Datas.NP_2TH),lowBound=0, upBound=Datas.P_BAT_MAX,cat='Continuous')
        p_bat_ch         = pl.LpVariable.dicts('p_bat_ch',          range(Datas.NP_2TH),lowBound=0, upBound=Datas.P_BAT_MAX,cat='Continuous')
        flag_ch_bat_est  = pl.LpVariable.dicts('flag_ch_bat_est',   range(Datas.NP_2TH),cat='Binary')
        flag_dis_bat_est = pl.LpVariable.dicts('flag_dis_bat_est',  range(Datas.NP_2TH),cat='Binary')
        soc_bat          = pl.LpVariable.dicts('soc_bat',           range(Datas.NP_2TH),lowBound=Datas.SOC_BAT_MIN, upBound=Datas.SOC_BAT_MAX,cat='Continuous')
        
        # Battery power variation module (Absolute value = A)
        # Charg
        abs_bat_a_var_ch      = pl.LpVariable.dicts('abs_bat_a_var_ch',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        abs_bat_b_var_ch      = pl.LpVariable.dicts('abs_bat_b_var_ch',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        flag_abs_bat_a_var_ch = pl.LpVariable.dicts('flag_abs_bat_a_var_ch', range(Datas.NP_2TH), cat='Binary')
        flag_abs_bat_b_var_ch = pl.LpVariable.dicts('flag_abs_bat_b_var_ch', range(Datas.NP_2TH), cat='Binary')
        # Discharge
        abs_bat_a_var_dis      = pl.LpVariable.dicts('abs_bat_a_var_dis',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        abs_bat_b_var_dis      = pl.LpVariable.dicts('abs_bat_b_var_dis',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        flag_abs_bat_a_var_dis = pl.LpVariable.dicts('flag_abs_bat_a_var_dis', range(Datas.NP_2TH), cat='Binary')
        flag_abs_bat_b_var_dis = pl.LpVariable.dicts('flag_abs_bat_b_var_dis', range(Datas.NP_2TH), cat='Binary')
        
        # Battery absolute values
        abs_bat_a_soc      = pl.LpVariable.dicts('abs_bat_a_soc',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_MAX, cat='Continuous')
        abs_bat_b_soc      = pl.LpVariable.dicts('abs_bat_b_soc',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_MAX, cat='Continuous')
        flag_abs_bat_a_soc = pl.LpVariable.dicts('flag_abs_bat_a_soc', range(Datas.NP_2TH), cat='Binary')
        flag_abs_bat_b_soc = pl.LpVariable.dicts('flag_abs_bat_b_soc', range(Datas.NP_2TH), cat='Binary')
        
        # Photovoltaic Panel
        k_pv              = pl.LpVariable.dicts('k_pv',          range(Datas.NP_2TH), lowBound=0, upBound=1, cat='Continuous')
        abs_k_pv_a_3th      = pl.LpVariable.dicts('abs_k_pv_a_3th',      range(Datas.NP_2TH), lowBound=0, upBound=1, cat='Continuous')
        abs_k_pv_b_3th      = pl.LpVariable.dicts('abs_k_pv_b_3th',      range(Datas.NP_2TH), lowBound=0, upBound=1, cat='Continuous')
        flag_abs_k_pv_a_3th = pl.LpVariable.dicts('flag_abs_k_pv_a_3th', range(Datas.NP_2TH), cat='Binary')
        flag_abs_k_pv_b_3th = pl.LpVariable.dicts('flag_abs_k_pv_b_3th', range(Datas.NP_2TH), cat='Binary')


        ''' ------------------------- FUNÇÃO OBJETIVO ------------------------------'''
        J_pv_3th      = pl.lpSum([(abs_k_pv_a_3th[k] + abs_k_pv_b_3th[k]) for k in range(Datas.NP_2TH)])
        
        J_bat_var_ch  = pl.lpSum([(abs_bat_a_var_ch[k] + abs_bat_b_var_ch[k])] for k in range(Datas.NP_2TH))
        
        J_bat_var_dis = pl.lpSum([(abs_bat_a_var_dis[k] + abs_bat_b_var_dis[k])] for k in range(Datas.NP_2TH))
        
        J_bat_var_soc = pl.lpSum([(abs_bat_a_soc[k] + abs_bat_b_soc[k])] for k in range(Datas.NP_2TH))
        
        # Divide por 2 porque sao duas parcelas referente a mesma coisa
        # TODO: Dividir pelo máximo da parcela (Deve passar por normalização)
        objective_function = ( (WEIGHT_K_PV      * J_pv_3th          / 1)
                             + (WEIGHT_DELTA_BAT * J_bat_var_ch  / 2)
                             + (WEIGHT_DELTA_BAT * J_bat_var_dis / 2)
                             + (WEIGHT_SOC_BAT   * J_bat_var_soc / 1)
                             )
        prob.setObjective(objective_function)
        
        
        
        ''' --------------------------- RESTRIÇÕES -------------------------------- '''
        '''
            No código, k = 0, é o mesmo que X(t+k|t) para k = 1, do texto.
            
            k=0 é o atual
        '''  
        for k in range(0, Datas.NP_2TH):
            
            # P_bat
            prob += p_bat_ch[k]  <= Datas.P_BAT_MAX * flag_ch_bat_est[k]
            prob += p_bat_dis[k] <= Datas.P_BAT_MAX * flag_dis_bat_est[k]
            prob += flag_ch_bat_est[k] + flag_dis_bat_est[k] <= 1 # simultaneity      
            
            # Absolute value for battery power variation
            if k > 0:
                prob += abs_bat_a_var_ch[k] - abs_bat_b_var_ch[k] == p_bat_ch[k] - p_bat_ch[k-1]
                prob += abs_bat_a_var_dis[k] - abs_bat_b_var_dis[k] == p_bat_dis[k] - p_bat_dis[k-1]
            else:
                if Datas.p_bat >= 0:
                   prob += abs_bat_a_var_ch[k] - abs_bat_b_var_dis[k] == 0
                   prob += abs_bat_a_var_dis[k] - abs_bat_b_var_dis[k] == p_bat_dis[k] - Datas.p_bat
                else:
                   prob += abs_bat_a_var_ch[k] - abs_bat_b_var_ch[k] == p_bat_ch[k] - Datas.p_bat
                   prob += abs_bat_a_var_dis[k] - abs_bat_b_var_dis[k] == p_bat_dis[k] - 0
            
            prob += abs_bat_a_var_ch[k] <= flag_abs_bat_a_var_ch[k] * Datas.P_BAT_VAR_MAX
            prob += abs_bat_b_var_ch[k] <= flag_abs_bat_b_var_ch[k] * Datas.P_BAT_VAR_MAX
            prob += flag_abs_bat_a_var_ch[k] + flag_abs_bat_b_var_ch[k] <= 1 # simultaneity
            prob += abs_bat_a_var_dis[k] <= flag_abs_bat_a_var_dis[k] * Datas.P_BAT_VAR_MAX
            prob += abs_bat_b_var_dis[k] <= flag_abs_bat_b_var_dis[k] * Datas.P_BAT_VAR_MAX
            prob += flag_abs_bat_a_var_dis[k] + flag_abs_bat_b_var_dis[k] <= 1 # simultaneity

            # Battery SOC
            if k > 0:
                prob += soc_bat[k] == soc_bat[k-1] - (p_bat_dis[k-1] - p_bat_ch[k-1])*Datas.TS_3TH/Datas.Q_BAT
            else:
                prob += soc_bat[k] == Datas.soc_bat

            # Absolute value between SOC and SOC_ref
            prob += abs_bat_a_soc[k] - abs_bat_b_soc[k] == soc_bat[k] - Datas.SOC_BAT_REF
            prob += abs_bat_a_soc[k] <= flag_abs_bat_a_soc
            prob += abs_bat_b_soc[k] <= flag_abs_bat_b_soc
            prob += flag_abs_bat_a_soc[k] + flag_abs_bat_b_soc[k] <= 1 # simultaneity

            # Absolute value between k_pv and K_PV_REF
            prob += abs_k_pv_a_3th[k] - abs_k_pv_b_3th[k] == k_pv[k] - Datas.K_PV_REF
            prob += abs_k_pv_a_3th[k] <= flag_abs_k_pv_a_3th
            prob += abs_k_pv_b_3th[k] <= flag_abs_k_pv_b_3th
            prob += flag_abs_k_pv_a_3th[k] + flag_abs_k_pv_b_3th[k] <= 1 # simultaneity
            
            
            # BALANÇO DE POTÊNCIA NO BARRAMENTO DC
            prob += (
                    k_pv[k]*pv_forecasted.loc[k, 'data'] + 
                    p_bat_dis[k]
                    ==
                    load_forecasted.loc[k, 'data'] + 
                    p_bat_ch[k]
                    )        
        
        
        
        ''' ------------------------------------------------------------------------------- 
        EXECUTA O ALGORITMO DE OTIMIZAÇÃO
        --------------------------------------------------------------------------------'''
        print("\nEXECUTAR SOLVER\n")
        solution  = prob.solve(solver)
        fo_status = pl.LpStatus[solution]
        fo_value = pl.value(prob.objective)
        print("Status: {}".format(fo_status))
        print("Valor da FO: {}".format(fo_value))
        
        if not pl.LpStatus[solution] == 'Optimal':
            raise("Infactivel optimization problem")
        
        
        
        ''' ------------------------------------------------------------------------------- 
        SALVA OS DADOS DA OTIMIZAÇÃO
        --------------------------------------------------------------------------------'''
        # for k in range(0, Datas.NP_2TH):
        #     Datas.R_3th.loc[k , 'p_bat_sch']  = p_bat_dis[k].varValue - p_bat_ch[k].varValue
        #     Datas.R_3th.loc[k , 'k_pv_sch']   = k_pv[k].varvalue
        results_3th = None
        fo_value = None
        if pl.LpStatus[solution] == 'Optimal':
            print("OTIMO")
            # Results
            results_3th = pd.DataFrame(index=range(Datas.NP_2TH), columns=['p_bat_sch', 'k_pv_sch', 'soc_bat'])
            for k in range(0, Datas.NP_2TH):
                results_3th.loc[k, 'p_bat_sch']   = p_bat_dis[k].varValue - p_bat_ch[k].varValue
                results_3th.loc[k, 'k_pv_sch']    = k_pv[k].varValue
                # results_3th.loc[0, 'p_grid_sch']  = p_grid.value[k]
                results_3th.loc[k, 'soc_bat']    = soc_bat[k].varValue
        else:
            print("ENGASGOU")

        return results_3th, fo_value
