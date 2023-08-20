# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 18:23:10 2023

@author: Wesley
"""

import cvxpy as cp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd



constants = pd.DataFrame({'np': [288],
                          'qtd_ciclos_para_rodar_mpc': [288],
                          'ts': [0.083],
                          'q_bat': [12], # kWh
                          'soc_max': [0.95],
                          'soc_min': [0.2],
                          'soc_ini': [0.90],
                          'p_bat_max': [12],
                          'soc_ref_est': [0.90],
                          'q_sc': [0.289], # kWh
                          'soc_max_sc': [0.95],
                          'soc_min_sc': [0.05],
                          'soc_ini_sc': [0.5],
                          'p_max_sc': [13],
                          'soc_ref_sc': [0.5],
                          'eff_conv': [1],
                          'eff_conv_sc': [1],
                          'p_max_inv_ac': [20],
                          'p_max_rede_exp': [20],
                          'p_max_rede_imp': [20],
                          'bay_pass_pv_forecast': 1,
                          'k_pv_ref': 1,
                          'Peso_k_pv': 0.05,
                          'Peso_delta_est': 0.45,
                          'Peso_ref_est': 0.45,
                          'Peso_ref_SC': 0.05})


# Parâmetros da microrrede
np = constants.loc[0, 'np']
time_steps = list(range(np))

p_bat_max = constants.loc[0, 'p_bat_max']
soc_bat_max = constants.loc[0, 'soc_bat_max']
soc_bat_min = constants.loc[0, 'soc_bat_min']

p_sc_max = constants.loc[0, 'p_sc_max']
soc_bat_max = constants.loc[0, 'soc_bat_max']
soc_bat_min = constants.loc[0, 'soc_bat_min']

p_grid_max = 150  # Capacidade da rede da concessionária em kWh

p_load = np.array([80, 85, 90, 85, 80, 75, 70, 70, 75, 80, 85, 90, 95, 100, 110, 120, 130, 140, 135, 130, 125, 120, 110, 100])  # Exemplo de demanda em kWh
p_pv = np.array([30, 25, 20, 15, 10, 5, 8, 15, 25, 35, 40, 45, 50, 60, 70, 80, 90, 100, 80, 60, 40, 20, 15, 10])  # Exemplo de geração do PV em kWh

# Variáveis de otimização
p_bat = cp.Variable(np)
p_sc = cp.Variable(np)
p_grid = cp.Variable(np)

# Problema de otimização
objective = cp.Minimize(cp.sum_squares(p_grid) + cp.sum_squares(p_bat))
constraints = []

for t in time_steps:

    # Balanço de potência
    power_balance = p_pv[t] + p_bat[t] + p_sc[t] + p_grid[t] - p_load[t]
    constraints.append(power_balance == 0)

    # Armazenamento máximo
    constraints.append(P_bat[t] <= soc_bat)
    constraints.append(supercapacitor_energy[t] <= supercapacitor_capacity)

problem = cp.Problem(objective, constraints)
problem.solve()

# Exibindo resultados
for t in time_steps:
    print(f"Hora {t}:")
    print(f"Demand: {demand[t]:.2f} kWh")
    print(f"Bateria: {P_bat.value[t]:.2f} kWh")
    print(f"Supercapacitor: {supercapacitor_energy.value[t]:.2f} kWh")
    print(f"Geração do PV: {pv_generation_input[t]:.2f} kWh")
    print(f"Importação da Rede: {grid_import.value[t]:.2f} kWh")
    print()



print("Custo Total:", problem.value)



# Criando gráfico das potências
battery_power = np.array([P_bat.value[t] - P_bat.value[t-1] if t > 0 else P_bat.value[t] for t in time_steps])
supercap_power = np.array([supercapacitor_energy.value[t] - supercapacitor_energy.value[t-1] if t > 0 else supercapacitor_energy.value[t] for t in time_steps])
pv_power = pv_generation_input  # Considerando que o PV está entrando na microrrede
grid_power = -grid_import.value

plt.figure(figsize=(10, 5))
plt.plot(time_steps, battery_power, marker='o', linestyle='-', color='b', label='Bateria')
plt.plot(time_steps, supercap_power, marker='o', linestyle='-', color='g', label='Supercapacitor')
plt.plot(time_steps, pv_power, marker='o', linestyle='-', color='orange', label='PV')
plt.plot(time_steps, grid_power, marker='o', linestyle='-', color='r', label='Rede (Importação)')
plt.axhline(0, color='black', linestyle='--')
plt.xlabel('Hora')
plt.ylabel('Potência (kWh)')
plt.title('Potências na Microrrede')
plt.legend()
plt.grid()
plt.show()

print("Custo Total:", problem.value)