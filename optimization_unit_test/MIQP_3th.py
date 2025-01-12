import cvxpy as cp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Datas:
    def __init__(self):
        
        
        # Operation mode
        # self.operation_mode = "CONNECTED"
        self.operation_mode = "ISOLATED"
        
        # Optmization method
        self.optimization_method = "QP"
        # self.optimization_method = "MILP"
        
        # Paths for files
        self.pv_path = "PV_model"
        self.load_path = "Load_model"
        
        # Time constants
        self.NP_2TH         = 15 # seconds
        self.NP_3TH         = 24 # minutes
        self.TS_2TH         = 1 # seconds
        self.TS_3TH         = 1 # seconds
        self.TS_MEASUREMENT = 1 # seconds
        self.TS_FORECAST    = 1 # minutes

        # Technical specification constants
        # bat
        self.Q_BAT         = int(120)
        self.SOC_BAT_MIN   = 0.2
        self.SOC_BAT_MAX   = float(0.95)
        self.P_BAT_MAX     = int(20)
        self.P_BAT_MIN     = int(-20)
        self.P_BAT_VAR_MAX = int(20)
        self.P_BAT_VAR_MIN = int(20)
        # sc
        self.SOC_SC_MIN = 0.2
        self.SOC_SC_MAX = float(0.95)
        self.P_SC_MAX   = int(20)
        self.P_SC_MIN   = int(-20)
        # grid
        self.P_GRID_MAX = int(50)
        self.P_GRID_MIN = int(-50)

        # Constansts references for optimization
        self.SOC_SC_REF  = 0.5
        self.SOC_BAT_REF = 0.8
        self.K_PV_REF    = 1
              
        # Measurements (Init values)
        self.soc_bat = 0.5
        self.soc_sc  = float(0.5)
        self.p_pv    = float(0)
        self.p_load  = float(-2)
        self.p_grid  = float(0)
        self.p_bat   = float(0)
        self.p_sc    = float(0)
        
        # Scheduled (Calculated by 3th)
        self.p_bat_sch  = 0
        self.p_grid_sch = 0
        self.k_pv_sch   = 0
        
        # References (Calculated by 2th)
        self.p_bat_ref  = 0
        self.p_grid_ref = 0
        self.k_pv_ref   = 0

def isolated_optimization_3th(Datas, pv_forecasted, load_forecasted):
        print("isolated Optimization in 3th")
        
        # WEIGHTs for objective function
        # 3th
        WEIGHT_K_PV      = 1
        WEIGHT_DELTA_BAT = 0.1
        WEIGHT_SOC_BAT   = 1
        
        # Optimization variables
        # Bat
        p_bat          = cp.Variable(Datas.NP_3TH)
        p_bat_ch       = cp.Variable(Datas.NP_3TH)
        p_bat_dis      = cp.Variable(Datas.NP_3TH)
        flag_p_bat_ch  = cp.Variable(Datas.NP_3TH, boolean = True)
        flag_p_bat_dis = cp.Variable(Datas.NP_3TH, boolean = True)
        soc_bat        = cp.Variable(Datas.NP_3TH)
        delta_p_bat    = cp.Variable(Datas.NP_3TH)
        # PV
        k_pv           = cp.Variable(Datas.NP_3TH)
        
        # Objective function
        objective = cp.Minimize(cp.sum_squares(k_pv[0:Datas.NP_3TH] - Datas.K_PV_REF)       * WEIGHT_K_PV       +
                                cp.sum_squares(delta_p_bat[0:Datas.NP_3TH])                 * WEIGHT_DELTA_BAT  +
                                cp.sum_squares(soc_bat[1:Datas.NP_3TH] - Datas.SOC_BAT_REF) * WEIGHT_SOC_BAT)
        
        # Constraints
        constraints = []
        # MPC LOOP
        for k in range(0, Datas.NP_3TH):
            
            # Power balance
            constraints.append(p_bat[k] + k_pv[k]*pv_forecasted.loc[k, 'data'] - load_forecasted.loc[k, 'data'] == 0)
            
            # Battery SOC
            if k == 0:
                constraints.append(soc_bat[k]     == Datas.soc_bat) # SOC now
                constraints.append(delta_p_bat[k] == p_bat[k] - Datas.p_bat)
            else:
            # if k > 0:
                constraints.append(soc_bat[k]     == soc_bat[k-1] - p_bat[k-1]*Datas.TS_3TH/Datas.Q_BAT)
                constraints.append(delta_p_bat[k] == p_bat[k] - p_bat[k-1])
            
            # Technical constrains
            # SOC bat
            constraints.append(soc_bat[k] >= Datas.SOC_BAT_MIN)
            constraints.append(soc_bat[k] <= Datas.SOC_BAT_MAX)
            # P_bat
            constraints.append(p_bat_ch[k]                          >= 0)
            constraints.append(p_bat_ch[k]       <= Datas.P_BAT_MAX * flag_p_bat_ch[k])
            constraints.append(p_bat_dis[k]                         >= 0)
            constraints.append(p_bat_dis[k]     <= Datas.P_BAT_MAX * flag_p_bat_dis[k])
            constraints.append(p_bat[k]                             >= Datas.P_BAT_MIN)
            constraints.append(p_bat[k]                             <= Datas.P_BAT_MAX)
            constraints.append(p_bat[k]                             == p_bat_dis[k] - p_bat_ch[k])
            constraints.append(flag_p_bat_ch[k] + flag_p_bat_dis[k] <= 1)
            # k_pv
            constraints.append(k_pv[k] >= 0)
            constraints.append(k_pv[k] <= 1)

        # SOLVER
        problem = cp.Problem(objective, constraints)
        # problem.solve(solver=cp.CBC)
        problem.solve(solver=cp.SCIP, verbose = True)
        
        if problem.status == cp.OPTIMAL:
            print("OTIMO")
            # Results
            results_3th = pd.DataFrame(index=range(Datas.NP_3TH), columns=['p_bat_sch', 'k_pv_sch', 'soc_bat'])
            OF_3th      = 0
            for k in range(0, Datas.NP_3TH):
                results_3th.loc[k, 'p_bat_sch']   = p_bat.value[k]
                results_3th.loc[k, 'k_pv_sch']    = k_pv.value[k]
                # results_3th.loc[0, 'p_grid_sch']  = p_grid.value[k]
                results_3th.loc[k, 'soc_bat']    = soc_bat.value[k]
                
            OF_3th = problem.value
            print(type(results_3th))
            return results_3th, OF_3th
        else:
            print("ENGASGOU")
            return None, None



