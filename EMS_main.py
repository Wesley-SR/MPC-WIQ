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
from pyModbusTCP.client import ModbusClient

# My libs
from OptimizationMIQP import OptimizationMIQP
from OptimizationMILP import OptimizationMILP
from datas import Datas
from ForecastingModel import ForecastingModel

# Modbus
from pyModbusTCP.client import ModbusClient

import mmpw




# *******************************************************
#      EMC CLASS                                        #
# *******************************************************
class EMS():
    def __init__(self):
        
        
        print("-------------------------")
        print("Initialization")
        # Create a object of datas
        self.Datas = Datas()
        
        # Execution variables
        self.run_mpc = True
        self.run_3th = True
        self.run_2th = False
        
        # Timers
        self.t = 96 # Time that start in matrix M (in simulation)
        # Last Timers
        self.last_time_measurement = 0
        self.last_time_2th = 0
        self.last_time_3th = 0

        # Create optimization object
        if self.Datas.optimization_method == "QP":
            self.qp_optimization = OptimizationMIQP(self.Datas) # With the parameter self.Datas, the OptimizationMIQP methods can edit the object Data
        elif self.Datas.optimization_method == "MILP":
            self.milp_optimization = OptimizationMILP(self.Datas)
        
        # Create Modbus object
        self.host = 'localhost'
        self.port = 502
        self.client_ID = 2
        try:
            self.modbus_client = ModbusClient(host = self.host, port = self.port, unit_id = self.client_ID, debug=False, auto_open=True)
        except Exception as e:
            print("Erros connecting Modbus Client: {}".format(e))
            self.modbus_client.close()
        self.counter_mb = 0

        # Forecasting models
        # self.forecast = ForecastingModel(self.Datas.pv_path, self.Datas.load_path)
        
        print("Initialized EMS")





    # =======================================================
    #      Main loop of MPC                                 #
    # =======================================================
    def run(self) -> None:
        
        print("Run MPC")
        
        while self.run_mpc:

            print(f"t = {self.t}")    

            # Take measurements
            if (self.is_it_time_to_take_measurements()):
                self.get_measurements()

            # Run terciary optmization
            if (self.is_it_time_to_run_3th() and self.run_3th):
                print("Update 3th data")
                # Update past 3th data
                self.Datas.P_3th.iloc[0:self.Datas.NP_3TH-1] = self.Datas.P_3th.iloc[1:self.Datas.NP_3TH] # Discart the oldest sample
                self.Datas.P_3th.at[self.Datas.NP_3TH, 'p_pv'] = self.Datas.p_pv # Update the new PV sample with the actual data
                self.Datas.P_3th.at[self.Datas.NP_3TH, 'p_load'] = self.Datas.p_load # Update the new load sample with the actual data
                
                print(f"p_pv mensuremented: {self.Datas.P_3th.at[self.Datas.NP_3TH, 'p_pv']}")
                print(f"p_load mensuremented: {self.Datas.P_3th.at[self.Datas.NP_3TH, 'p_load']}")
                
                # Update the first row of the I_3th matrix
                ## The first row of the I_3th matrix is a measurement.
                self.Datas.I_3th.loc[0, 'pv_forecast'] = self.Datas.p_pv
                self.Datas.I_3th.loc[0, 'load_forecast'] = self.Datas.p_load

                # Run 3th forecast
                # self.Datas.I_3th.loc[1:, 'pv_forecast']   = self.forecast.predict_pv(self.Datas.P_3th[:, 'p_pv'])
                # self.Datas.I_3th.loc[1:, 'load_forecast'] = self.forecast.predict_load(self.Datas.P_3th[:, 'p_load'])
                self.Datas.I_3th.loc[1:, 'pv_forecast']   = mmpw(self.Datas.P_3th[:,'p_pv'])
                self.Datas.I_3th.loc[1:, 'load_forecast'] = mmpw(self.Datas.P_3th[:,'p_load'])
                
                # Run optmization 3th
                self.run_3th_optimization()

            # Run 2th optmization
            if (self.is_it_time_to_run_2th() and self.run_2th):
                # Update past 2th data
                self.Datas.P_2th.iloc[0:self.Datas.NP_2TH-1] = self.Datas.P_2th.iloc[1:self.Datas.NP_2TH] # Discart the oldest sample
                self.Datas.P_2th.at[self.Datas.NP_2TH, 'p_pv'] = self.Datas.p_pv # Update the new PV sample
                self.Datas.P_2th.at[self.Datas.NP_2TH, 'p_load'] = self.Datas.p_load # Update the new load sample
                
                # Assumes the same value for the entire forecast horizon
                self.Datas.I_2th.loc['pv_forecast'] = self.Datas.p_pv
                self.Datas.I_2th.loc['load_forecast'] = self.Datas.p_load
                
                # Updates reference signals
                self.Datas.I_2th.loc['p_bat_ref'] = self.Datas.R_3th.loc[self.Datas.NP_3TH, 'p_bat_3th']
                self.Datas.I_2th.loc['p_bat_ref'] = self.Datas.R_3th.loc[self.Datas.NP_3TH, 'p_bat_3th']
                
                # Run optimization 2th
                self.run_2th_optimization()
                
                self.send_control_signals()

            # Check if it's time to stop the code
            self.run_mpc = False # To run only a time
            if not self.run_mpc:
                break
        
            self.t = self.t + 1
            
        self.plot_result()
        return self.Datas





    # =======================================================
    #    # Auxiliaries functions                            #
    # =======================================================

    # Check if is time to take new measumerements for microgrid via Mudbus
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



    def run_3th_optimization(self) -> None:
        print("run_3th_optimization")
        # Call optimization
        if (self.Datas.operation_mode == "CONNECTED"):
            if (self.Datas.optimization_method == "QP"):
                self.qp_optimization.connected_optimization_3th()
            elif(self.Datas.optimization_method == "MILP"):
                # self.milp_optimization.connected_optimization_3th()
                print("Dont have connected MILP")

        elif (self.Datas.operation_mode == "ISOLATED"):
            if (self.Datas.optimization_method == "QP"):
                self.qp_optimization.isolated_optimization_3th()
            elif (self.Datas.optimization_method == "MILP"):
                self.milp_optimization.isolated_optimization_3th()
            else:
                print("Don't have optimization method")
                
        else:
            print("Don't have optimization method")



    def run_2th_optimization(self) -> None:
        # Update the first row of the I_2th matrix
        self.Datas.I_2th.loc[:, 'pv_forecast'] = self.Datas.p_pv
        self.Datas.I_2th.loc[:, 'load_forecast'] = self.Datas.p_load
        
        # Call optimization
        if (self.Datas.operation_mode == "CONNECTED"):
            if (self.Datas.optimization_method == "QP"):
                self.qp_optimization.connected_optimization_2th()
            elif (self.Datas.optimization_method == "MILP"):
                print("TODO: MILP Optimization")
                pass
        elif (self.Datas.operation_mode == "ISOLATED"):
            if (self.Datas.optimization_method == "QP"):
                self.qp_optimization.isolated_optimization_2th()
            elif (self.Datas.optimization_method == "MILP"):
                print("TODO: MILP Optimization")
                pass


    
    def get_measurements(self) -> None:
        print("get_measurements")
        wait_for_new_data = 1
        
        cmd_to_send_new_data = 1
        self.modbus_client.write_multiple_registers(0, [self.counter_mb, cmd_to_send_new_data])
        time.sleep(0.100)
        
        while wait_for_new_data == 0:
            print("Waiting for datas")
            registers = self.modbus_client.read_holding_registers(0, 9)
            
            # Check if we have new data
            cmd_to_send_new_data = int(registers[1])
            if cmd_to_send_new_data == 1:
                
                # Operation mode
                if (registers[2] == 1):
                    self.Datas.operation_mode = "CONNECTED"
                else:
                    self.Datas.operation_mode = "ISOLATED"
                
                # Datas from microgrid
                self.Datas.p_pv         = registers[3]/1000
                self.Datas.p_load       = registers[4]/1000
                self.Datas.p_grid       = registers[5]/1000
                self.Datas.p_bat        = registers[6]/1000
                self.Datas.p_sc         = registers[7]/1000
                self.Datas.soc_bat      = registers[8]/1000
                self.Datas.soc_sc       = registers[9]/1000
                
                print("Measurements \n")
                print(f'cmd_to_send_new_data:    {cmd_to_send_new_data} \n')
                print(f'operation_mode: {self.Datas.operation_mode} \n')
                print(f'p_pv:           {self.Datas.p_pv} \n')
                print(f'p_load:         {self.Datas.p_load} \n')
                print(f'p_grid:         {self.Datas.p_grid} \n')
                print(f'p_bat:          {self.Datas.p_bat} \n')
                print(f'p_sc:           {self.Datas.p_sc} \n')
                print(f'soc_bat:        {self.Datas.soc_bat} \n')
                print(f'soc_sc:         {self.Datas.soc_sc} \n\n')
                
                self.counter_mb += 1
                wait_for_new_data = 0
                
            time.sleep(0.5)
        


    def send_control_signals(self) -> None:
        control_signals = [self.Datas.R_2th.loc['p_bat_2th', 0],
                           self.Datas.R_2th.loc['p_sc_2th', 0],
                           self.Datas.R_2th.loc['p_grid_2th', 0],
                           self.Datas.R_2th.loc['k_pv', 0]]
        # self.modbus_client.write_multiple_registers(10, control_signals)
    



    def plot_result(self) -> None:
        time_steps = list(range(self.Datas.NP_3TH))
        
        plt.figure(figsize=(10, 5))
        
        if (self.Datas.operation_mode == "CONNECTED"):
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
        if (self.Datas.operation_mode == "CONNECTED"):
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
    
    data_results = EMS_instance.run()