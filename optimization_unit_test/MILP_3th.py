import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datas import Datas
from OptimizationMILP import OptimizationMILP

MilpOptimization = OptimizationMILP()

# p_pv_forecast   = np.array([0.1, 0.00, 0.00, 0.00, 0.1, 0.08, 0.10, 0.1, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.07, 0.05, 0.04, 0.05, 0.0, 0.00, 0.00, 0.00, 0.00, 0.00])  # Exemplo de geração do PV em kWh
# p_load_forecast = np.array([0.1, 0.15, 0.16, 0.19, 0.2, 0.25, 0.29, 0.3, 0.25, 0.22, 0.19, 0.18, 0.15, 0.14, 0.18, 0.19, 0.05, 0.09, 0.1, 0.12, 0.18, 0.12, 0.12, 0.12])  # Exemplo de demanda em kWh

# p_pv = pd.DataFrame(p_pv_forecast, columns=['data'])
# p_load = pd.DataFrame(p_load_forecast, columns=['data'])

Datas = Datas()
Datas.update_past_datas()

p_pv = pd.DataFrame({'data': [0.0]*Datas.NP_3TH})
p_load = pd.DataFrame({'data': [0.0]*Datas.NP_3TH})

p_pv.loc[0:Datas.NP_3TH-1, 'data'] = Datas.P_3th.loc[0:Datas.NP_3TH, 'p_pv']
p_load.loc[0:Datas.NP_3TH-1, 'data'] = Datas.P_3th.loc[0:Datas.NP_3TH, 'p_load']


start_time = time.time()
results_3th, OF_3th  = MilpOptimization.isolated_optimization_3th(Datas, p_pv, p_load)
end_time = time.time()
execution_time = end_time - start_time
print(f"execution_time: {execution_time}")

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
plt.plot(p_pv['data'], label = 'p_pv', linestyle = ':')
plt.plot(-p_load['data'].values, label = 'p_load',color='#8B0000', linestyle = '--')
plt.plot(p_load['data'].values, label = 'p_load',color='#8B0000', linestyle = '--', linewidth = 0.5)
plt.plot(power_balance['data'], label = 'power_balance')
plt.legend()

plt.figure(figsize=(10, 5))
plt.plot(soc_bat['data'].values, label = 'soc_bat')
plt.plot(k_pv_sch['data'].values, label = 'k_pv_sch')
plt.legend()
plt.show()