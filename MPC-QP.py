"""
Created on Sat Aug 22 21:39:00 2023

@author: Wesley
"""

import time
from optimization_qp import OptimizationQP

class OptimizationProcess(OptimizationQP):
    def __init__(self, constants):
        super().__init__()
        self.stop_mpc = False
        self.data = []
        self.time_sleep = constants.loc[0, 'time_sleep']
        self.sampling_time_secondary = constants.loc[0, 'sampling_time_secondary']
        self.sampling_time_measurement = constants.loc[0, 'sampling_time_measurement']
        self.sampling_time_terciary = constants.loc[0, 'sampling_time_terciary']

    def get_measurements(self):
        # Simula a captura de dados
        print("Capturando medidas...")
        return [1, 2, 3, 4, 5]

    def run(self):
        start_time = time.time()
        current_time = time.time()
        last_time_measurement = current_time
        last_time_secundary = current_time
        last_time_terciary = current_time

        while not self.stop_mpc:
            time.sleep(self.time_sleep)
            current_time = time.time()

            # Verifica se é hora de capturar medidas
            if current_time - last_time_measurement >= self.sampling_time_measurement:
                print("Call self.get_measurements()")
                self.get_measurements()
            current_time = time.time()

            # Verifica se é hora da otimização terciária
            if current_time - last_time_terciary >= self.sampling_time_terciary:
                self.tertiary_optimization()
            current_time = time.time()

            # Verifica se é hora da otimização secundária
            if current_time -  last_time_secundary >= self.sampling_time_secondary:
                self.secondary_optimization()

            # Exemplo de condição de parar
            if stop():
                self.stop_mpc = True

    def stop(self):
        self.stop_mpc = True

