# -*- coding: utf-8 -*-
'''============================================================================
                   EMS - CONTROLE TERCIÁRIO E SECUNDÁRIO
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
    def optimization_3th(Datas: Datas, pv_forecasted: pd.DataFrame, load_forecasted: pd.DataFrame, connected_mode: bool) -> tuple:
        print("isolated Optimization in 3th")
        
        # 3TH - 3TH - 3TH - 3TH - 3TH - 3TH - 3TH - 3TH - 3TH - 3TH
        if connected_mode is True:
            WEIGHT_REF_K_PV  = 1
            WEIGHT_VAR_P_BAT = 1
            MULTIPLIER_J_VAR_BAT = 75
            WEIGHT_REF_SOC_BAT   = 1
            WEIGHT_VAR_P_GRID = 0.01
            WEIGHT_REF_P_GRID = 1.5
        else: 
            WEIGHT_REF_K_PV   = 1
            WEIGHT_VAR_P_BAT  = 1
            MULTIPLIER_J_VAR_BAT = 75
            WEIGHT_REF_SOC_BAT    = 5
            
        
        ''' -------------------- Optimization Problem ---------------------------- '''
        prob   = pl.LpProblem("OptimizationMILP", pl.LpMinimize) # LpMinimize e LpMaximize
        solver = pl.PULP_CBC_CMD(msg=False, timeLimit=60*1)
        # Solver Disponívels (gratuitos)
        # ['PULP_CBC_CMD', 'SCIP_CMD']

        ''' ------------------------- VARIÁVEIS DO PROBLEMA ----------------------- '''    
        # Battery power
        p_bat_dis    = pl.LpVariable.dicts('p_bat_dis',         range(Datas.NP_3TH),lowBound=0, upBound=Datas.P_BAT_MAX,cat='Continuous')
        p_bat_ch     = pl.LpVariable.dicts('p_bat_ch',          range(Datas.NP_3TH),lowBound=0, upBound=Datas.P_BAT_MAX,cat='Continuous')
        flag_ch_bat  = pl.LpVariable.dicts('flag_ch_bat',   range(Datas.NP_3TH),cat='Binary')
        flag_dis_bat = pl.LpVariable.dicts('flag_dis_bat',  range(Datas.NP_3TH),cat='Binary')
        soc_bat      = pl.LpVariable.dicts('soc_bat',           range(Datas.NP_3TH),lowBound=Datas.SOC_BAT_MIN, upBound=Datas.SOC_BAT_MAX,cat='Continuous')
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
        abs_ref_soc_bat_a      = pl.LpVariable.dicts('abs_ref_soc_bat_a',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.SOC_BAT_MAX-Datas.SOC_BAT_MIN, cat='Continuous')
        abs_ref_soc_bat_b      = pl.LpVariable.dicts('abs_ref_soc_bat_b',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.SOC_BAT_MAX-Datas.SOC_BAT_MIN, cat='Continuous')
        flag_abs_ref_soc_bat_a = pl.LpVariable.dicts('flag_abs_ref_soc_bat_a', range(Datas.NP_3TH), cat='Binary')
        flag_abs_ref_soc_bat_b = pl.LpVariable.dicts('flag_abs_ref_soc_bat_b', range(Datas.NP_3TH), cat='Binary')
        # Penalidade variacao bateria, Big-M
        flag_bigM_bat = pl.LpVariable.dicts('flag_d_bat', range(Datas.NP_3TH), cat='Binary')
        L_k_bat = -1000
        U_k_bat = 1000
        Epsolon_bat = 0.0001
        max_var_bat_bigM = 0.25
        
        # Photovoltaic Panel
        k_pv              = pl.LpVariable.dicts('k_pv',          range(Datas.NP_3TH), lowBound=0, upBound=1, cat='Continuous')
        abs_ref_k_pv_a      = pl.LpVariable.dicts('abs_ref_k_pv_a',      range(Datas.NP_3TH), lowBound=0, upBound=1, cat='Continuous')
        abs_ref_k_pv_b      = pl.LpVariable.dicts('abs_ref_k_pv_b',      range(Datas.NP_3TH), lowBound=0, upBound=1, cat='Continuous')
        flag_abs_ref_k_pv_a = pl.LpVariable.dicts('flag_abs_ref_k_pv_a', range(Datas.NP_3TH), cat='Binary')
        flag_abs_ref_k_pv_b = pl.LpVariable.dicts('flag_abs_ref_k_pv_b', range(Datas.NP_3TH), cat='Binary')
        
        # Main Grid
        if connected_mode is True:
            print("********** MODO CONECTADO ************")
            # p_imp
            p_grid_imp    = pl.LpVariable.dicts('p_grid_imp',         range(Datas.NP_3TH),lowBound=0, upBound=Datas.P_GRID_MAX,cat='Continuous')
            flag_p_grid_imp  = pl.LpVariable.dicts('flag_p_grid_imp',   range(Datas.NP_3TH),cat='Binary')
            # p_exp
            p_grid_exp    = pl.LpVariable.dicts('p_grid_exp',         range(Datas.NP_3TH),lowBound=0, upBound=Datas.P_GRID_MAX,cat='Continuous')
            flag_p_grid_exp  = pl.LpVariable.dicts('flag_p_grid_exp',   range(Datas.NP_3TH),cat='Binary')
            # Import variation
            abs_var_p_grid_imp_a      = pl.LpVariable.dicts('abs_var_p_grid_imp_a',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_GRID_VAR_MAX, cat='Continuous')
            abs_var_p_grid_imp_b      = pl.LpVariable.dicts('abs_var_p_grid_imp_b',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_GRID_VAR_MAX, cat='Continuous')
            flag_abs_var_p_grid_imp_a = pl.LpVariable.dicts('flag_abs_var_p_grid_imp_a', range(Datas.NP_3TH), cat='Binary')
            flag_abs_var_p_grid_imp_b = pl.LpVariable.dicts('flag_abs_var_p_grid_imp_b', range(Datas.NP_3TH), cat='Binary')
            # Export variation
            abs_var_p_grid_exp_a      = pl.LpVariable.dicts('abs_var_p_grid_exp_a',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_GRID_VAR_MAX, cat='Continuous')
            abs_var_p_grid_exp_b      = pl.LpVariable.dicts('abs_var_p_grid_exp_b',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_GRID_VAR_MAX, cat='Continuous')
            flag_abs_var_p_grid_exp_a = pl.LpVariable.dicts('flag_abs_var_p_grid_exp_a', range(Datas.NP_3TH), cat='Binary')
            flag_abs_var_p_grid_exp_b = pl.LpVariable.dicts('flag_abs_var_p_grid_exp_b', range(Datas.NP_3TH), cat='Binary')
            # Export reference
            abs_ref_p_grid_exp_a      = pl.LpVariable.dicts('abs_ref_p_grid_exp_a',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_GRID_MAX, cat='Continuous')
            abs_ref_p_grid_exp_b      = pl.LpVariable.dicts('abs_ref_p_grid_exp_b',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_GRID_MAX, cat='Continuous')
            flag_abs_ref_p_grid_exp_a = pl.LpVariable.dicts('flag_abs_ref_p_grid_exp_a', range(Datas.NP_3TH), cat='Binary')
            flag_abs_ref_p_grid_exp_b = pl.LpVariable.dicts('flag_abs_ref_p_grid_exp_b', range(Datas.NP_3TH), cat='Binary')
            # Import reference
            abs_ref_p_grid_imp_a      = pl.LpVariable.dicts('abs_ref_p_grid_imp_a',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_GRID_MAX, cat='Continuous')
            abs_ref_p_grid_imp_b      = pl.LpVariable.dicts('abs_ref_p_grid_imp_b',      range(Datas.NP_3TH), lowBound=0, upBound=Datas.P_GRID_MAX, cat='Continuous')
            flag_abs_ref_p_grid_imp_a = pl.LpVariable.dicts('flag_abs_ref_p_grid_imp_a', range(Datas.NP_3TH), cat='Binary')
            flag_abs_ref_p_grid_imp_b = pl.LpVariable.dicts('flag_abs_ref_p_grid_imp_b', range(Datas.NP_3TH), cat='Binary')


        ''' ------------------------- FUNÇÃO OBJETIVO ------------------------------'''
        # Specific Objects
        J_k_pv_ref     = pl.lpSum([(abs_ref_k_pv_a[k] + abs_ref_k_pv_b[k]) for k in range(Datas.NP_3TH)])
        
        J_bat_var_ch  = pl.lpSum([(abs_var_p_bat_ch_a[k] + abs_var_p_bat_ch_b[k] + flag_bigM_bat[k]*MULTIPLIER_J_VAR_BAT)] for k in range(Datas.NP_3TH))
        
        J_bat_var_dis = pl.lpSum([(abs_var_p_bat_dis_a[k] + abs_var_p_bat_dis_b[k] + flag_bigM_bat[k]*MULTIPLIER_J_VAR_BAT)] for k in range(Datas.NP_3TH))
        
        J_bat_ref_soc = pl.lpSum([(abs_ref_soc_bat_a[k] + abs_ref_soc_bat_b[k])] for k in range(Datas.NP_3TH))
        
        if connected_mode is True:
            # Grid ref
            J_grid_ref_imp = pl.lpSum([(abs_ref_p_grid_imp_a[k] + abs_ref_p_grid_imp_b[k])] for k in range(Datas.NP_2TH))
            J_grid_ref_exp = pl.lpSum([(abs_ref_p_grid_exp_a[k] + abs_ref_p_grid_exp_b[k])] for k in range(Datas.NP_2TH))
            # Grid var
            J_grid_var_imp  = pl.lpSum([(abs_var_p_grid_imp_a[k] + abs_var_p_grid_imp_b[k])] for k in range(Datas.NP_3TH))
            J_grid_var_exp = pl.lpSum([(abs_var_p_grid_exp_a[k] + abs_var_p_grid_exp_b[k])] for k in range(Datas.NP_3TH))
        
        # Objective Function
        if connected_mode is True:
            objective_function = ( (WEIGHT_REF_K_PV  * J_k_pv_ref)
                                + (WEIGHT_VAR_P_BAT  * (J_bat_var_ch + J_bat_var_dis))
                                + (WEIGHT_REF_SOC_BAT    * J_bat_ref_soc)
                                + (WEIGHT_VAR_P_GRID * (J_grid_var_exp + J_grid_var_imp))
                                + (WEIGHT_REF_P_GRID * (J_grid_ref_exp + J_grid_ref_imp))
                                )
        else:
            # TODO: Dividir pelo máximo da parcela (Deve passar por normalização)
            objective_function = ( (WEIGHT_REF_K_PV * J_k_pv_ref)
                                + (WEIGHT_VAR_P_BAT * (J_bat_var_ch + J_bat_var_dis))
                                + (WEIGHT_REF_SOC_BAT   * J_bat_ref_soc / 1)
                                )
            
        prob.setObjective(objective_function)
        
        
        
        ''' --------------------------- RESTRIÇÕES -------------------------------- '''
        '''
            No código, k = 0, é o mesmo que X(t+k|t) para k = 1, do texto.
            
            k=0 é o atual
        '''  
        for k in range(0, Datas.NP_3TH):
            # ------------ Operational Constraints ------------
            # BATTERY
            # P_bat
            prob += p_bat_ch[k]  <= flag_ch_bat[k] * Datas.P_BAT_MAX
            prob += p_bat_dis[k] <= flag_dis_bat[k] * Datas.P_BAT_MAX
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
            if k == 0:
                prob += soc_bat[k] == Datas.soc_bat
            else:
                prob += soc_bat[k] == soc_bat[k-1] - (p_bat_dis[k-1] - p_bat_ch[k-1])*(Datas.TS_3TH/60/60)/Datas.Q_BAT
            # flag_bigM_bat   L_k_bat     U_k_bat    Epsolon_bat    max_var_bat_bigM
            prob += (abs_var_p_bat_ch_a[k] + abs_var_p_bat_ch_b[k] + abs_var_p_bat_dis_a[k] + abs_var_p_bat_dis_b[k]) - max_var_bat_bigM >= L_k_bat * (1 - flag_bigM_bat[k])
            prob += (abs_var_p_bat_ch_a[k] + abs_var_p_bat_ch_b[k] + abs_var_p_bat_dis_a[k] + abs_var_p_bat_dis_b[k]) - max_var_bat_bigM <= (U_k_bat + Epsolon_bat)*flag_bigM_bat[k] - Epsolon_bat
                
            # Absolute value between SOC and SOC_ref
            prob += abs_ref_soc_bat_a[k] - abs_ref_soc_bat_b[k] == soc_bat[k] - Datas.SOC_BAT_REF
            prob += abs_ref_soc_bat_a[k] <= flag_abs_ref_soc_bat_a[k]
            prob += abs_ref_soc_bat_b[k] <= flag_abs_ref_soc_bat_b[k]
            prob += flag_abs_ref_soc_bat_a[k] + flag_abs_ref_soc_bat_b[k] <= 1 # simultaneity

            # k_pv
            # Absolute value between k_pv and K_PV_REF
            prob += abs_ref_k_pv_a[k] - abs_ref_k_pv_b[k] == k_pv[k] - Datas.K_PV_REF
            prob += abs_ref_k_pv_a[k] <= flag_abs_ref_k_pv_a[k]
            prob += abs_ref_k_pv_b[k] <= flag_abs_ref_k_pv_b[k]
            prob += flag_abs_ref_k_pv_a[k] + flag_abs_ref_k_pv_b[k] <= 1 # simultaneity
            
            # Main Grid
            if connected_mode is True:
                # p_grid
                prob += p_grid_imp[k] <= flag_p_grid_imp[k] * Datas.P_GRID_MAX
                prob += p_grid_exp[k] <= flag_p_grid_exp[k] * Datas.P_GRID_MAX
                prob += flag_p_grid_imp[k] + flag_p_grid_exp[k] <= 1 # simultaneity
                # Absolute value for p_grid var
                # Export
                prob += abs_var_p_grid_exp_a[k] <= flag_abs_var_p_grid_exp_a[k] * Datas.P_GRID_MAX
                prob += abs_var_p_grid_exp_b[k] <= flag_abs_var_p_grid_exp_b[k] * Datas.P_GRID_MAX
                prob += flag_abs_var_p_grid_exp_a[k] + flag_abs_var_p_grid_exp_b[k] <= 1 # simultaneity
                # Import
                prob += abs_var_p_grid_imp_a[k] <= flag_abs_var_p_grid_imp_a[k] * Datas.P_GRID_MAX
                prob += abs_var_p_grid_imp_b[k] <= flag_abs_var_p_grid_imp_b[k] * Datas.P_GRID_MAX
                prob += flag_abs_var_p_grid_imp_a[k] + flag_abs_var_p_grid_imp_b[k] <= 1 # simultaneity
                # Absolute value between p_grid and p_grid_sch (ref)
                # Export
                prob += abs_ref_p_grid_exp_a[k] - abs_ref_p_grid_exp_b[k] == p_grid_exp[k] - Datas.P_GRID_EXP_DESIRED
                prob += abs_ref_p_grid_exp_a[k] <= flag_abs_ref_p_grid_exp_a[k] * Datas.P_GRID_MAX
                prob += abs_ref_p_grid_exp_b[k] <= flag_abs_ref_p_grid_exp_b[k] * Datas.P_GRID_MAX
                prob += flag_abs_ref_p_grid_exp_a[k] + flag_abs_ref_p_grid_exp_b[k] <= 1 # simultaneity
                # Import
                prob += abs_ref_p_grid_imp_a[k] - abs_ref_p_grid_imp_b[k] == p_grid_imp[k] - Datas.P_GRID_IMP_DESIRED
                prob += abs_ref_p_grid_imp_a[k] <= flag_abs_ref_p_grid_imp_a[k] * Datas.P_GRID_MAX
                prob += abs_ref_p_grid_imp_b[k] <= flag_abs_ref_p_grid_imp_b[k] * Datas.P_GRID_MAX
                prob += flag_abs_ref_p_grid_imp_a[k] + flag_abs_ref_p_grid_imp_b[k] <= 1 # simultaneity
            
            
            
            # BALANÇO DE POTÊNCIA NO BARRAMENTO DC
            if connected_mode is True:
                prob += (
                        + k_pv[k]*pv_forecasted.loc[k, 'data'] +
                        + p_bat_dis[k]
                        + p_grid_imp[k]
                        ==
                        + load_forecasted.loc[k, 'data'] +
                        + p_bat_ch[k]
                        + p_grid_exp[k]
                        )
            else:
                prob += (
                        + k_pv[k]*pv_forecasted.loc[k, 'data'] +
                        + p_bat_dis[k]
                        ==
                        + load_forecasted.loc[k, 'data'] +
                        + p_bat_ch[k]
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
            raise("[isolated_optimization_3th] Infactivel optimization problem")
        
        
        
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
                if connected_mode is True:
                    results_3th.loc[k, 'p_grid_sch']  = p_grid_imp[k].varValue - p_grid_exp[k].varValue
                else:
                    results_3th.loc[k, 'p_grid_sch']  = 0
                results_3th.loc[k, 'soc_bat']    = soc_bat[k].varValue
                results_3th.loc[k, 'pv_forecasted_3th'] = pv_forecasted.loc[k, 'data']
                results_3th.loc[k, 'load_forecasted_3th'] = load_forecasted.loc[k, 'data']
        else:
            print("ENGASGOU")

        return results_3th, fo_value





    ''' ------------------------------------------------------------------------------- 
    isolated Optimization 2th
    --------------------------------------------------------------------------------'''
    @staticmethod
    def optimization_2th(Datas: Datas, pv_forecasted: pd.DataFrame, load_forecasted: pd.DataFrame, connected_mode: bool) -> tuple:
        # print("isolated Optimization in 2th")
        
        # 2TH - 2TH - 2TH - 2TH - 2TH - 2TH - 2TH - 2TH
        if connected_mode is True:
            WEIGHT_REF_K_PV   = 1
            WEIGHT_VAR_K_PV   = 1
            WEIGHT_VAR_P_BAT  = 1
            WEIGHT_REF_P_BAT  = 0.5
            WEIGHT_REF_SOC_SC = 2
            WEIGHT_VAR_P_SC   = 0.001
            MULTIPLIER_J_VAR_BAT = 1
            WEIGHT_REF_P_GRID = 0.1
            WEIGHT_VAR_P_GRID = 0.001
            WEIGHT_J_SOC_SC_REC = 1000
        else:
            WEIGHT_REF_K_PV   = 1
            WEIGHT_VAR_K_PV   = 1
            WEIGHT_VAR_P_BAT  = 15
            WEIGHT_REF_P_BAT  = 1
            WEIGHT_REF_SOC_SC = 2
            WEIGHT_VAR_P_SC   = 0.0001
            MULTIPLIER_J_VAR_BAT = 75
            WEIGHT_J_SOC_SC_REC = 1000
        
        ''' -------------------- Optimization Problem ---------------------------- '''
        prob = pl.LpProblem("OptimizationMILP", pl.LpMinimize) # LpMinimize e LpMaximize
        solver = pl.PULP_CBC_CMD(msg=False, timeLimit=1)
        # Solver Disponívels (gratuitos)
        # ['PULP_CBC_CMD', 'SCIP_CMD']

        ''' ------------------------- VARIÁVEIS DO PROBLEMA ----------------------- '''   
        # BATTERY 
        # Battery power
        p_bat_dis    = pl.LpVariable.dicts('p_bat_dis', range(Datas.NP_2TH),lowBound=0, upBound=Datas.P_BAT_MAX,cat='Continuous')
        p_bat_ch     = pl.LpVariable.dicts('p_bat_ch', range(Datas.NP_2TH),lowBound=0, upBound=Datas.P_BAT_MAX,cat='Continuous')
        flag_ch_bat  = pl.LpVariable.dicts('flag_ch_bat', range(Datas.NP_2TH),cat='Binary')
        flag_dis_bat = pl.LpVariable.dicts('flag_dis_bat', range(Datas.NP_2TH),cat='Binary')
        soc_bat      = pl.LpVariable.dicts('soc_bat', range(Datas.NP_2TH),lowBound=Datas.SOC_BAT_MIN, upBound=Datas.SOC_BAT_MAX,cat='Continuous')
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
        abs_ref_p_bat_ch_a      = pl.LpVariable.dicts('abs_ref_p_bat_ch_a',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_MAX, cat='Continuous')
        abs_ref_p_bat_ch_b      = pl.LpVariable.dicts('abs_ref_p_bat_ch_b',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_MAX, cat='Continuous')
        flag_abs_ref_p_bat_ch_a = pl.LpVariable.dicts('flag_abs_ref_p_bat_ch_a', range(Datas.NP_2TH), cat='Binary')
        flag_abs_ref_p_bat_ch_b = pl.LpVariable.dicts('flag_abs_ref_p_bat_ch_b', range(Datas.NP_2TH), cat='Binary')
        # Discharge
        abs_ref_p_bat_dis_a      = pl.LpVariable.dicts('abs_ref_p_bat_dis_a',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_MAX, cat='Continuous')
        abs_ref_p_bat_dis_b      = pl.LpVariable.dicts('abs_ref_p_bat_dis_b',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_BAT_MAX, cat='Continuous')
        flag_abs_ref_p_bat_dis_a = pl.LpVariable.dicts('flag_abs_ref_p_bat_dis_a', range(Datas.NP_2TH), cat='Binary')
        flag_abs_ref_p_bat_dis_b = pl.LpVariable.dicts('flag_abs_ref_p_bat_dis_b', range(Datas.NP_2TH), cat='Binary')
        # Penalidade variacao bateria, Big-M
        flag_bigM_bat = pl.LpVariable.dicts('flag_d_bat', range(Datas.NP_2TH), cat='Binary')
        L_k_bat = -1000
        U_k_bat = 1000
        Epsolon_bat = 0.0001
        max_var_bat_bigM = 0.25

        # SUPERCAPACITOR
        # supercapacitor power
        p_sc_dis = pl.LpVariable.dicts('p_sc_dis', range(Datas.NP_2TH),lowBound=0, upBound=Datas.P_SC_MAX,cat='Continuous')
        p_sc_ch = pl.LpVariable.dicts('p_sc_ch', range(Datas.NP_2TH),lowBound=0, upBound=Datas.P_SC_MAX,cat='Continuous')
        flag_ch_sc = pl.LpVariable.dicts('flag_ch_sc', range(Datas.NP_2TH),cat='Binary')
        flag_dis_sc = pl.LpVariable.dicts('flag_dis_sc', range(Datas.NP_2TH),cat='Binary')
        soc_sc = pl.LpVariable.dicts('soc_sc', range(Datas.NP_2TH),lowBound=Datas.SOC_SC_MIN, upBound=Datas.SOC_SC_MAX,cat='Continuous')
        # Absolute valute for supercapacitor power variation module
        # Charg
        abs_var_p_sc_ch_a = pl.LpVariable.dicts('abs_var_p_sc_ch_a', range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_SC_VAR_MAX, cat='Continuous')
        abs_var_p_sc_ch_b = pl.LpVariable.dicts('abs_var_p_sc_ch_b', range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_SC_VAR_MAX, cat='Continuous')
        flag_abs_var_p_sc_ch_a = pl.LpVariable.dicts('flag_abs_var_p_sc_ch_a', range(Datas.NP_2TH), cat='Binary')
        flag_abs_var_p_sc_ch_b = pl.LpVariable.dicts('flag_abs_var_p_sc_ch_b', range(Datas.NP_2TH), cat='Binary')
        # Discharge
        abs_var_p_sc_dis_a = pl.LpVariable.dicts('abs_var_p_sc_dis_a', range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_SC_VAR_MAX, cat='Continuous')
        abs_var_p_sc_dis_b = pl.LpVariable.dicts('abs_var_p_sc_dis_b', range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_SC_VAR_MAX, cat='Continuous')
        flag_abs_var_p_sc_dis_a = pl.LpVariable.dicts('flag_abs_var_p_sc_dis_a', range(Datas.NP_2TH), cat='Binary')
        flag_abs_var_p_sc_dis_b = pl.LpVariable.dicts('flag_abs_var_p_sc_dis_b', range(Datas.NP_2TH), cat='Binary')
        # Absolute value for supercapacitor power reference
        # Charge
        abs_ref_soc_sc_a = pl.LpVariable.dicts('abs_ref_soc_sc_a', range(Datas.NP_2TH), lowBound=0, upBound=Datas.SOC_SC_MAX-Datas.SOC_SC_MIN, cat='Continuous')
        abs_ref_soc_sc_b = pl.LpVariable.dicts('abs_ref_soc_sc_b', range(Datas.NP_2TH), lowBound=0, upBound=Datas.SOC_SC_MAX-Datas.SOC_SC_MIN, cat='Continuous')
        flag_abs_ref_soc_sc_a = pl.LpVariable.dicts('flag_abs_ref_soc_sc_a', range(Datas.NP_2TH), cat='Binary')
        flag_abs_ref_soc_sc_b = pl.LpVariable.dicts('flag_abs_ref_soc_sc_b', range(Datas.NP_2TH), cat='Binary')
        # Penalidade para limites do SOC do SC
        Beta_soc_sc_max = pl.LpVariable.dicts('Beta_soc_sc_max', range(Datas.NP_2TH), cat='Binary')
        Beta_soc_sc_min = pl.LpVariable.dicts('Beta_soc_sc_min', range(Datas.NP_2TH), cat='Binary')
        L_k_soc_sc = - 1000
        U_k_soc_sc = 1000
        Epsolon_soc_sc = 0.0001

        # PHOTOVOLTAIC PANEL
        # k_pv
        k_pv                      = pl.LpVariable.dicts('k_pv',          range(Datas.NP_2TH), lowBound=0, upBound=1, cat='Continuous')
        # k_pv reference
        abs_ref_k_pv_a      = pl.LpVariable.dicts('abs_ref_k_pv_a',      range(Datas.NP_2TH), lowBound=0, upBound=1, cat='Continuous')
        abs_ref_k_pv_b      = pl.LpVariable.dicts('abs_ref_k_pv_b',      range(Datas.NP_2TH), lowBound=0, upBound=1, cat='Continuous')
        flag_abs_ref_k_pv_a = pl.LpVariable.dicts('flag_abs_ref_k_pv_a', range(Datas.NP_2TH), cat='Binary')
        flag_abs_ref_k_pv_b = pl.LpVariable.dicts('flag_abs_ref_k_pv_b', range(Datas.NP_2TH), cat='Binary')
        # k_pv variation
        abs_var_k_pv_a = pl.LpVariable.dicts('abs_var_k_pv_a', range(Datas.NP_2TH), lowBound=0, upBound=1, cat='Continuous')
        abs_var_k_pv_b = pl.LpVariable.dicts('abs_var_k_pv_b', range(Datas.NP_2TH), lowBound=0, upBound=1, cat='Continuous')
        
        # Main Grid
        if (connected_mode):
            # p_imp
            p_grid_imp    = pl.LpVariable.dicts('p_grid_imp',         range(Datas.NP_2TH),lowBound=0, upBound=Datas.P_GRID_MAX,cat='Continuous')
            flag_p_grid_imp  = pl.LpVariable.dicts('flag_p_grid_imp',   range(Datas.NP_2TH),cat='Binary')
            # p_exp
            p_grid_exp    = pl.LpVariable.dicts('p_grid_exp',         range(Datas.NP_2TH),lowBound=0, upBound=Datas.P_GRID_MAX,cat='Continuous')
            flag_p_grid_exp  = pl.LpVariable.dicts('flag_p_grid_exp',   range(Datas.NP_2TH),cat='Binary')
            # Export variation
            abs_var_p_grid_exp_a      = pl.LpVariable.dicts('abs_var_p_grid_exp_a',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_GRID_VAR_MAX, cat='Continuous')
            abs_var_p_grid_exp_b      = pl.LpVariable.dicts('abs_var_p_grid_exp_b',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_GRID_VAR_MAX, cat='Continuous')
            flag_abs_var_p_grid_exp_a = pl.LpVariable.dicts('flag_abs_var_p_grid_exp_a', range(Datas.NP_2TH), cat='Binary')
            flag_abs_var_p_grid_exp_b = pl.LpVariable.dicts('flag_abs_var_p_grid_exp_b', range(Datas.NP_2TH), cat='Binary')
            # Import variation
            abs_var_p_grid_imp_a      = pl.LpVariable.dicts('abs_var_p_grid_imp_a',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_GRID_VAR_MAX, cat='Continuous')
            abs_var_p_grid_imp_b      = pl.LpVariable.dicts('abs_var_p_grid_imp_b',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_GRID_VAR_MAX, cat='Continuous')
            flag_abs_var_p_grid_imp_a = pl.LpVariable.dicts('flag_abs_var_p_grid_imp_a', range(Datas.NP_2TH), cat='Binary')
            flag_abs_var_p_grid_imp_b = pl.LpVariable.dicts('flag_abs_var_p_grid_imp_b', range(Datas.NP_2TH), cat='Binary')
            # Export reference
            abs_ref_p_grid_exp_a      = pl.LpVariable.dicts('abs_ref_p_grid_exp_a',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_GRID_MAX, cat='Continuous')
            abs_ref_p_grid_exp_b      = pl.LpVariable.dicts('abs_ref_p_grid_exp_b',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_GRID_MAX, cat='Continuous')
            flag_abs_ref_p_grid_exp_a = pl.LpVariable.dicts('flag_abs_ref_p_grid_exp_a', range(Datas.NP_2TH), cat='Binary')
            flag_abs_ref_p_grid_exp_b = pl.LpVariable.dicts('flag_abs_ref_p_grid_exp_b', range(Datas.NP_2TH), cat='Binary')
            # Import reference
            abs_ref_p_grid_imp_a      = pl.LpVariable.dicts('abs_ref_p_grid_imp_a',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_GRID_MAX, cat='Continuous')
            abs_ref_p_grid_imp_b      = pl.LpVariable.dicts('abs_ref_p_grid_imp_b',      range(Datas.NP_2TH), lowBound=0, upBound=Datas.P_GRID_MAX, cat='Continuous')
            flag_abs_ref_p_grid_imp_a = pl.LpVariable.dicts('flag_abs_ref_p_grid_imp_a', range(Datas.NP_2TH), cat='Binary')
            flag_abs_ref_p_grid_imp_b = pl.LpVariable.dicts('flag_abs_ref_p_grid_imp_b', range(Datas.NP_2TH), cat='Binary')
            
        
        # Power Balance pl.LpVariable.dicts('abs_var_p_bat_ch_a',     
        power_balance = pl.LpVariable.dicts('power_balance', range(Datas.NP_2TH),lowBound=0, upBound=1,cat='Continuous')
        

        ''' ------------------------- FUNÇÃO OBJETIVO ------------------------------'''
        # We created each party of the OF separately. Then we put them all together.
        J_k_pv_ref    = pl.lpSum([(abs_ref_k_pv_a[k] + abs_ref_k_pv_b[k]) for k in range(Datas.NP_2TH)])
        
        J_k_pv_var    = pl.lpSum([(abs_var_k_pv_a[k] + abs_var_k_pv_b[k])] for k in range(Datas.NP_2TH))
        
        J_bat_var_ch  = pl.lpSum([(abs_var_p_bat_ch_a[k] + abs_var_p_bat_ch_b[k] + flag_bigM_bat[k]*MULTIPLIER_J_VAR_BAT)] for k in range(Datas.NP_2TH))
        
        J_bat_var_dis = pl.lpSum([(abs_var_p_bat_dis_a[k] + abs_var_p_bat_dis_b[k] + flag_bigM_bat[k]*MULTIPLIER_J_VAR_BAT)] for k in range(Datas.NP_2TH))
        
        J_bat_ref_p_bat_ch = pl.lpSum([(abs_ref_p_bat_ch_a[k] + abs_ref_p_bat_ch_b[k])] for k in range(Datas.NP_2TH))
        
        J_bat_ref_p_bat_dis = pl.lpSum([(abs_ref_p_bat_dis_a[k] + abs_ref_p_bat_dis_b[k])] for k in range(Datas.NP_2TH))
        
        J_sc_ref_soc = pl.lpSum([(abs_ref_soc_sc_a[k] + abs_ref_soc_sc_b[k])] for k in range(Datas.NP_2TH))
        
        J_sc_var_ch = pl.lpSum([(abs_var_p_sc_ch_a[k] + abs_var_p_sc_ch_b[k])] for k in range(Datas.NP_2TH))
        
        J_sc_var_dis = pl.lpSum([(abs_var_p_sc_dis_a[k] + abs_var_p_sc_dis_b[k])] for k in range(Datas.NP_2TH))
        
        J_sc_limit = pl.lpSum([((Beta_soc_sc_max[k] + Beta_soc_sc_min[k]))] for k in range(Datas.NP_2TH))
        
        if connected_mode is True:
            # Ref
            J_grid_ref_imp = pl.lpSum([(abs_ref_p_grid_imp_a[k] + abs_ref_p_grid_imp_b[k])] for k in range(Datas.NP_2TH))
            J_grid_ref_exp = pl.lpSum([(abs_ref_p_grid_exp_a[k] + abs_ref_p_grid_exp_b[k])] for k in range(Datas.NP_2TH))
            # Var
            J_grid_var_imp = pl.lpSum([(abs_var_p_grid_imp_a[k] + abs_var_p_grid_imp_b[k])] for k in range(Datas.NP_2TH))
            J_grid_var_exp = pl.lpSum([(abs_var_p_grid_exp_a[k] + abs_var_p_grid_exp_b[k])] for k in range(Datas.NP_2TH))
        
        
        # TODO: Dividir pelo máximo da parcela (Deve passar por normalização)
        if connected_mode is True:
            objective_function = (  (WEIGHT_REF_K_PV   * J_k_pv_ref)
                                  + (WEIGHT_VAR_K_PV   * J_k_pv_var)
                                  + (WEIGHT_VAR_P_BAT  * (J_bat_var_ch + J_bat_var_dis))
                                  + (WEIGHT_REF_P_BAT  * (J_bat_ref_p_bat_ch + J_bat_ref_p_bat_dis))
                                  + (WEIGHT_REF_SOC_SC * J_sc_ref_soc)   
                                  + (WEIGHT_VAR_P_SC   * (J_sc_var_ch + J_sc_var_dis))
                                  + (WEIGHT_J_SOC_SC_REC * J_sc_limit)
                                  + (WEIGHT_REF_P_GRID * (J_grid_ref_imp + J_grid_ref_exp))
                                  + (WEIGHT_VAR_P_GRID * (J_grid_var_imp + J_grid_var_exp))
                                  )
        else:
            objective_function = (  (WEIGHT_REF_K_PV   * J_k_pv_ref)
                                  + (WEIGHT_VAR_K_PV   * J_k_pv_var)
                                  + (WEIGHT_VAR_P_BAT  * (J_bat_var_ch + J_bat_var_dis))
                                  + (WEIGHT_REF_P_BAT  * (J_bat_ref_p_bat_ch + J_bat_ref_p_bat_dis))
                                  + (WEIGHT_REF_SOC_SC * J_sc_ref_soc)
                                  + (WEIGHT_VAR_P_SC   * (J_sc_var_ch + J_sc_var_dis))
                                  + (WEIGHT_J_SOC_SC_REC * J_sc_limit)
                                )
        prob.setObjective(objective_function)
        
        
        
        ''' --------------------------- RESTRIÇÕES -------------------------------- '''
        for k in range(0, Datas.NP_2TH):
            
            # BATTERY
            # P_bat
            prob += p_bat_ch[k] <= flag_ch_bat[k] * Datas.P_BAT_MAX
            prob += p_bat_dis[k] <= flag_dis_bat[k]  * Datas.P_BAT_MAX
            prob += flag_ch_bat[k] + flag_dis_bat[k] <= 1 # simultaneity     
            if k == 0:
                # SOC bat
                prob += soc_bat[k] == Datas.soc_bat
                # var p_bat
                if Datas.p_bat >= 0:
                   prob += abs_var_p_bat_ch_a[k] - abs_var_p_bat_ch_b[k] == p_bat_ch[k] - 0
                   prob += abs_var_p_bat_dis_a[k] - abs_var_p_bat_dis_b[k] == p_bat_dis[k] - Datas.p_bat
                else:
                   prob += abs_var_p_bat_ch_a[k] - abs_var_p_bat_ch_b[k] == p_bat_ch[k] - (-Datas.p_bat) # (-Datas.p_bat) because p_bat_ch is positive defined
                   prob += abs_var_p_bat_dis_a[k] - abs_var_p_bat_dis_b[k] == p_bat_dis[k] - 0
            else:
                # SOC bat
                prob += soc_bat[k] == soc_bat[k-1] - (p_bat_dis[k-1] - p_bat_ch[k-1])*(Datas.TS_2TH/60/60)/Datas.Q_BAT
                # var p_bat
                prob += abs_var_p_bat_ch_a[k] - abs_var_p_bat_ch_b[k] == p_bat_ch[k] - p_bat_ch[k-1]
                prob += abs_var_p_bat_dis_a[k] - abs_var_p_bat_dis_b[k] == p_bat_dis[k] - p_bat_dis[k-1]
            # Absolute value for p_bat var
            prob += abs_var_p_bat_ch_a[k] <= flag_abs_var_p_bat_ch_a[k] * Datas.P_BAT_VAR_MAX
            prob += abs_var_p_bat_ch_b[k] <= flag_abs_var_p_bat_ch_b[k] * Datas.P_BAT_VAR_MAX
            prob += flag_abs_var_p_bat_ch_a[k] + flag_abs_var_p_bat_ch_b[k] <= 1 # simultaneity
            prob += abs_var_p_bat_dis_a[k] <= flag_abs_var_p_bat_dis_a[k] * Datas.P_BAT_VAR_MAX
            prob += abs_var_p_bat_dis_b[k] <= flag_abs_var_p_bat_dis_b[k] * Datas.P_BAT_VAR_MAX
            prob += flag_abs_var_p_bat_dis_a[k] + flag_abs_var_p_bat_dis_b[k] <= 1 # simultaneity
            # flag_bigM_bat   L_k_bat     U_k_bat    Epsolon_bat    max_var_bat_bigM
            prob += (abs_var_p_bat_ch_a[k] + abs_var_p_bat_ch_b[k] + abs_var_p_bat_dis_a[k] + abs_var_p_bat_dis_b[k]) - max_var_bat_bigM >= L_k_bat * (1 - flag_bigM_bat[k])
            prob += (abs_var_p_bat_ch_a[k] + abs_var_p_bat_ch_b[k] + abs_var_p_bat_dis_a[k] + abs_var_p_bat_dis_b[k]) - max_var_bat_bigM <= (U_k_bat + Epsolon_bat)*flag_bigM_bat[k] - Epsolon_bat
            # Absolute value between p_bat and p_bat_sch (ref)
            # Charge
            prob += abs_ref_p_bat_ch_a[k] - abs_ref_p_bat_ch_b[k] == p_bat_ch[k] - Datas.p_bat_ch_sch
            prob += abs_ref_p_bat_ch_a[k] <= flag_abs_ref_p_bat_ch_a[k] * Datas.P_BAT_MAX
            prob += abs_ref_p_bat_ch_b[k] <= flag_abs_ref_p_bat_ch_b[k] * Datas.P_BAT_MAX
            prob += flag_abs_ref_p_bat_ch_a[k] + flag_abs_ref_p_bat_ch_b[k] <= 1 # simultaneity
            # Discharge
            prob += abs_ref_p_bat_dis_a[k] - abs_ref_p_bat_dis_b[k] == p_bat_dis[k] - Datas.p_bat_dis_sch
            prob += abs_ref_p_bat_dis_a[k] <= flag_abs_ref_p_bat_dis_a[k] * Datas.P_BAT_MAX
            prob += abs_ref_p_bat_dis_b[k] <= flag_abs_ref_p_bat_dis_b[k] * Datas.P_BAT_MAX
            prob += flag_abs_ref_p_bat_dis_a[k] + flag_abs_ref_p_bat_dis_b[k] <= 1 # simultaneity
            
            
            # SUPERCAPACITOR
            # p_sc
            prob += p_sc_ch[k] <= flag_ch_sc[k] * Datas.P_SC_MAX
            prob += p_sc_dis[k] <= flag_dis_sc[k] * Datas.P_SC_MAX
            prob += flag_ch_sc[k] + flag_dis_sc[k] <= 1 # simultaneity
            if k == 0:
                # SOC sc
                prob += soc_sc[k] == Datas.soc_sc
                # var p_sc
                if Datas.p_sc >= 0:
                    prob += abs_var_p_sc_ch_a[k] - abs_var_p_sc_ch_b[k] == p_sc_ch[k] - 0
                    prob += abs_var_p_sc_dis_a[k] - abs_var_p_sc_dis_b[k] == p_sc_dis[k] - Datas.p_sc
                else:
                    prob += abs_var_p_sc_ch_a[k] - abs_var_p_sc_ch_b[k] == p_sc_ch[k] - (-Datas.p_sc)
                    prob += abs_var_p_sc_dis_a[k] - abs_var_p_sc_dis_b[k] == p_sc_dis[k] - 0
            else:
                # SOC sc
                prob += soc_sc[k] == soc_sc[k-1] - (p_sc_dis[k-1] - p_sc_ch[k-1])*(Datas.TS_2TH/60/60)/Datas.Q_SC
                # vat p_sc
                prob += abs_var_p_sc_ch_a[k] - abs_var_p_sc_ch_b[k] == p_sc_ch[k] - p_bat_ch[k-1]
                prob += abs_var_p_sc_dis_a[k] - abs_var_p_sc_dis_b[k] == p_sc_dis[k] - p_bat_dis[k-1]
            # Absolute value for var p_sc
            prob += abs_var_p_sc_ch_a[k] <= flag_abs_var_p_sc_ch_a[k] * Datas.P_SC_VAR_MAX
            prob += abs_var_p_sc_ch_b[k] <= flag_abs_var_p_sc_ch_b[k] * Datas.P_SC_VAR_MAX
            prob += flag_abs_var_p_sc_ch_a[k] + flag_abs_var_p_sc_ch_b[k] <= 1 # simultaneity
            prob += abs_var_p_sc_dis_a[k] <= flag_abs_var_p_sc_dis_a[k] * Datas.P_SC_VAR_MAX
            prob += abs_var_p_sc_dis_b[k] <= flag_abs_var_p_sc_dis_b[k] * Datas.P_SC_VAR_MAX
            prob += flag_abs_var_p_sc_dis_a[k] + flag_abs_var_p_sc_dis_b[k] <= 1 # simultaneity
            # Absolute value between SOC and SOC_ref
            prob += abs_ref_soc_sc_a[k] - abs_ref_soc_sc_b[k] == soc_sc[k] - Datas.SOC_SC_REF
            prob += abs_ref_soc_sc_a[k] <= flag_abs_ref_soc_sc_a[k]
            prob += abs_ref_soc_sc_b[k] <= flag_abs_ref_soc_sc_b[k]
            prob += flag_abs_ref_soc_sc_a[k] + flag_abs_ref_soc_sc_b[k] <= 1 # simultaneity
            # Penalidade de SOC_sc > SOC_sc_min recomendado
            prob += soc_sc[k] - Datas.SOC_SC_MIN_RECOMMENDED <= (U_k_soc_sc + Epsolon_soc_sc) * (1 - Beta_soc_sc_min[k]) - Epsolon_soc_sc
            prob += soc_sc[k] - Datas.SOC_SC_MIN_RECOMMENDED >= L_k_soc_sc * Beta_soc_sc_min[k]
            # Penalidade de SOC_sc > SOC_sc_max recomendado
            prob += soc_sc[k] - Datas.SOC_SC_MAX_RECOMMENDED >= (L_k_soc_sc - Epsolon_soc_sc) * (1 - Beta_soc_sc_max[k]) + Epsolon_soc_sc
            prob += soc_sc[k] - Datas.SOC_SC_MAX_RECOMMENDED <= U_k_soc_sc * Beta_soc_sc_max[k]

            # k_pv
            if k == 0:
                # var k_pv
                prob += abs_var_k_pv_a[k] - abs_var_k_pv_b[k] == k_pv[k] - Datas.k_pv  
            else:
                # var k_pv
                prob += abs_var_k_pv_a[k] - abs_var_k_pv_b[k] == k_pv[k] - k_pv[k-1]
            # Absolute value between k_pv and K_PV_REF
            prob += abs_ref_k_pv_a[k] - abs_ref_k_pv_b[k] == k_pv[k] - Datas.k_pv_sch
            prob += abs_ref_k_pv_a[k] <= flag_abs_ref_k_pv_a[k]
            prob += abs_ref_k_pv_b[k] <= flag_abs_ref_k_pv_b[k]
            prob += flag_abs_ref_k_pv_a[k] + flag_abs_ref_k_pv_b[k] <= 1 # simultaneity
            
            
            # MAIN GRID
            if connected_mode is True:
                prob += p_grid_imp[k] <= flag_p_grid_imp[k] * Datas.P_GRID_MAX
                prob += p_grid_exp[k] <= flag_p_grid_exp[k] * Datas.P_GRID_MAX
                prob += flag_p_grid_imp[k] + flag_p_grid_exp[k] <= 1 # simultaneity
                # var
                if k == 0:
                    # var p_grid k = 0
                    if Datas.p_grid >= 0:
                        prob += abs_var_p_grid_exp_a[k] - abs_var_p_grid_exp_b[k] == p_grid_exp[k] - 0
                        prob += abs_var_p_grid_imp_a[k] - abs_var_p_grid_imp_b[k] == p_grid_imp[k] - Datas.p_grid
                    else:
                        prob += abs_var_p_grid_exp_a[k] - abs_var_p_grid_exp_b[k] == p_grid_exp[k] - (-Datas.p_grid) # (-Datas.p_grid) because p_grid_exp is positive defined
                        prob += abs_var_p_grid_imp_a[k] - abs_var_p_grid_imp_b[k] == p_grid_imp[k] - 0
                else:
                    # var p_grid k > 0
                    prob += abs_var_p_grid_exp_a[k] - abs_var_p_grid_exp_b[k] == p_grid_exp[k] - p_grid_exp[k-1]
                    prob += abs_var_p_grid_imp_a[k] - abs_var_p_grid_imp_b[k] == p_grid_imp[k] - p_grid_imp[k-1]
                # Absolute value for var p_grid_imp 
                prob += abs_var_p_grid_imp_a[k] <= flag_abs_var_p_grid_imp_a[k] * Datas.P_GRID_MAX
                prob += abs_var_p_grid_imp_b[k] <= flag_abs_var_p_grid_imp_b[k] * Datas.P_GRID_MAX
                prob += flag_abs_var_p_grid_imp_a[k] + flag_abs_var_p_grid_imp_b[k] <= 1 # simultaneity
                # Absolute value for var p_grid_exp 
                prob += abs_var_p_grid_exp_a[k] <= flag_abs_var_p_grid_exp_a[k] * Datas.P_GRID_MAX
                prob += abs_var_p_grid_exp_b[k] <= flag_abs_var_p_grid_exp_b[k] * Datas.P_GRID_MAX
                prob += flag_abs_var_p_grid_exp_a[k] + flag_abs_var_p_grid_exp_b[k] <= 1 # simultaneity
                # Absolute value between p_grid and p_grid_sch (ref)
                # Export
                prob += abs_ref_p_grid_exp_a[k] - abs_ref_p_grid_exp_b[k] == p_grid_exp[k] - Datas.p_grid_exp_sch
                prob += abs_ref_p_grid_exp_a[k] <= flag_abs_ref_p_grid_exp_a[k] * Datas.P_GRID_MAX
                prob += abs_ref_p_grid_exp_b[k] <= flag_abs_ref_p_grid_exp_b[k] * Datas.P_GRID_MAX
                prob += flag_abs_ref_p_grid_exp_a[k] + flag_abs_ref_p_grid_exp_b[k] <= 1 # simultaneity
                # Import
                prob += abs_ref_p_grid_imp_a[k] - abs_ref_p_grid_imp_b[k] == p_grid_imp[k] - Datas.p_grid_imp_sch
                prob += abs_ref_p_grid_imp_a[k] <= flag_abs_ref_p_grid_imp_a[k] * Datas.P_GRID_MAX
                prob += abs_ref_p_grid_imp_b[k] <= flag_abs_ref_p_grid_imp_b[k] * Datas.P_GRID_MAX
                prob += flag_abs_ref_p_grid_imp_a[k] + flag_abs_ref_p_grid_imp_b[k] <= 1 # simultaneity


            # BALANÇO DE POTÊNCIA NO BARRAMENTO DC
            if connected_mode is True:
                prob += power_balance[k] == (
                        k_pv[k]*pv_forecasted.loc[k, 'data'] + 
                        + p_bat_dis[k] +
                        + p_sc_dis[k] +
                        + p_grid_imp[k] +
                        - load_forecasted.loc[k, 'data'] + 
                        - p_bat_ch[k] +
                        - p_sc_ch[k] +
                        - p_grid_exp[k]
                        )
            else:    
                prob += power_balance[k] == (
                        k_pv[k]*pv_forecasted.loc[k, 'data'] + 
                        + p_bat_dis[k] +
                        + p_sc_dis[k] +
                        - load_forecasted.loc[k, 'data'] + 
                        - p_bat_ch[k] +
                        - p_sc_ch[k]
                        )
            prob += power_balance[k] == 0
        
        ''' ------------------------------------------------------------------------------- 
        EXECUTA O ALGORITMO DE OTIMIZAÇÃO
        --------------------------------------------------------------------------------'''
        # print("EXECUTAR SOLVER 2th")
        solution  = prob.solve(solver)
        fo_status = pl.LpStatus[solution]
        fo_value = pl.value(prob.objective)
        # print("Status: {}".format(fo_status))
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
            # print("OTIMO")
            # Results
            results_2th = pd.DataFrame(index=range(Datas.NP_2TH), columns=['p_bat_ref', 'k_pv_ref', 'p_grid_ref', 'p_sc_ref', 'soc_bat', 'soc_sc'])
            for k in range(0, Datas.NP_2TH):
                # This values are for inverters reference
                results_2th.loc[k, 'p_bat_ref'] = p_bat_dis[k].varValue - p_bat_ch[k].varValue
                results_2th.loc[k, 'k_pv_ref'] = k_pv[k].varValue
                if connected_mode is True:
                    results_2th.loc[k, 'p_grid_ref'] = p_grid_imp[k].varValue - p_grid_exp[k].varValue
                else:
                    results_2th.loc[k, 'p_grid_ref'] = 0
                results_2th.loc[k, 'p_sc_ref'] = p_sc_dis[k].varValue - p_sc_ch[k].varValue
                
                # These values are for analysis only
                results_2th.loc[k, 'soc_bat'] = soc_bat[k].varValue
                results_2th.loc[k, 'soc_sc'] = soc_sc[k].varValue
                
                if power_balance[k].varValue >= 0.001:
                    print("Ta dando merda")
                    
                if (Beta_soc_sc_max[k].varValue > 0) or (Beta_soc_sc_min[k].varValue > 0):
                    print(f"************ SOC_sc: {soc_sc[k].varValue}")
                # print(f"flagbigM: {flag_bigM_bat[k].varValue}, ABSvar: {(abs_var_p_bat_ch_a[k].varValue + abs_var_p_bat_ch_b[k].varValue + abs_var_p_bat_dis_a[k].varValue + abs_var_p_bat_dis_b[k].varValue)}")
                # Verifica se existe algum NaN
            existe_nan = results_2th.isna().any().any()
            if existe_nan:
                print(f"Error. NaN in results_2th")  # True se houver NaN, False caso contrário
                print(results_2th)
        else:
            print("Error. ENGASGOU in isolated_optimization_2th")

        return results_2th, fo_value
