# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 18:23:10 2023

@author: Wesley
"""

import cvxpy as cp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd



constants = pd.DataFrame({'Np': [24],
                          'ts': [0.083],
                          'q_bat': [12], # kWh
                          'soc_bat_max': [0.95],
                          'soc_bat_min': [0.2],
                          'soc_bat_ini': [0.90],
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

p_grid_max = 150  # Capacidade da rede da concessionária em kWh

p_load = np.array([-80, -85, -90, -85, -80, -75, -70, -70, -75, -80, -85, -90, -95, -100, -110, -120, -130, -140, -135, -130, -125, -120, -110, -100])  # Exemplo de demanda em kWh
p_pv = np.array([30, 25, 20, 15, 10, 5, 8, 15, 25, 35, 40, 45, 50, 60, 70, 80, 90, 100, 80, 60, 40, 20, 15, 10])  # Exemplo de geração do PV em kWh

# Variáveis de otimização
p_bat = cp.Variable(Np)
soc_bat = cp.Variable(Np)
p_grid = cp.Variable(Np)

# Problema de otimização
objective = cp.Minimize(cp.sum_squares(p_grid) + cp.sum_squares(p_bat))
constraints = []

for t in time_steps:

    # Balanço de potência
    constraints.append(p_pv[t] + p_bat[t] + p_grid[t] + p_load[t] == 0)

    # SOC da bateria
    if t > 0:
        constraints.append(soc_bat[t] == soc_bat[t-1] - p_bat[t]*ts/q_bat)

problem = cp.Problem(objective, constraints)
problem.solve()

# Exibindo resultados
for t in time_steps:
    print("Hora {}:".format(t))
    print("p_load: {:.2f} kWh".format(p_load[t]))
    print("p_bat: {:.2f} kWh".format(p_bat.value[t]))
    print("Geração do PV: {:.2f} kWh".format(p_pv[t]))
    print("Importação da Rede: {:.2f} kWh".format(p_grid.value[t]))
    print()



print("Custo Total:", problem.value)



# Criando gráfico das potências
battery_power = np.array([p_bat.value[t] for t in time_steps])
grid_power = np.array([p_grid.value[t] for t in time_steps])


plt.figure(figsize=(10, 5))
plt.plot(time_steps, battery_power, marker='o', linestyle='-', color='b', label='Bateria')
plt.plot(time_steps, p_pv, marker='o', linestyle='-', color='orange', label='PV')
plt.plot(time_steps, grid_power, marker='o', linestyle='-', color='r', label='Rede')
plt.plot(time_steps, p_load, marker='o', linestyle='-', color='g', label='Carga')


plt.axhline(0, color='black', linestyle='--')
plt.xlabel('Hora')
plt.ylabel('Potência (kWh)')
plt.title('Potências na Microrrede')
plt.legend()
plt.grid()
plt.show()

print("Custo Total:", problem.value)