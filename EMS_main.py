"""
Created on Sat Aug 22 21:39:00 2023

@author: Wesley
"""

#TODO: To download and to test the PVLIB and PyBaMM libraries!

# Python libs
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import modbus_comunication.modbus_client_cs2mb

# My libs
from OptimizationQP import OptimizationQP
from Datas import Datas
from ForecastMm import run_forecast_mm

# Modbus
from pyModbusTCP.client import ModbusClient



class EMS():
    def __init__(self):

        self.Datas = Datas()
        print(self.Datas.I_3th.loc[0, 'pv_forecast'])
        
        self.stop_mpc = False
        # Last Time
        self.last_time_measurement = 0
        self.last_time_2th = 0
        self.last_time_3th = 0
        
        self.connected_mode = 1
        # 0 -> QP.   Connected mode.
        # 1 -> QP.   Islanded mode.
        # 2 -> MILP. Connected mode.
        # 3 -> MILP. Islanded mode.
        
        self.qp_optimization = OptimizationQP(self.Datas)
        # self.milp_optimization = OptimizationMILP(self.Datas)
        
        self.host = 'localhost'
        self.port = 502
        self.client_ID = 2
        try:
            self.modbus_client = ModbusClient(host = self.host, port = self.port, unit_id = self.client_ID, debug=False, auto_open=True)
        except Exception as error:
            print("Erro ao conectar o cliente Modbus: {}".format(e))
            self.modbus_client.close()
            break



    def run(self) -> None:

        while not self.stop_mpc:
            print("EMS init")
            
            time.sleep(self.Datas.TIME_SLEEP)

            # Check if staying in island mode or connected mode

            # Take measurements
            if (self.is_it_time_to_take_measurements()):
                self.get_measurements()


            # Run terciary optmization
            if (self.is_it_time_to_run_3th()):
                # Update past 3th data
                self.P_3th.iloc[0:self.Datas.NP_3TH-1] = self.P_3th.iloc[1:self.Datas.NP_3TH] # Descarta a amostra mais antiga
                self.P_3th.at[self.Datas.NP_3TH, 'p_pv'] = self.Datas.p_pv # Atualiza a ultima amostra do PV
                self.P_3th.at[self.Datas.NP_3TH, 'p_load'] = self.Datas.p_load # Atualiza a ultima amostra da carga
                
                # Update the first row of the I_3th matrix
                self.Datas.I_3th.loc[0, 'pv_forecast'] = self.Datas.p_pv
                self.Datas.I_3th.loc[0, 'load_forecast'] = self.Datas.p_load

                # Run 3th forecast
                self.Datas.I_3th.loc[1:, 'pv_forecast'] = run_forecast_mm(P_3th[:, 'p_pv'])
                
                # Run optmization 3th
                self.run_3th_optimization()

            # Run 2th optmization
            if (self.is_it_time_to_run_2th()):
                # Update past 2th data
                self.P_2th.iloc[0:self.Datas.NP_2TH-1] = self.P_2th.iloc[1:self.Datas.NP_2TH] # Descarta a amostra mais antiga
                self.P_2th.at[self.Datas.NP_2TH, 'p_pv'] = self.Datas.p_pv # Atualiza a última amostra do PV
                self.P_2th.at[self.Datas.NP_2TH, 'p_load'] = self.Datas.p_load # Atualiza a última amostra da carga
                
                # Assumes the same value for the entire forecast horizon
                self.Datas.I_2th.loc['pv_forecast'] = self.Datas.p_pv
                self.Datas.I_2th.loc['load_forecast'] = self.Datas.p_load
                
                # Updates reference signals
                self.Datas.I_2th.loc['p_bat_ref'] = self.Datas.R_3th.loc[self.Datas.NP_3TH, 'p_bat_3th']
                self.Datas.I_2th.loc['p_bat_ref'] = self.Datas.R_3th.loc[self.Datas.NP_3TH, 'p_bat_3th']
                
                # Run optimization 2th
                self.run_2th_optimization()

            # Check if it's time to stop the code
            self.stop_mpc = True # Test for now
            if self.stop():
                break
            
        
        self.plot_result()
        return self.Datas.I_3th, self.Datas.R_3th




    def is_it_time_to_take_measurements(self) -> bool:
        current_time = time.time()
        
        if (current_time - self.last_time_measurement >= self.Datas.TS_MEASUREMENT):
            print("It's time to measurement")
            self.last_time_measurement = current_time
            return True
        else:
            return False





    def is_it_time_to_run_3th(self) -> bool:
        current_time = time.time()
        if (current_time - self.last_time_3th >= self.Datas.TS_3TH):
            print("It's time to 3th")
            self.last_time_3th = current_time
            return True
        else:
            return False





    def is_it_time_to_run_2th(self) -> bool:
        current_time = time.time()
        if (current_time - self.last_time_2th >= self.Datas.TS_2TH):
            print("It's time to 2th")
            self.last_time_2th = current_time
            return True
        else:
            return False





    def run_2th_optimization(self) -> None:
        
        # Update the first row of the I_2th matrix
        self.Datas.I_2th.loc[:, 'pv_forecast'] = self.Datas.p_pv
        self.Datas.I_2th.loc[:, 'load_forecast'] = self.Datas.p_load
        
        # Call optimization
        if (self.connected_mode):
            self.qp_optimization.connected_optimization_2th()
        else:
            self.qp_optimization.islanded_optimization_2th()




    def run_3th_optimization(self) -> None:       
        # Call optimization
        if (self.connected_mode):
            self.qp_optimization.connected_optimization_3th()
        else:
            self.qp_optimization.islanded_optimization_3th()




    
    def get_measurements(self) -> None:
        # Simula a captura de dados
        # TODO: Talvez eu possa criar uma thread para ficar lendo os dados e atualizando
        registers = self.modbus_client.read_holding_registers(0, 9)
        
        if registers:
            self.Datas.p_pv = registers[2]/1000
            self.Datas.p_load = registers[3]/1000
            self.Datas.p_grid = registers[4]/1000
            self.Datas.p_bat = registers[5]/1000
            self.Datas.p_sc = registers[6]/1000
            self.Datas.soc_bat = registers[7]/1000
            self.Datas.soc_sc = registers[8]/1000


    def get_forecast_pv(self) -> None:
        p_pv = np.array([0, 0, 0, 0, 0, 0, 3, 12, 25, 35, 40, 45, 50, 60, 50, 40, 10, 7, 0, 0, 0, 0, 0, 0])  # Exemplo de geração do PV em kWh
        self.Datas.I_3th.loc[1:, 'pv_forecast'] = p_pv[1:]
        



    def get_forecast_load(self) -> None:
        p_load = np.array([-0, -5, -13, -20, -40, -45, -65, -35, -38, -20, -18, -40, -48, -56, -70, -50, -40, -40, -35, -32, -27, -25, -20, -15])  # Exemplo de demanda em kWh
        self.Datas.I_3th.loc[1:, 'load_forecast'] = p_load[1:]
        




    def stop(self) -> None:
        return self.stop_mpc





    def plot_result(self) -> None:
        time_steps = list(range(self.Datas.NP_3TH))
        
        plt.figure(figsize=(10, 5))
        
        if (self.connected_mode):
            print("Plot p_grid")
            plt.plot(time_steps, self.Datas.R_3th.loc[:, 'p_grid_3th'], marker='o', linestyle='-', color='r', label='Grid')
        
        plt.plot(time_steps, self.Datas.R_3th.loc[:, 'p_bat_3th'], marker='o', linestyle='-', color='b', label='Battery')
        plt.plot(time_steps, self.Datas.I_3th.loc[:, 'pv_forecast'], marker='o', linestyle='-', color='orange', label='PV')
        plt.plot(time_steps, self.Datas.I_3th.loc[:, 'load_forecast'], marker='o', linestyle='-', color='g', label='Load')
        plt.plot(time_steps, self.Datas.I_3th.loc[:, 'pv_forecast']*self.Datas.R_3th.loc[:, 'k_pv_3th'], linestyle='-', color='orange', label='Load')
        plt.axhline(0, color='black', linestyle='--')
        plt.xlabel('Time (h)')
        plt.ylabel('Power (kW)')
        plt.title('Microgrid power')
        plt.legend()
        plt.grid()

        plt.figure(figsize=(10, 5))
        if (not self.connected_mode):
            plt.plot(time_steps, self.Datas.R_3th.loc[:, 'k_pv_3th'], marker='o', linestyle='-', color='r', label='k_pv_3th')
        
        plt.plot(time_steps, self.Datas.R_3th.loc[:, 'soc_bat_3th'], marker='o', linestyle='-', color='b', label='soc_bat')
        plt.axhline(0, color='black', linestyle='--')
        plt.xlabel('Hora')
        plt.ylabel('SOC (%)')
        plt.title('Estado de Carga da Bateria')
        plt.legend()
        plt.grid()
        plt.show()
        print("Custo Total:", self.Datas.R_3th.loc[0, 'FO'])
        
        
        
if __name__ == "__main__":

    EMS_instance = EMS()
    
    I_3th, R_3th = EMS_instance.run()