p_load1 = np.array([3, 3, 3, 3, 3, 3, 3, 5, 5, 5, 4, 5, 3, 5, 5, 5, 5, 4, 8, 8, 7, 1, 1, 1])  # Exemplo de demanda em kWh
p_pv1 = np.array([0, 0, 0, 0, 0, 0, 1, 1, 2, 3, 4, 5, 5, 6, 7, 8, 9, 10, 8, 0, 0, 0, 0, 0])  # Exemplo de geração do PV em kWh

p_load = pd.DataFrame(p_load1, columns=['data'])
p_pv = pd.DataFrame(p_pv1, columns=['data'])
Datas = Datas()


results_3th, OF_3th  = isolated_optimization_3th(Datas, p_pv, p_load)

k_pv_m_p_pv = pd.DataFrame(index=range(Datas.NP_3TH), columns=['data'])
k_pv_sch = pd.DataFrame(index=range(Datas.NP_3TH), columns=['data'])
power_balance = pd.DataFrame(index=range(Datas.NP_3TH), columns=['data'])
p_bat = pd.DataFrame(index=range(Datas.NP_3TH), columns=['data'])
soc_bat = pd.DataFrame(index=range(Datas.NP_3TH), columns=['data'])


for k in range(0, Datas.NP_3TH):
    k_pv_m_p_pv.loc[k, 'data'] = p_pv.loc[k, 'data'] * results_3th.loc[k, 'k_pv_sch']
    k_pv_sch.loc[k, 'data'] = results_3th.loc[k, 'k_pv_sch']
    p_bat.loc[k,'data'] = results_3th.loc[k, 'p_bat_sch']
    power_balance.loc[k, 'data'] = p_bat.loc[k,'data'] + k_pv_m_p_pv.loc[k, 'data'] - p_load.loc[k,'data']
    soc_bat.loc[k,'data'] = results_3th.loc[k, 'soc_bat']

time_stamp = list(range(Datas.NP_3TH))
plt.figure(figsize=(10, 5))
plt.plot(p_bat['data'].values, label = 'p_bat_sch')
plt.plot(k_pv_m_p_pv['data'].values, label = 'k_pv_m_p_pv')
plt.plot(p_pv['data'], label = 'p_pv')
plt.plot(p_load['data'].values, label = 'p_load')
plt.plot(power_balance['data'], label = 'power_balance')
plt.legend()

plt.figure(figsize=(10, 5))
plt.plot(soc_bat['data'].values, label = 'soc_bat')
plt.plot(k_pv_sch['data'].values, label = 'k_pv_sch')
plt.legend()
plt.show()
