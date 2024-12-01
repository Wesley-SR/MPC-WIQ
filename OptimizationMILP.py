# -*- coding: utf-8 -*-
'''============================================================================
                               PROJETO V2G
#==========================================================================='''

import pulp as pl
import pandas as pd
from datas import Datas
from typing import Type

class OptimizationMILP():

    ''' ------------------------------------------------------------------------------- 
    isolated Optimization 3th
    --------------------------------------------------------------------------------'''
    @staticmethod
    def isolated_optimization_3th(Datas: Datas, pv_forecasted: pd.DataFrame, load_forecasted: pd.DataFrame) -> tuple:
        print("isolated Optimization in 3th")
        
        WEIGHT_K_PV      = 1
        WEIGHT_VAR_P_BAT = 1
        WEIGHT_VAR_P_BAT = 1
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
        flag_ch_bat  = pl.LpVariable.dicts('flag_ch_bat',   range(Datas.NP_3TH),cat='Binary')
        flag_dis_bat = pl.LpVariable.dicts('flag_dis_bat',  range(Datas.NP_3TH),cat='Binary')
        soc_bat          = pl.LpVariable.dicts('soc_bat',           range(Datas.NP_3TH),lowBound=Datas.SOC_BAT_MIN, upBound=Datas.SOC_BAT_MAX,cat='Continuous')
        
        # Battery power variation module
        # Charg
        abs_var_p_bat_ch_a      = pl.LpVariable.dicts('abs_var_p_bat_ch_a',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        abs_var_p_bat_ch_b      = pl.LpVariable.dicts('abs_var_p_bat_ch_b',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        flag_abs_var_p_bat_ch_a = pl.LpVariable.dicts('flag_abs_var_p_bat_ch_a', range(Datas.NP_3TH), cat='Binary')
        flag_abs_var_p_bat_ch_b = pl.LpVariable.dicts('flag_abs_var_p_bat_ch_b', range(Datas.NP_3TH), cat='Binary')
        # Discharge
        abs_var_p_bat_dis_a      = pl.LpVariable.dicts('abs_var_p_bat_dis_a',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        abs_var_p_bat_dis_b      = pl.LpVariable.dicts('abs_var_p_bat_dis_b',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        flag_abs_var_p_bat_dis_a = pl.LpVariable.dicts('flag_abs_var_p_bat_dis_a', range(Datas.NP_3TH), cat='Binary')
        flag_abs_var_p_bat_dis_b = pl.LpVariable.dicts('flag_abs_var_p_bat_dis_b', range(Datas.NP_3TH), cat='Binary')
        
        # Battery absolute values
        abs_error_ref_soc_bat_a      = pl.LpVariable.dicts('abs_error_ref_soc_bat_a',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_BAT_MAX, cat='Continuous')
        abs_error_ref_soc_bat_b      = pl.LpVariable.dicts('abs_error_ref_soc_bat_b',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_BAT_MAX, cat='Continuous')
        flag_abs_error_ref_soc_bat_a = pl.LpVariable.dicts('flag_abs_error_ref_soc_bat_a', range(Datas.NP_3TH), cat='Binary')
        flag_abs_error_ref_soc_bat_b = pl.LpVariable.dicts('flag_abs_error_ref_soc_bat_b', range(Datas.NP_3TH), cat='Binary')
        
        # Photovoltaic Panel
        k_pv              = pl.LpVariable.dicts('k_pv',          range(Datas.NP_3TH), lowBound=0, upBound=1, cat='Continuous')
        abs_error_ref_k_pv_a      = pl.LpVariable.dicts('abs_error_ref_k_pv_a',      range(Datas.NP_3TH), lowBound=0, upBound=1, cat='Continuous')
        abs_error_ref_k_pv_b      = pl.LpVariable.dicts('abs_error_ref_k_pv_b',      range(Datas.NP_3TH), lowBound=0, upBound=1, cat='Continuous')
        flag_abs_error_ref_k_pv_a = pl.LpVariable.dicts('flag_abs_error_ref_k_pv_a', range(Datas.NP_3TH), cat='Binary')
        flag_abs_error_ref_k_pv_b = pl.LpVariable.dicts('flag_abs_error_ref_k_pv_b', range(Datas.NP_3TH), cat='Binary')


        ''' ------------------------- FUNÇÃO OBJETIVO ------------------------------'''
        J_pv_3th          = pl.lpSum([(abs_error_ref_k_pv_a[k] + abs_error_ref_k_pv_b[k]) for k in range(Datas.NP_3TH)])
        
        J_bat_var_ch  = pl.lpSum([(abs_var_p_bat_ch_a[k] + abs_var_p_bat_ch_b[k])] for k in range(Datas.NP_3TH))
        
        J_bat_var_dis = pl.lpSum([(abs_var_p_bat_dis_a[k] + abs_var_p_bat_dis_b[k])] for k in range(Datas.NP_3TH))
        
        J_bat_var_soc = pl.lpSum([(abs_error_ref_soc_bat_a[k] + abs_error_ref_soc_bat_b[k])] for k in range(Datas.NP_3TH))
        
        # TODO: Dividir pelo máximo da parcela (Deve passar por normalização)
        objective_function = ( (WEIGHT_K_PV      * J_pv_3th      / 1)
                             + (WEIGHT_VAR_P_BAT * J_bat_var_ch  / 2)
                             + (WEIGHT_VAR_P_BAT * J_bat_var_dis / 2)
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
            prob += p_bat_ch[k]  <= Datas.P_BAT_MAX * flag_ch_bat[k]
            prob += p_bat_dis[k] <= Datas.P_BAT_MAX * flag_dis_bat[k]
            prob += flag_ch_bat[k] + flag_dis_bat[k] <= 1 # simultaneity      
            
            # Absolute value for battery power variation
            if k == 0:
                if Datas.p_bat >= 0:
                   prob += abs_var_p_bat_ch_a[k] - abs_var_p_bat_ch_b[k] == p_bat_ch[k] - 0
                   prob += abs_var_p_bat_dis_a[k] - abs_var_p_bat_dis_b[k] == p_bat_dis[k] - Datas.p_bat
                else:
                   prob += abs_var_p_bat_ch_a[k] - abs_var_p_bat_ch_b[k] == p_bat_ch[k] - (-Datas.p_bat)
                   prob += abs_var_p_bat_dis_a[k] - abs_var_p_bat_dis_b[k] == p_bat_dis[k] - 0
            else:
                prob += abs_var_p_bat_ch_a[k] - abs_var_p_bat_ch_b[k] == p_bat_ch[k] - p_bat_ch[k-1]
                prob += abs_var_p_bat_dis_a[k] - abs_var_p_bat_dis_b[k] == p_bat_dis[k] - p_bat_dis[k-1]
            
            prob += abs_var_p_bat_ch_a[k] <= flag_abs_var_p_bat_ch_a[k] * Datas.P_BAT_VAR_MAX
            prob += abs_var_p_bat_ch_b[k] <= flag_abs_var_p_bat_ch_b[k] * Datas.P_BAT_VAR_MAX
            prob += flag_abs_var_p_bat_ch_a[k] + flag_abs_var_p_bat_ch_b[k] <= 1 # simultaneity
            prob += abs_var_p_bat_dis_a[k] <= flag_abs_var_p_bat_dis_a[k] * Datas.P_BAT_VAR_MAX
            prob += abs_var_p_bat_dis_b[k] <= flag_abs_var_p_bat_dis_b[k] * Datas.P_BAT_VAR_MAX
            prob += flag_abs_var_p_bat_dis_a[k] + flag_abs_var_p_bat_dis_b[k] <= 1 # simultaneity

            # Battery SOC
            if k > 0:
                prob += soc_bat[k] == soc_bat[k-1] - (p_bat_dis[k-1] - p_bat_ch[k-1])*(Datas.TS_3TH/60/60)/Datas.Q_BAT
            else:
                prob += soc_bat[k] == Datas.soc_bat

            # Absolute value between SOC and SOC_ref
            prob += abs_error_ref_soc_bat_a[k] - abs_error_ref_soc_bat_b[k] == soc_bat[k] - Datas.SOC_BAT_REF
            prob += abs_error_ref_soc_bat_a[k] <= flag_abs_error_ref_soc_bat_a
            prob += abs_error_ref_soc_bat_b[k] <= flag_abs_error_ref_soc_bat_b
            prob += flag_abs_error_ref_soc_bat_a[k] + flag_abs_error_ref_soc_bat_b[k] <= 1 # simultaneity

            # Absolute value between k_pv and K_PV_REF
            prob += abs_error_ref_k_pv_a[k] - abs_error_ref_k_pv_b[k] == k_pv[k] - Datas.K_PV_REF
            prob += abs_error_ref_k_pv_a[k] <= flag_abs_error_ref_k_pv_a
            prob += abs_error_ref_k_pv_b[k] <= flag_abs_error_ref_k_pv_b
            prob += flag_abs_error_ref_k_pv_a[k] + flag_abs_error_ref_k_pv_b[k] <= 1 # simultaneity
            
            
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
        print("EXECUTAR SOLVER")
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
            results_3th = pd.DataFrame(index=range(Datas.NP_3TH), columns=['p_bat_sch', 'k_pv_sch', 'p_grid_sch', 'soc_bat'])
            for k in range(0, Datas.NP_3TH):
                results_3th.loc[k, 'p_bat_sch']   = p_bat_dis[k].varValue - p_bat_ch[k].varValue
                results_3th.loc[k, 'k_pv_sch']    = k_pv[k].varValue
                results_3th.loc[0, 'p_grid_sch']  = 0
                results_3th.loc[k, 'soc_bat']    = soc_bat[k].varValue
        else:
            print("ENGASGOU")

        return results_3th, fo_value


    ''' ------------------------------------------------------------------------------- 
    isolated Optimization 2th
    --------------------------------------------------------------------------------'''
    @staticmethod
    def isolated_optimization_2th(Datas: Datas, pv_forecasted: pd.DataFrame, load_forecasted: pd.DataFrame) -> tuple:
        print("isolated Optimization in 2th")
        
        WEIGHT_K_PV = 1
        WEIGHT_VAR_P_BAT = 2
        WEIGHT_REF_P_BAT = 5
        WEIGHT_REF_SOC_SC = 1
        WEIGHT_VAR_P_SC = 0.00001
        
        ''' -------------------- Optimization Problem ---------------------------- '''
        prob = pl.LpProblem("OptimizationMILP", pl.LpMinimize) # LpMinimize e LpMaximize
        solver = pl.PULP_CBC_CMD(msg=False, timeLimit=1)
        # Solver Disponívels (gratuitos)
        # ['PULP_CBC_CMD', 'SCIP_CMD']

        ''' ------------------------- VARIÁVEIS DO PROBLEMA ----------------------- '''    
        # Battery power
        p_bat_dis        = pl.LpVariable.dicts('p_bat_dis',         range(Datas.NP_2TH),lowBound=0, upBound=Datas.P_BAT_MAX,cat='Continuous')
        p_bat_ch         = pl.LpVariable.dicts('p_bat_ch',          range(Datas.NP_2TH),lowBound=0, upBound=Datas.P_BAT_MAX,cat='Continuous')
        flag_ch_bat  = pl.LpVariable.dicts('flag_ch_bat',   range(Datas.NP_2TH),cat='Binary')
        flag_dis_bat = pl.LpVariable.dicts('flag_dis_bat',  range(Datas.NP_2TH),cat='Binary')
        soc_bat          = pl.LpVariable.dicts('soc_bat',           range(Datas.NP_2TH),lowBound=Datas.SOC_BAT_MIN, upBound=Datas.SOC_BAT_MAX,cat='Continuous')
        
        # Absolute valute for battery power variation module
        # Charge
        abs_var_p_bat_ch_a      = pl.LpVariable.dicts('abs_var_p_bat_ch_a',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        abs_var_p_bat_ch_b      = pl.LpVariable.dicts('abs_var_p_bat_ch_b',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        flag_abs_var_p_bat_ch_a = pl.LpVariable.dicts('flag_abs_var_p_bat_ch_a', range(Datas.NP_2TH), cat='Binary')
        flag_abs_var_p_bat_ch_b = pl.LpVariable.dicts('flag_abs_var_p_bat_ch_b', range(Datas.NP_2TH), cat='Binary')
        # Discharge
        abs_var_p_bat_dis_a      = pl.LpVariable.dicts('abs_var_p_bat_dis_a',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        abs_var_p_bat_dis_b      = pl.LpVariable.dicts('abs_var_p_bat_dis_b',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        flag_abs_var_p_bat_dis_a = pl.LpVariable.dicts('flag_abs_var_p_bat_dis_a', range(Datas.NP_2TH), cat='Binary')
        flag_abs_var_p_bat_dis_b = pl.LpVariable.dicts('flag_abs_var_p_bat_dis_b', range(Datas.NP_2TH), cat='Binary')
        
        # Absolute value for battery power reference
        # Charge
        abs_error_ref_p_bat_ch_a      = pl.LpVariable.dicts('abs_error_ref_p_bat_ch_a',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_MAX, cat='Continuous')
        abs_error_ref_p_bat_ch_b      = pl.LpVariable.dicts('abs_error_ref_p_bat_ch_b',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_MAX, cat='Continuous')
        flag_abs_error_ref_p_bat_ch_a = pl.LpVariable.dicts('flag_abs_error_ref_p_bat_ch_a', range(Datas.NP_2TH), cat='Binary')
        flag_abs_error_ref_p_bat_ch_b = pl.LpVariable.dicts('flag_abs_error_ref_p_bat_ch_b', range(Datas.NP_2TH), cat='Binary')
        # Discharge
        abs_error_ref_p_bat_dis_a      = pl.LpVariable.dicts('abs_error_ref_p_bat_dis_a',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_MAX, cat='Continuous')
        abs_error_ref_p_bat_dis_b      = pl.LpVariable.dicts('abs_error_ref_p_bat_dis_b',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_MAX, cat='Continuous')
        flag_abs_error_ref_p_bat_dis_a = pl.LpVariable.dicts('flag_abs_error_ref_p_bat_dis_a', range(Datas.NP_2TH), cat='Binary')
        flag_abs_error_ref_p_bat_dis_b = pl.LpVariable.dicts('flag_abs_error_ref_p_bat_dis_b', range(Datas.NP_2TH), cat='Binary')

        # SC power
        p_sc_dis = pl.LpVariable.dicts('p_sc_dis', range(Datas.NP_2TH),lowBound=0, upBound=Datas.P_BAT_MAX,cat='Continuous')
        p_sc_ch = pl.LpVariable.dicts('p_sc_ch', range(Datas.NP_2TH),lowBound=0, upBound=Datas.P_BAT_MAX,cat='Continuous')
        flag_ch_sc = pl.LpVariable.dicts('flag_ch_sc', range(Datas.NP_2TH),cat='Binary')
        flag_dis_sc = pl.LpVariable.dicts('flag_dis_sc', range(Datas.NP_2TH),cat='Binary')
        soc_sc = pl.LpVariable.dicts('soc_sc', range(Datas.NP_2TH),lowBound=Datas.SOC_BAT_MIN, upBound=Datas.SOC_BAT_MAX,cat='Continuous')
        
        # Absolute valute for battery power variation module
        # Charg
        abs_var_p_sc_ch_a = pl.LpVariable.dicts('abs_var_p_sc_ch_a', range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        abs_var_p_sc_ch_b = pl.LpVariable.dicts('abs_var_p_sc_ch_b', range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        flag_abs_var_p_sc_ch_a = pl.LpVariable.dicts('flag_abs_var_p_sc_ch_a', range(Datas.NP_2TH), cat='Binary')
        flag_abs_var_p_sc_ch_b = pl.LpVariable.dicts('flag_abs_var_p_sc_ch_b', range(Datas.NP_2TH), cat='Binary')
        # Discharge
        abs_var_p_sc_dis_a = pl.LpVariable.dicts('abs_var_p_sc_dis_a', range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        abs_var_p_sc_dis_b = pl.LpVariable.dicts('abs_var_p_sc_dis_b', range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_VAR_MAX, cat='Continuous')
        flag_abs_var_p_sc_dis_a = pl.LpVariable.dicts('flag_abs_var_p_sc_dis_a', range(Datas.NP_2TH), cat='Binary')
        flag_abs_var_p_sc_dis_b = pl.LpVariable.dicts('flag_abs_var_p_sc_dis_b', range(Datas.NP_2TH), cat='Binary')
        
        # Absolute value for battery power reference
        # Charge
        abs_error_ref_soc_sc_a = pl.LpVariable.dicts('abs_error_ref_soc_sc_a', range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_MAX, cat='Continuous')
        abs_error_ref_soc_sc_b = pl.LpVariable.dicts('abs_error_ref_soc_sc_b', range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_MAX, cat='Continuous')
        flag_abs_error_ref_soc_sc_a = pl.LpVariable.dicts('flag_abs_error_ref_soc_sc_a', range(Datas.NP_2TH), cat='Binary')
        flag_abs_error_ref_soc_sc_b = pl.LpVariable.dicts('flag_abs_error_ref_soc_sc_b', range(Datas.NP_2TH), cat='Binary')
               
        # Photovoltaic Panel
        k_pv                    = pl.LpVariable.dicts('k_pv',          range(Datas.NP_2TH), lowBound=0, upBound=1, cat='Continuous')
        abs_error_ref_k_pv_a      = pl.LpVariable.dicts('abs_error_ref_k_pv_a',      range(Datas.NP_2TH), lowBound=0, upBound=1, cat='Continuous')
        abs_error_ref_k_pv_b      = pl.LpVariable.dicts('abs_error_ref_k_pv_b',      range(Datas.NP_2TH), lowBound=0, upBound=1, cat='Continuous')
        flag_abs_error_ref_k_pv_a = pl.LpVariable.dicts('flag_abs_error_ref_k_pv_a', range(Datas.NP_2TH), cat='Binary')
        flag_abs_error_ref_k_pv_b = pl.LpVariable.dicts('flag_abs_error_ref_k_pv_b', range(Datas.NP_2TH), cat='Binary')

        ''' ------------------------- FUNÇÃO OBJETIVO ------------------------------'''
        # We created each party of the OF separately. Then we put them all together.
        J_pv_3th      = pl.lpSum([(abs_error_ref_k_pv_a[k] + abs_error_ref_k_pv_b[k]) for k in range(Datas.NP_2TH)])
        
        J_bat_var_ch  = pl.lpSum([(abs_var_p_bat_ch_a[k] + abs_var_p_bat_ch_b[k])] for k in range(Datas.NP_2TH))
        
        J_bat_var_dis = pl.lpSum([(abs_var_p_bat_dis_a[k] + abs_var_p_bat_dis_b[k])] for k in range(Datas.NP_2TH))
        
        J_bat_ref_p_bat_ch = pl.lpSum([(abs_error_ref_p_bat_ch_a[k] + abs_error_ref_p_bat_ch_b[k])] for k in range(Datas.NP_2TH))
        
        J_bat_ref_p_bat_dis = pl.lpSum([(abs_error_ref_p_bat_dis_a[k] + abs_error_ref_p_bat_dis_b[k])] for k in range(Datas.NP_2TH))
        
        J_sc_ref_soc = pl.lpSum([(abs_error_ref_soc_sc_a[k] + abs_error_ref_soc_sc_b[k])] for k in range(Datas.NP_2TH))
        
        J_sc_var_ch = pl.lpSum([(abs_var_p_sc_ch_a[k] + abs_var_p_sc_ch_b[k])] for k in range(Datas.NP_2TH))
        
        J_sc_var_dis = pl.lpSum([(abs_var_p_sc_dis_a[k] + abs_var_p_sc_dis_b[k])] for k in range(Datas.NP_2TH))
        
        # TODO: Dividir pelo máximo da parcela (Deve passar por normalização)
        objective_function = ( (WEIGHT_K_PV * J_pv_3th / 1)
                             + (WEIGHT_VAR_P_BAT * (J_bat_var_ch + J_bat_var_dis) / 1)
                             + (WEIGHT_REF_P_BAT * (J_bat_ref_p_bat_ch + J_bat_ref_p_bat_dis) / 1)
                             + (WEIGHT_REF_SOC_SC * J_sc_ref_soc / 1)   
                             + (WEIGHT_VAR_P_SC * (J_sc_var_ch + J_sc_var_dis) / 1)
                             )
        prob.setObjective(objective_function)
        
        
        
        ''' --------------------------- RESTRIÇÕES -------------------------------- '''
        '''
            No código, k = 0, é o mesmo que X(t+k|t) para k = 1, do texto.
            
            k=0 é o atual
        '''  
        for k in range(0, Datas.NP_2TH):
            
            # P_bat
            prob += p_bat_ch[k] <= Datas.P_BAT_MAX * flag_ch_bat[k]
            prob += p_bat_dis[k] <= Datas.P_BAT_MAX * flag_dis_bat[k]
            prob += flag_ch_bat[k] + flag_dis_bat[k] <= 1 # simultaneity      
            
            # p_sc
            prob += p_sc_ch[k] <= Datas.P_SC_MAX * flag_ch_sc[k]
            prob += p_sc_dis[k] <= Datas.P_SC_MAX * flag_dis_sc[k]
            prob += flag_ch_sc[k] + flag_dis_sc[k] <= 1 # simultaneity
            
            if k == 0:
                # SOC bat
                prob += soc_bat[k] == Datas.soc_bat
                # var p_bat
                if Datas.p_bat >= 0:
                   prob += abs_var_p_bat_ch_a[k] - abs_var_p_bat_ch_b[k] == (p_bat_ch[k] - 0)
                   prob += abs_var_p_bat_dis_a[k] - abs_var_p_bat_dis_b[k] == p_bat_dis[k] - Datas.p_bat
                else:
                   prob += abs_var_p_bat_ch_a[k] - abs_var_p_bat_ch_b[k] == p_bat_ch[k] - (-Datas.p_bat)
                   prob += abs_var_p_bat_dis_a[k] - abs_var_p_bat_dis_b[k] == p_bat_dis[k] - 0
                # SOC sc
                prob += soc_sc[k] == Datas.soc_sc
                # var p_sc
                if Datas.p_sc >= 0:
                    prob += abs_var_p_sc_ch_a[k] - abs_var_p_sc_ch_b == p_sc_ch[k] - 0
                    prob += abs_var_p_sc_dis_a[k] - abs_var_p_sc_dis_b == p_sc_dis[k] - Datas.p_sc
                else:
                    prob += abs_var_p_sc_ch_a[k] - abs_var_p_sc_ch_b == p_sc_ch[k] - (-Datas.p_sc)
                    prob += abs_var_p_sc_dis_a[k] - abs_var_p_sc_dis_b == p_sc_dis[k] - 0
            else:
                # SOC bat
                prob += soc_bat[k] == soc_bat[k-1] - (p_bat_dis[k-1] - p_bat_ch[k-1])*Datas.TS_2TH/Datas.Q_BAT
                # var p_bat
                prob += abs_var_p_bat_ch_a[k] - abs_var_p_bat_ch_b[k] == p_bat_ch[k] - p_bat_ch[k-10] # + (abs_var_p_bat_ch_a[k-1] - abs_var_p_bat_ch_b[k-1]) # Como penalizar a variacao
                prob += abs_var_p_bat_dis_a[k] - abs_var_p_bat_dis_b[k] == p_bat_dis[k] - p_bat_dis[k-1] # + (abs_var_p_bat_dis_a[k] - abs_var_p_bat_dis_b[k])
                # SOC sc
                prob += soc_sc[k] == soc_sc[k-1] - (p_sc_dis[k-1] - p_sc_ch[k-1])*Datas.TS_2TH/Datas.Q_SC
                # vat p_sc
                prob += abs_var_p_sc_ch_a[k] - abs_var_p_sc_ch_b[k] == p_sc_ch[k] - p_bat_ch[k-1]
                prob += abs_var_p_sc_dis_a[k] - abs_var_p_sc_dis_b[k] == p_sc_dis[k] - p_bat_dis[k-1]
                
            # Absolute value for p_bat
            prob += abs_var_p_bat_ch_a[k] <= flag_abs_var_p_bat_ch_a[k] * Datas.P_BAT_VAR_MAX
            prob += abs_var_p_bat_ch_b[k] <= flag_abs_var_p_bat_ch_b[k] * Datas.P_BAT_VAR_MAX
            prob += flag_abs_var_p_bat_ch_a[k] + flag_abs_var_p_bat_ch_b[k] <= 1 # simultaneity
            prob += abs_var_p_bat_dis_a[k] <= flag_abs_var_p_bat_dis_a[k] * Datas.P_BAT_VAR_MAX
            prob += abs_var_p_bat_dis_b[k] <= flag_abs_var_p_bat_dis_b[k] * Datas.P_BAT_VAR_MAX
            prob += flag_abs_var_p_bat_dis_a[k] + flag_abs_var_p_bat_dis_b[k] <= 1 # simultaneity

            # Absolute value between p_bat and p_bat_sch
            # Charge
            prob += abs_error_ref_p_bat_ch_a[k] - abs_error_ref_p_bat_ch_b[k] == p_bat_ch[k] - Datas.p_bat_ch_sch
            prob += abs_error_ref_p_bat_ch_a[k] <= flag_abs_error_ref_p_bat_ch_a
            prob += abs_error_ref_p_bat_ch_b[k] <= flag_abs_error_ref_p_bat_ch_b
            prob += flag_abs_error_ref_p_bat_ch_a[k] + flag_abs_error_ref_p_bat_ch_b[k] <= 1 # simultaneity
            # Discharge
            prob += abs_error_ref_p_bat_dis_a[k] - abs_error_ref_p_bat_dis_b[k] == p_bat_dis[k] - Datas.p_bat_dis_sch
            prob += abs_error_ref_p_bat_dis_a[k] <= flag_abs_error_ref_p_bat_dis_a
            prob += abs_error_ref_p_bat_dis_b[k] <= flag_abs_error_ref_p_bat_dis_b
            prob += flag_abs_error_ref_p_bat_dis_a[k] + flag_abs_error_ref_p_bat_dis_b[k] <= 1 # simultaneity

            # Absolute value between k_pv and K_PV_REF
            prob += abs_error_ref_k_pv_a[k] - abs_error_ref_k_pv_b[k] == k_pv[k] - Datas.k_pv_sch
            prob += abs_error_ref_k_pv_a[k] <= flag_abs_error_ref_k_pv_a
            prob += abs_error_ref_k_pv_b[k] <= flag_abs_error_ref_k_pv_b
            prob += flag_abs_error_ref_k_pv_a[k] + flag_abs_error_ref_k_pv_b[k] <= 1 # simultaneity
            
            # Absolute value for p_sc
            prob += abs_var_p_sc_ch_a[k] <= flag_abs_var_p_sc_ch_a[k] * Datas.P_SC_VAR_MAX
            prob += abs_var_p_sc_ch_b[k] <= flag_abs_var_p_sc_ch_b[k] * Datas.P_SC_VAR_MAX
            prob += flag_abs_var_p_sc_ch_a[k] + flag_abs_var_p_sc_ch_b[k] <= 1 # simultaneity
            prob += abs_var_p_sc_dis_a[k] <= flag_abs_var_p_sc_dis_a[k] * Datas.P_SC_VAR_MAX
            prob += abs_var_p_sc_dis_b[k] <= flag_abs_var_p_sc_dis_b[k] * Datas.P_SC_VAR_MAX
            prob += flag_abs_var_p_sc_dis_a[k] + flag_abs_var_p_sc_dis_b[k] <= 1 # simultaneity
            
            # Absolute value between SOC and SOC_ref
            prob += abs_error_ref_soc_sc_a[k] - abs_error_ref_soc_sc_b[k] == soc_sc[k] - Datas.SOC_SC_REF
            prob += abs_error_ref_soc_sc_a[k] <= flag_abs_error_ref_soc_sc_a
            prob += abs_error_ref_soc_sc_b[k] <= flag_abs_error_ref_soc_sc_b
            prob += flag_abs_error_ref_soc_sc_a[k] + flag_abs_error_ref_soc_sc_b[k] <= 1 # simultaneity
            
            # BALANÇO DE POTÊNCIA NO BARRAMENTO DC
            prob += (
                    k_pv[k]*pv_forecasted.loc[k, 'data'] + 
                    p_bat_dis[k] +
                    p_sc_dis[k]
                    ==
                    load_forecasted.loc[k, 'data'] + 
                    p_bat_ch[k] +
                    p_bat_ch[k]
                    )
        
        ''' ------------------------------------------------------------------------------- 
        EXECUTA O ALGORITMO DE OTIMIZAÇÃO
        --------------------------------------------------------------------------------'''
        print("EXECUTAR SOLVER 2th")
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
        # TODO: Save the test round by concatenating it with the previous
        # for k in range(0, Datas.NP_2TH):
        #     Datas.R_2th.loc[k , 'p_bat_ref']  = p_bat_dis[k].varValue - p_bat_ch[k].varValue
        #     Datas.R_2th.loc[k , 'k_pv_ref']   = k_pv[k].varvalue
        results_2th = None
        if pl.LpStatus[solution] == 'Optimal':
            print("OTIMO")
            # Results
            results_2th = pd.DataFrame(index=range(Datas.NP_2TH), columns=['p_bat_ref', 'k_pv_ref', 'p_grid_ref', 'p_sc_ref', 'soc_bat', 'soc_sc'])
            for k in range(0, Datas.NP_2TH):
                # This values are for inverters reference
                results_2th.loc[k, 'p_bat_ref'] = p_bat_dis[k].varValue - p_bat_ch[k].varValue
                results_2th.loc[k, 'k_pv_ref'] = k_pv[k].varValue
                results_2th.loc[k, 'p_grid_ref']  = 0
                results_2th.loc[k, 'p_sc_ref'] = p_sc_dis[k].varValue - p_sc_ch[k].varValue
                
                # These values are for analysis only
                results_2th.loc[k, 'soc_bat'] = soc_bat[k].varValue
                results_2th.loc[k, 'soc_sc'] = soc_sc[k].varValue
                # Verifica se existe algum NaN
            existe_nan = results_2th.isna().any().any()
            if existe_nan:
                print(f"Error. NaN in results_2th")  # True se houver NaN, False caso contrário
                print(results_2th)
        else:
            print("Error. ENGASGOU in isolated_optimization_2th")

        return results_2th, fo_value
