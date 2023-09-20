# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 18:23:10 2023

@author: Wesley
"""

import cvxpy as cp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time


R = pd.DataFrame({'p_bat_ref': [0]*24})
R2 = pd.DataFrame({'p_bat_ref': [0]*24})

constants = pd.DataFrame({'Np': [24],
                          'ts': [1],
                          'q_bat': [12], # kWh
                          'soc_bat_max': [0.95],
                          'soc_bat_min': [0.2],
                          'soc_bat_ini': [0.8],
                          'p_bat_max': [12],
                          'p_max_grid': [20],
                          'bay_pass_pv_forecast': 1,
                          'k_pv_ref': 1,
                          'Peso_k_pv': 0.05,
                          'Peso_delta_est': 0.45,
                          'Peso_ref_est': 0.45,
                          'Peso_ref_SC': 0.05})


# Parâmetros da microrrede
ts = constants.loc[0, 'ts']
Np = constants.loc[0, 'Np']
time_steps = list(range(Np))

q_bat = constants.loc[0, 'q_bat']
p_bat_max = constants.loc[0, 'p_bat_max']
soc_bat_max = constants.loc[0, 'soc_bat_max']
soc_bat_min = constants.loc[0, 'soc_bat_min']
soc_bat_ini = constants.loc[0, 'soc_bat_ini']


p_load = np.array([-80, -85, -90, -85, -80, -75, -70, -70, -75, -80, -85, -90, -95, -100, -110, -120, -130, -140, -135, -130, -125, -120, -110, -100])  # Exemplo de demanda em kWh
p_pv = np.array([0, 0, 0, 0, 0, 0, 3, 12, 25, 35, 40, 45, 50, 60, 50, 40, 10, 7, 0, 0, 0, 0, 0, 0])  # Exemplo de geração do PV em kWh

# Variáveis de otimização
p_bat = cp.Variable(Np)
soc_bat = cp.Variable(Np)
p_grid = cp.Variable(Np)

# Problema de otimização
objective = cp.Minimize(cp.sum_squares(p_grid) + cp.sum_squares(p_bat))
constraints = []

start_time = time.time()

R_problem_3th = pd.DataFrame({'FO': [0]*24,
                           'P1': [0.0]*24,
                           'P2': [0.0]*24})

for t in time_steps:

    # Balanço de potência
    constraints.append(p_pv[t] + p_bat[t] + p_grid[t] + p_load[t] == 0)

    # SOC da bateria
    if t == 0:
        constraints.append(soc_bat[t] == soc_bat_ini)
    else:
        constraints.append(soc_bat[t] == soc_bat[t-1] - p_bat[t]*ts/q_bat)
    
    
    # Technical constrains
    constraints.append(p_grid[t] <= 150)
    constraints.append(p_grid[t] >= -150)
    constraints.append(soc_bat[t] >= 0.2)
    constraints.append(soc_bat[t] <= 0.9)
    constraints.append(p_bat[t] >= -80)
    constraints.append(p_bat[t] <= 80)
    
    
problem = cp.Problem(objective, constraints)
problem.solve(solver=cp.ECOS)

end_time = time.time()
# Calcula o tempo de execução
execution_time = end_time - start_time


R.loc[:, 'p_bat_ref'] = p_bat.value[:]
print(R['p_bat_ref'])

R.loc[:, 'soc_bat'] = soc_bat.value[:]
print(R['soc_bat'])

# Exibindo resultados
for t in time_steps:
    print("Hora {}:".format(t))
    print("p_load: {:.2f} kWh".format(p_load[t]))
    print("p_bat: {:.2f} kWh".format(p_bat.value[t]))
    print("Geração do PV: {:.2f} kWh".format(p_pv[t]))
    print("Importação da Rede: {:.2f} kWh".format(p_grid.value[t]))
    print()



print("Custo Total:", problem.value)

print("Tempo de execução:", execution_time, "segundos")

# Criando gráfico das potências
battery_power = np.array([p_bat.value[t] for t in time_steps])
grid_power = np.array([p_grid.value[t] for t in time_steps])
soc_battery = np.array([soc_bat.value[t] for t in time_steps])


        # Optimization Result
for i in range(0, 24):
    R_problem_3th.loc[i, 'p_bat_ref'] = p_bat.value[i]
    R_problem_3th.loc[i, 'p_grid_ref'] = p_grid.value[i]
    R_problem_3th.loc[i, 'soc_bat_ref'] = soc_bat.value[i]
    

plt.figure(figsize=(10, 5))
plt.plot(time_steps, R_problem_3th.loc[:, 'p_bat_ref'], marker='o', linestyle='-', color='b', label='Bateria')
plt.plot(time_steps, p_pv, marker='o', linestyle='-', color='orange', label='PV')
plt.plot(time_steps, R_problem_3th.loc[:, 'p_grid_ref'], marker='o', linestyle='-', color='r', label='Rede')
plt.plot(time_steps, p_load, marker='o', linestyle='-', color='g', label='Carga')
plt.axhline(0, color='black', linestyle='--')
plt.xlabel('Hora')
plt.ylabel('Potência (kW)')
plt.title('Potências na Microrrede')
plt.legend()
plt.grid()

plt.figure(figsize=(10, 5))
plt.plot(time_steps, soc_battery, marker='o', linestyle='-', color='b', label='soc_bat')
plt.axhline(0, color='black', linestyle='--')
plt.xlabel('Hora')
plt.ylabel('SOC (%)')
plt.title('Estado de Carga da Bateria')
plt.legend()
plt.grid()
plt.show()


plt.show()

print("Custo Total:", problem.value)