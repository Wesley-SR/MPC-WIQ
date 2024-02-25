# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 11:45:23 2024

@author: wesle
"""

import pybamm
import matplotlib.pyplot as plt

# Configurar parâmetros da bateria
parameter_values = pybamm.ParameterValues(
    chemistry=pybamm.parameter_sets.Ecker2015,
    current_collector=pybamm.parameter_sets.Xu2019,
    temperature=273.15 + 25,  # 25°C
    current_function=pybamm.GetConstantCurrent(30),  # Carregar a bateria com 30 kW
    # Adicionar parâmetros personalizados
    options={
        "Maximum power": 30,   # Potência máxima em kW
        "Maximum capacity": 100,  # Capacidade máxima em Ah (carga máxima)
        "Minimum SOC": 0.1,  # Estado de carga mínimo (10%)
        "Maximum SOC": 0.9,  # Estado de carga máximo (90%)
    }
)

# Configurar o modelo de bateria com os parâmetros
model = pybamm.lithium_ion.DFN(parameters=parameter_values)

# Criar uma malha temporal
time_mesh = pybamm.MeshGenerator(pybamm.Geometry(), pybamm.SubMesh1D(mesh=[])).uniform_mesh(0, 1, 0.1)

# Resolver o sistema de equações diferenciais
solver = pybamm.CasadiSolver()
solution = solver.solve(model, time_mesh)

# Plotar os resultados
output_variables = [
    "Current collector current density",
    "Terminal voltage",
    "Negative particle surface concentration",
    "Positive particle surface concentration",
    "State of Charge",
]

pybamm.plot(solution, output_variables=output_variables)
plt.show()
