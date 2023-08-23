"""
Created on Sat Aug 22 21:39:00 2023

@author: Wesley
"""

import time
from optimization_qp import OptimizationQP

class OptimizationProcess(OptimizationQP):
    def __init__(self):
        super().__init__()
        self.stop_condition = False
        self.data = []

    def get_measurements(self):
        # Simula a captura de dados
        print("Capturando medidas...")
        return [1, 2, 3, 4, 5]

    def run(self):
        while not self.stop_condition:
            start_time = time.time()

            # Verifica se é hora de capturar medidas
            if start_time % 5 == 0:  # Exemplo hipotético de condição
                self.data.extend(self.get_measurements())

            # Verifica se é hora de otimização terciária
            if start_time % 10 == 0:  # Exemplo hipotético de condição
                self.data = self.tertiary_optimization(self.data)

            # Verifica se é hora de otimização secundária
            if start_time % 15 == 0:  # Exemplo hipotético de condição
                self.data = self.secondary_optimization(self.data)

            # Exemplo de condição de parada
            if len(self.data) >= 50:  # Exemplo hipotético de condição de parada
                self.stop_condition = True

            time.sleep(1)  # Espera por 1 segundo antes da próxima iteração

# Criar uma instância da classe e executar o processo de otimização
optimization_process = OptimizationProcess()
optimization_process.run()
