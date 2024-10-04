# -*- coding: utf-8 -*-
'''============================================================================
                               PROJETO V2G
#==========================================================================='''

import pulp as pl



class OptimizationMILP:

    def __init__(self, Datas) -> None:

        self.Datas = Datas


    ''' ------------------------------------------------------------------------------- 
    isolated Optimization 3th
    --------------------------------------------------------------------------------'''
    def isolated_optimization_3th(self):
        print("isolated Optimization in 3th")
        
        ''' -------------------- Optimization Problem ---------------------------- '''
        prob = pl.LpProblem("OptimizationMILP", pl.LpMinimize) # LpMinimize e LpMaximize
        solver = pl.PULP_CBC_CMD(msg=False, timeLimit=60*1)
        # Solver Disponívels (gratuitos)
        # ['PULP_CBC_CMD', 'SCIP_CMD']



        ''' ------------------------- VARIÁVEIS DO PROBLEMA ----------------------- '''    
        # Battery power
        p_bat_3th_dis    = pl.LpVariable.dicts('p_bat_3th_dis',    range(self.Datas.NP_3TH),lowBound=0, upBound=self.Datas.P_BAT_MAX,cat='Continuous')
        p_bat_3th_ch     = pl.LpVariable.dicts('p_bat_3th_ch',     range(self.Datas.NP_3TH),lowBound=0, upBound=self.Datas.P_BAT_MAX,cat='Continuous')
        flag_ch_bat_est  = pl.LpVariable.dicts('flag_ch_bat_est',  range(self.Datas.NP_3TH),cat='Binary')
        flag_dis_bat_est = pl.LpVariable.dicts('flag_dis_bat_est', range(self.Datas.NP_3TH),cat='Binary')
        soc_bat          = pl.LpVariable.dicts('soc_bat',          range(self.Datas.NP_3TH),lowBound=self.Datas.SOC_BAT_MIN, upBound=self.Datas.SOC_BAT_MAX,cat='Continuous')
        
        # Battery power variation module (Absolute value = A)
        # Charg
        A_bat_a_3th_var_ch       = pl.LpVariable.dicts('A_bat_a_3th_var_ch',      range(self.Datas.NP_3TH), lowBound=0, upBound=self.Datas.P_BAT_VAR_MAX, cat='Continuous')
        A_bat_b_3th_var_ch       = pl.LpVariable.dicts('A_bat_b_3th_var_ch',      range(self.Datas.NP_3TH), lowBound=0, upBound=self.Datas.P_BAT_VAR_MAX, cat='Continuous')
        flag_A_bat_a_3th_var_ch  = pl.LpVariable.dicts('flag_A_bat_a_3th_var_ch', range(self.Datas.NP_3TH), cat='Binary')
        flag_A_bat_b_3th_var_ch  = pl.LpVariable.dicts('flag_A_bat_b_3th_var_ch', range(self.Datas.NP_3TH), cat='Binary')
        # Discharge
        A_bat_a_3th_var_dis      = pl.LpVariable.dicts('A_bat_a_3th_var_dis',      range(self.Datas.NP_3TH), lowBound=0, upBound=self.Datas.P_BAT_VAR_MAX, cat='Continuous')
        A_bat_b_3th_var_dis      = pl.LpVariable.dicts('A_bat_b_3th_var_dis',      range(self.Datas.NP_3TH), lowBound=0, upBound=self.Datas.P_BAT_VAR_MAX, cat='Continuous')
        flag_A_bat_a_3th_var_dis = pl.LpVariable.dicts('flag_A_bat_a_3th_var_dis', range(self.Datas.NP_3TH), cat='Binary')
        flag_A_bat_b_3th_var_dis = pl.LpVariable.dicts('flag_A_bat_b_3th_var_dis', range(self.Datas.NP_3TH), cat='Binary')
        
        # Battery absolute values
        A_bat_a_3th_soc          = pl.LpVariable.dicts('A_bat_a_3th_soc',      range(self.Datas.NP_3TH), lowBound=0, upBound=self.Datas.P_BAT_MAX, cat='Continuous')
        A_bat_b_3th_soc          = pl.LpVariable.dicts('A_bat_b_3th_soc',      range(self.Datas.NP_3TH), lowBound=0, upBound=self.Datas.P_BAT_MAX, cat='Continuous')
        flag_A_bat_a_3th_soc     = pl.LpVariable.dicts('flag_A_bat_a_3th_soc', range(self.Datas.NP_3TH), cat='Binary')
        flag_A_bat_b_3th_soc     = pl.LpVariable.dicts('flag_A_bat_b_3th_soc', range(self.Datas.NP_3TH), cat='Binary')
        
        # Photovoltaic Panel
        k_pv_3th                 = pl.LpVariable.dicts('k_pv_3th',          range(self.Datas.NP_3TH), lowBound=0, upBound=1, cat='Continuous')
        A_k_pv_a_3th             = pl.LpVariable.dicts('A_k_pv_a_3th',      range(self.Datas.NP_3TH), lowBound=0, upBound=1, cat='Continuous')
        A_k_pv_b_3th             = pl.LpVariable.dicts('A_k_pv_b_3th',      range(self.Datas.NP_3TH), lowBound=0, upBound=1, cat='Continuous')
        flag_A_k_pv_a_3th        = pl.LpVariable.dicts('flag_A_k_pv_a_3th', range(self.Datas.NP_3TH), cat='Binary')
        flag_A_k_pv_b_3th        = pl.LpVariable.dicts('flag_A_k_pv_b_3th', range(self.Datas.NP_3TH), cat='Binary')



        ''' ------------------------- FUNÇÃO OBJETIVO ------------------------------'''
        J_pv_3th          = pl.lpSum([(A_k_pv_a_3th[k] + A_k_pv_b_3th[k]) for k in range(self.Datas.NP_3TH)])
        
        J_bat_3th_var_ch  = pl.lpSum([(A_bat_a_3th_var_ch[k] + A_bat_b_3th_var_ch[k])] for k in range(self.Datas.NP_3TH))
        
        J_bat_3th_var_dis = pl.lpSum([(A_bat_a_3th_var_dis[k] + A_bat_b_3th_var_dis[k])] for k in range(self.Datas.NP_3TH))
        
        J_bat_3th_var_soc = pl.lpSum([(A_bat_a_3th_soc[k] + A_bat_b_3th_soc[k])] for k in range(self.Datas.NP_3TH))
        
        # Divide por 2 porque porque porque sao duas parcelas referente a mesma coisa
        # TODO: Dividir pelo máximo da parcela (Deve passar por normalização)
        objective_function = ( (self.Datas.WEIGHT_K_PV_3TH      * J_pv_3th          / 1)
                             + (self.Datas.WEIGHT_DELTA_BAT_3TH * J_bat_3th_var_ch  / 2)
                             + (self.Datas.WEIGHT_DELTA_BAT_3TH * J_bat_3th_var_dis / 2)
                             + (self.Datas.WEIGHT_SOC_BAT_3TH   * J_bat_3th_var_soc / 1)
                             )
        prob.setObjective(objective_function)
        
        
        
        ''' --------------------------- RESTRIÇÕES -------------------------------- '''
        '''
            No código, k = 0, é o mesmo que X(t+k|t) para k = 1, do texto.
            
            k=0 é o atual
        '''  
        for k in range(0, self.Datas.NP_3TH):
            
            # P_bat
            prob += p_bat_3th_ch[k]  <= self.Datas.P_BAT_MAX * flag_ch_bat_est[k]
            prob += p_bat_3th_dis[k] <= self.Datas.P_BAT_MAX * flag_dis_bat_est[k]
            prob += flag_ch_bat_est[k] + flag_dis_bat_est[k] <= 1 # simultaneity
            
            
            # Absolute value for battery power charge variation
            if k > 0:
                prob += A_bat_a_3th_var_ch[k] - A_bat_b_3th_var_ch[k] == p_bat_3th_ch[k] - p_bat_3th_ch[k-1]
            else: # k = 0
                if self.Datas.p_bat >= 0:
                    prob += A_bat_a_3th_var_ch[k] - A_bat_b_3th_var_ch[k] == p_bat_3th_ch[k] - 0
                else:
                    prob += A_bat_a_3th_var_ch[k] - A_bat_b_3th_var_ch[k] == p_bat_3th_ch[k] - self.Datas.p_bat
            
            prob += A_bat_a_3th_var_ch[k] <= flag_A_bat_a_3th_var_ch[k] * self.Datas.P_BAT_VAR_MAX
            prob += A_bat_b_3th_var_ch[k] <= flag_A_bat_b_3th_var_ch[k] * self.Datas.P_BAT_VAR_MAX
            prob += flag_A_bat_a_3th_var_ch[k] + flag_A_bat_b_3th_var_ch[k] <= 1 # simultaneity
            
            
            # Absolute value for battery power  discharge variation
            if k > 0:
                prob += A_bat_a_3th_var_dis[k] - A_bat_b_3th_var_dis[k] == p_bat_3th_dis[k] - p_bat_3th_dis[k-1]
            else:
                if self.Datas.p_bat >= 0:
                   prob += A_bat_a_3th_var_dis[k] - A_bat_b_3th_var_dis[k] == p_bat_3th_dis[k] - self.Datas.p_bat
                else:
                   prob += A_bat_a_3th_var_dis[k] - A_bat_b_3th_var_dis[k] == p_bat_3th_dis[k] - 0
            
            prob += A_bat_a_3th_var_dis[k] <= flag_A_bat_a_3th_var_dis[k] * self.Datas.P_BAT_VAR_MAX
            prob += A_bat_b_3th_var_dis[k] <= flag_A_bat_b_3th_var_dis[k] * self.Datas.P_BAT_VAR_MAX
            prob += flag_A_bat_a_3th_var_dis[k] + flag_A_bat_b_3th_var_dis[k] <= 1 # simultaneity


            # Battery SOC
            if k > 0:
                prob += soc_bat[k] == soc_bat[k-1] + (p_bat_3th_dis[k-1] - p_bat_3th_ch[k-1])*self.Datas.TS_3TH/self.Datas.Q_BAT
            else:
                prob += soc_bat[k] == self.Datas.soc_bat

            # Absolute value between SOC and SOC_ref
            prob += A_bat_a_3th_soc[k] - A_bat_b_3th_soc[k] == soc_bat[k] - self.Datas.SOC_BAT_REF
            prob += A_bat_a_3th_soc[k] <= flag_A_bat_a_3th_soc
            prob += A_bat_b_3th_soc[k] <= flag_A_bat_b_3th_soc
            prob += flag_A_bat_a_3th_soc[k] + flag_A_bat_b_3th_soc[k] <= 1 # simultaneity

            # PV
            prob += A_k_pv_a_3th[k] - A_k_pv_b_3th[k] == k_pv_3th[k] - self.Datas.K_PV_REF_3TH
            prob += A_k_pv_a_3th[k] <= flag_A_k_pv_a_3th
            prob += A_k_pv_b_3th[k] <= flag_A_k_pv_b_3th
            prob += flag_A_k_pv_a_3th[k] + flag_A_k_pv_b_3th[k] <= 1 # simultaneity
            
            
            # BALANÇO DE POTÊNCIA NO BARRAMENTO DC
            prob += (
                    k_pv_3th[k]*self.Datas.I_3th.loc[k, 'pv_forecast'] + 
                    p_bat_3th_dis[k]
                    ==
                    self.Datas.I_3th.loc[k, 'load_forecast'] + 
                    p_bat_3th_ch[k]
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
            raise("Online Infactivel")
        
        
        
        ''' ------------------------------------------------------------------------------- 
        SALVA OS DADOS DA OTIMIZAÇÃO
        --------------------------------------------------------------------------------'''
        for k in range(0, self.Datas.NP_3TH):
            self.Datas.R_3th.loc[k , 'p_bat_3th']  = p_bat_3th_dis[k].varValue - p_bat_3th_ch[k].varValue
            self.Datas.R_3th.loc[k , 'k_pv_3th']   = k_pv_3th[k].varvalue
            
            
            
        
    
    