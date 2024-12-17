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
# from ForecastingModel import ForecastingModel

# Modbus
from pyModbusTCP.client import ModbusClient

from mmpw import mmpw


# *******************************************************
#      EMC CLASS                                        #
# *******************************************************
class EMS():
    def __init__(self):
        
        print("-------------------------")
        print("1) EMS Initialization")
        # Create a object of datas
        self.Datas = Datas()
        
        # Execution variables
        self.enable_run_EMS = True
        self.enable_run_3th = True
        self.enable_run_2th = True
        self.enable_plot = False
        self.enable_save_plot = False
        self.path_to_plot = "C:\\Users\\wesle\\Desktop\\Plots\\"
        
        # Timers
        self.t = 0 # Time that start in matrix M (in simulation)
        self.t_final = 1
        # Last Timers
        self.last_time_measurement = -1
        self.last_time_2th = -1
        self.last_time_3th = -900

        # Create optimization object
        if self.Datas.optimization_method == "QP":
            self.qp_optimization = OptimizationMIQP()
        elif self.Datas.optimization_method == "MILP":
            self.milp_optimization = OptimizationMILP()
        
        # Create Modbus object
        print("\n2) Modbus initialization")
        self.host = 'localhost'
        self.port = 502
        self.client_ID = 2
        try:
            self.modbus_client = ModbusClient(host = self.host, port = self.port, unit_id = self.client_ID, auto_open=True)
        except Exception as e:
            print("[EMS Init] Error connecting Modbus Client: {}".format(e))
            self.modbus_client.close()
        self.counter_mb = 0
        self.modbus_client.write_single_register(100, 1)
        reset = 1
        while reset == 1:
            time.sleep(0.50)
            reset = self.modbus_client.read_holding_registers(100, 1)[0]

        # Create DataFrame for forecast
        self.pv_forecasted_3th = pd.DataFrame(index=range(self.Datas.NP_3TH), columns=['data'])
        self.load_forecasted_3th = pd.DataFrame(index=range(self.Datas.NP_3TH), columns=['data'])
        # Create DataFrame for past datas
        self.p_pv_past_3th = pd.read_csv("data_pv_15_min_past.csv", index_col='time')
        self.p_load_past_3th = pd.read_csv("data_load_15_min_past.csv", index_col='time')
        if self.enable_plot or self.enable_save_plot:
            plt.figure(figsize=(10, 5))
            time_steps = list(range(self.Datas.NP_3TH))
            plt.plot(time_steps, self.p_pv_past_3th['data'].values, label = 'p_pv_past_3th')
            plt.plot(time_steps, self.p_load_past_3th['data'].values, label = 'p_load_past_3th')
            plt.title('Passado')
            plt.legend()
            plt.grid()
            if (self.enable_save_plot):
                plt.savefig(f'{self.path_to_plot}Passado.png')
        
        # Create DataFrame for forecast
        self.pv_forecasted_2th = pd.DataFrame(index=range(self.Datas.NP_2TH), columns=['data'])
        self.load_forecasted_2th = pd.DataFrame(index=range(self.Datas.NP_2TH), columns=['data'])
        
        self.results_3th = pd.DataFrame(index=range(self.Datas.NP_3TH), columns=['p_bat_sch', 'k_pv_sch', 'p_grid_sch','soc_bat','pv_forecasted_3th', 'load_forecasted_3th'])
        self.results_2th = pd.DataFrame(index=range(self.Datas.NP_2TH), columns=['p_bat_ref', 'k_pv_ref', 'p_sc_ref', 'p_grid_ref','soc_bat', 'soc_sc'])
        self.OF_3th = 0
        self.OF_2th = 0




    # =======================================================
    #      Main loop of MPC                                 #
    # =======================================================
    def run(self) -> Datas:
        
        try:
            while self.enable_run_EMS and self.t < self.t_final:

                print(f"t = {self.t}, counter_mb: {self.counter_mb}") 

                # Take measurements
                if (self.is_it_time_to_take_measurements()):
                    self.get_measurements()

                # Run terciary optmization
                if (self.is_it_time_to_run_3th() and self.enable_run_3th):
                    # Update past 3th data
                    self.p_pv_past_3th.iloc[0:self.Datas.NP_3TH-1] = self.p_pv_past_3th.iloc[1:self.Datas.NP_3TH] # Discart the oldest sample
                    self.p_load_past_3th.iloc[0:self.Datas.NP_3TH-1] = self.p_load_past_3th.iloc[1:self.Datas.NP_3TH] # Discart the oldest sample
                    
                    self.p_pv_past_3th.at[self.Datas.NP_3TH, 'data'] = self.Datas.p_pv # Update the new PV sample with the actual data
                    self.p_load_past_3th.at[self.Datas.NP_3TH, 'data'] = self.Datas.p_load # Update the new load sample with the actual data                
                    # print(f"p_pv mensuremented: {self.p_pv_past_3th.at[self.Datas.NP_3TH, 'data']}")
                    # print(f"p_load mensuremented: {self.p_load_past_3th.at[self.Datas.NP_3TH, 'data']}")
                    
                    # Update the first row of the forecast DataFrames
                    ## The first row of the forecast DataFrames is a measurement.
                    self.pv_forecasted_3th.loc[0, 'data'] = self.Datas.p_pv
                    self.load_forecasted_3th.loc[0, 'data'] = self.Datas.p_load

                    # Run 3th forecast
                    self.pv_forecasted_3th.iloc[1:]   = mmpw(self.p_pv_past_3th, self.Datas.NP_3TH)
                    self.load_forecasted_3th.iloc[1:] = mmpw(self.p_load_past_3th, self.Datas.NP_3TH)
                    
                    if self.enable_plot or self.enable_save_plot:
                        plt.figure(figsize=(10, 5))
                        time_steps = list(range(self.Datas.NP_3TH))
                        plt.plot(time_steps, self.pv_forecasted_3th['data'].values, label = 'pv_forecasted_3th')
                        plt.plot(time_steps, self.load_forecasted_3th['data'].values, label = 'load_forecasted_3th')
                        plt.title("Forecast to 3th")
                        plt.legend()
                        plt.grid()
                        if (self.enable_save_plot):
                            plt.savefig(f"{self.path_to_plot}forecast_for_3th.png")

                    self.run_3th_optimization()
                    self.Datas.k_pv_sch     = self.results_3th.loc[0, 'k_pv_sch']
                    self.Datas.p_bat_sch    = self.results_3th.loc[0, 'p_bat_sch']
                    self.Datas.p_grid_sch    = self.results_3th.loc[0, 'p_grid_sch']

                    if self.Datas.p_bat_sch >= 0:
                        self.Datas.p_bat_dis_sch = self.Datas.p_bat_sch
                        self.Datas.p_bat_ch_sch  = 0
                    else:
                        self.Datas.p_bat_dis_sch = 0
                        self.Datas.p_bat_ch_sch  = self.Datas.p_bat_sch
                    
                    if self.enable_plot or self.enable_save_plot:
                        # self.Datas.p_grid_sch = self.results_3th.loc[0, 'p_grid_sch'] # Not used
                        print(f"OF_3th: {self.OF_3th}")
                        plt.figure(figsize=(10, 5))
                        time_steps = list(range(self.Datas.NP_3TH))
                        plt.plot(time_steps, self.results_3th['p_bat_sch'].values, label = 'p_bat_sch')
                        plt.plot(time_steps, self.results_3th['k_pv_sch'].values, label = 'k_pv_sch')
                        plt.title("Schedule")
                        plt.legend()
                        plt.grid()
                        if (self.enable_save_plot):
                            plt.savefig(f"{self.path_to_plot}schedule_from_3th.png")
                    
                # Run 2th optmization
                if (self.is_it_time_to_run_2th() and self.enable_run_2th):

                    # Run optimization 2th
                    self.run_2th_optimization()
                    self.send_control_signals()
                    
                    if self.enable_plot or self.enable_save_plot:
                        print(f"OF_2th: {self.OF_2th}")
                        plt.figure(figsize=(10, 5))
                        time_steps = list(range(self.Datas.NP_2TH))
                        plt.plot(time_steps, self.results_2th['p_bat_ref'].values, label = 'p_bat_ref')
                        plt.plot(time_steps, self.results_2th['k_pv_ref'].values, label = 'k_pv_ref')
                        plt.plot(time_steps, self.results_2th['p_sc_ref'].values, label = 'p_sc_ref')
                        plt.plot(time_steps, self.pv_forecasted_2th['data'].values, label = 'pv_forecasted_2th')
                        plt.plot(time_steps, self.load_forecasted_2th['data'].values, label = 'load_forecasted_2th')
                        plt.title("Reference")
                        plt.legend()
                        plt.grid()
                        if (self.enable_save_plot):
                            plt.savefig(f"{self.path_to_plot}results_2th_{self.t}.png")
                    
                # Check if plot
                if self.enable_plot:
                    plt.show()

                print("\n------------------------------------")
                # self.enable_run_EMS = bool(int(input("Pressione 1 para continuar e 0 para finalizar: ")))
            
                self.t = self.t + 1
        
        except Exception as e:
            print(f"[EMS][RUN] Error: {e}")
        
        return self.Datas, self.t





    # =======================================================
    #    # Auxiliaries functions                            #
    # =======================================================

    # Check if is time to take new measumerements for microgrid via Mudbus
    def is_it_time_to_take_measurements(self) -> bool: 
        # current_time = time.time()
        current_time = self.t
        if (current_time - self.last_time_measurement >= self.Datas.TS_MEASUREMENT):
            # print("It's time to take measurement")
            self.last_time_measurement = current_time
            return True
        else:
            # print("It`s not time to take measurement")
            return False



    def is_it_time_to_run_3th(self) -> bool:
        # current_time = time.time() # For real control
        current_time = self.t # For simulation
        if (current_time - self.last_time_3th >= self.Datas.TS_3TH):
            self.last_time_3th = current_time
            return True
        else:
            return False



    def is_it_time_to_run_2th(self) -> bool:
        # current_time = time.time() # For real control
        current_time = self.t # For simulation
        if (current_time - self.last_time_2th >= self.Datas.TS_2TH):
            self.last_time_2th = current_time
            return True
        else:
            return False



    def run_3th_optimization(self) -> None:
        print("4) run_3th_optimization")
        # Call optimization
        if (self.Datas.operation_mode == self.Datas.CONNECTED):
            if (self.Datas.optimization_method == "QP"):
                self.results_3th, self.OF_3th = self.qp_optimization.connected_optimization_3th(self.Datas, self.pv_forecasted_3th, self.load_forecasted_3th)
            elif(self.Datas.optimization_method == "MILP"):
                # self.milp_optimization.connected_optimization_3th()
                print("Dont have connected MILP")

        elif (self.Datas.operation_mode == self.Datas.ISOLATED):
            if (self.Datas.optimization_method == "QP"):
                self.results_3th, self.OF_3th = self.qp_optimization.isolated_optimization_3th(self.Datas, self.pv_forecasted_3th, self.load_forecasted_3th)
            elif (self.Datas.optimization_method == "MILP"):
                self.results_3th, self.OF_3th = self.milp_optimization.isolated_optimization_3th(self.Datas, self.pv_forecasted_3th, self.load_forecasted_3th)
            else:
                print("Don't have optimization method")
        else:
            print("Don't have optimization method")
        
        # Save 3th results
        self.results_3th.to_csv(f"results_3th_{self.t}.csv")


    def run_2th_optimization(self) -> None:

        print("\n5) OTIMIZAZAO - ESTADO ATUAL")
        self.pv_forecasted_2th['data'] = self.Datas.p_pv
        self.load_forecasted_2th['data'] = self.Datas.p_load
        # self.pv_forecasted_2th.loc[0, 'data'] = self.Datas.p_pv
        # self.load_forecasted_2th.loc[0, 'data'] = self.Datas.p_load
        # print(self.load_forecasted_2th)
        
        print(f'p_pv: {self.Datas.p_pv} '
        f'p_load: {self.Datas.p_load} '
        f'p_grid: {self.Datas.p_grid} '
        f'p_bat: {self.Datas.p_bat} '
        f'p_sc: {self.Datas.p_sc} '
        f'soc_bat: {self.Datas.soc_bat} '
        f'soc_sc: {self.Datas.soc_sc} '
        f'p_bat_sch: {self.Datas.p_bat_sch} ')
        
        self.Datas.M.loc[self.t, 'power_balance'] = self.Datas.p_pv*self.Datas.k_pv + self.Datas.p_bat + self.Datas.p_sc - self.Datas.p_load
        print(f"balanco: {self.Datas.M.loc[self.t, 'power_balance']}")
        
        # Call optimization
        time_before_optimizaion = time.time()
        if (self.Datas.operation_mode == self.Datas.CONNECTED):
            if (self.Datas.optimization_method == "QP"):
                self.results_2th, self.OF_2th = self.qp_optimization.connected_optimization_2th(self.Datas, self.pv_forecasted_2th, self.load_forecasted_2th)
            elif (self.Datas.optimization_method == "MILP"):
                print("TODO: MILP Optimization")
                pass
        elif (self.Datas.operation_mode == self.Datas.ISOLATED):
            if (self.Datas.optimization_method == "QP"):
                self.results_2th, self.OF_2th = self.qp_optimization.isolated_optimization_2th(self.Datas, self.pv_forecasted_2th, self.load_forecasted_2th)
            elif (self.Datas.optimization_method == "MILP"):
                self.results_2th, self.OF_2th = self.milp_optimization.isolated_optimization_2th(self.Datas, self.pv_forecasted_2th, self.load_forecasted_2th)
        optimizaion_time = time.time() - time_before_optimizaion
        # print(f"Time to run run_2th_optimization: {optimizaion_time}")
    
    def get_measurements(self) -> None:
        print("3) MEDIDAS")
        wait_for_new_data = 1
        
        updated_data_switch = 1
        self.modbus_client.write_multiple_registers(0, [self.counter_mb, updated_data_switch])
        send_request_time = time.time()
        time.sleep(0.05)
        
        while wait_for_new_data == 1:
            # print("Waiting for datas")
            registers = self.modbus_client.read_holding_registers(0, 15)
            # Check if we have new data
            updated_data_switch = int(registers[1])
            if updated_data_switch == 0:
                # print(f"[updated_data_switch = {updated_data_switch}] registers: {registers}")
                self.counter_mb += 1
                wait_for_new_data = 0
                
                # Operation mode
                if (registers[2] == 1):
                    self.Datas.operation_mode = self.Datas.CONNECTED
                else:
                    self.Datas.operation_mode = self.Datas.ISOLATED
                
                # Datas from microgrid
                # 0             1           2               3       4       5       6       7       8       9       10          11
                # counter_mb	new_mb_data	operation_mode	p_pv	p_load	p_grid	p_bat	p_sc	soc_bat	soc_sc	p_bat_neg	p_sc_neg
                
                # if self.t > 0:
                #     self.pv_forecasted_2th['data'] = self.Datas.p_pv
                #     self.load_forecasted_2th['data'] = self.Datas.p_load
                
                self.Datas.p_pv      = registers[3]/self.Datas.MB_MULTIPLIER
                self.Datas.p_load    = registers[4]/self.Datas.MB_MULTIPLIER
                self.Datas.p_grid    = registers[5]/self.Datas.MB_MULTIPLIER
                self.Datas.p_bat     = registers[6]/self.Datas.MB_MULTIPLIER
                self.Datas.p_sc      = registers[7]/self.Datas.MB_MULTIPLIER
                self.Datas.soc_bat   = registers[8]/self.Datas.MB_MULTIPLIER
                self.Datas.soc_sc    = registers[9]/self.Datas.MB_MULTIPLIER
                self.Datas.p_bat_neg = registers[10]
                self.Datas.p_sc_neg  = registers[11]
                
                if self.Datas.p_bat_neg == 1:
                    self.Datas.p_bat = - self.Datas.p_bat
                if self.Datas.p_sc_neg == 1:
                    self.Datas.p_sc = - self.Datas.p_sc
                
                print(f'updated_data_switch: {updated_data_switch} '
                f'operation_mode: {self.Datas.operation_mode} ')
                print(f'p_pv: {self.Datas.p_pv} '
                f'p_load: {self.Datas.p_load} '
                f'p_grid: {self.Datas.p_grid} '
                f'p_bat: {self.Datas.p_bat} '
                f'p_sc: {self.Datas.p_sc} '
                f'soc_bat: {self.Datas.soc_bat} '
                f'soc_sc: {self.Datas.soc_sc}')
                
                # Save data
                index = self.t
                self.Datas.M.loc[index, 'soc_bat'] = self.Datas.soc_bat
                self.Datas.M.loc[index, 'soc_sc'] = self.Datas.soc_sc
                self.Datas.M.loc[index, 'p_bat'] = self.Datas.p_bat
                self.Datas.M.loc[index, 'p_sc'] = self.Datas.p_sc
                # print(f"self.Datas.M.loc[{self.t}, 'soc_bat']: {self.Datas.M.loc[self.t, 'soc_bat']}")
                # print(f"self.Datas.M.loc[{self.t}, 'soc_sc']: {self.Datas.M.loc[self.t, 'soc_sc']}")
                # print(f"self.Datas.M.loc[{self.t}, 'p_bat']: {self.Datas.M.loc[self.t, 'p_bat']}")
                # print(f"self.Datas.M.loc[{self.t}, 'p_sc']: {self.Datas.M.loc[self.t, 'p_sc']}")
                
            time.sleep(0.05)
            if (send_request_time - time.time() > 0.5):
                self.get_measurements()



    def send_control_signals(self) -> None:
        print("\n6) CONTROL SIGNAL TO SEND")
        is_signal_reference = 2
        existe_nan = self.results_2th.isna().any().any()
        if existe_nan:
            print(f"existe_nan ---------------")
            print(self.results_2th)
        
        p_bat_ref  = int((self.results_2th.loc[0, 'p_bat_ref']) * self.Datas.MB_MULTIPLIER)
        p_sc_ref   = int((self.results_2th.loc[0, 'p_sc_ref']) * self.Datas.MB_MULTIPLIER)
        p_grid_ref = int((self.results_2th.loc[0, 'p_grid_ref']) * self.Datas.MB_MULTIPLIER)
        k_pv_ref   = int((self.results_2th.loc[0, 'k_pv_ref']) * self.Datas.MB_MULTIPLIER)
        
        if p_bat_ref < 0:
            p_bat_ref_neg = 1
            p_bat_ref = -p_bat_ref
        else:
            p_bat_ref_neg = 0
        
        if p_sc_ref < 0:
            p_sc_ref_neg = 1
            p_sc_ref = - p_sc_ref
        else:
            p_sc_ref_neg = 0
        # if p_grid_ref < 0: # TODO
        
        print(f"pv_forecasted_2th: {self.pv_forecasted_2th.loc[0,'data']} "
        f"load_forecasted_2th: {self.load_forecasted_2th.loc[0,'data']} "
        f"p_grid: {self.Datas.p_grid} "
        f"p_bat_ref: {p_bat_ref} "
        f"p_sc_ref: {p_sc_ref} "
        f"p_grid_ref: {p_grid_ref} "
        f"k_pv_ref: {k_pv_ref} "
        f"p_bat_sch: {self.Datas.p_bat_sch} ")
        
        control_signals = [p_bat_ref,
                           p_sc_ref,
                           p_grid_ref,
                           k_pv_ref,
                           p_bat_ref_neg,
                           p_sc_ref_neg]
        
        self.modbus_client.write_multiple_registers(12, control_signals)
        
        # Save data
        index = self.t
        self.Datas.M.loc[index, 'p_bat_ref'] = self.results_2th.loc[0, 'p_bat_ref']
        self.Datas.M.loc[index, 'p_sc_ref'] = self.results_2th.loc[0, 'p_sc_ref']
        self.Datas.M.loc[index, 'p_grid_ref'] = self.results_2th.loc[0, 'p_grid_ref']
        self.Datas.M.loc[index, 'k_pv_ref'] = self.results_2th.loc[0, 'k_pv_ref']

        # PLOT ALL 2TH OUTPUT
        # print("p_bat_ref", end = ' ')
        # for k in range(self.Datas.NP_2TH):
        #     print(self.results_2th.loc[k, 'p_bat_ref'], end = ' ')
        # print("")
        # print("p_sc_ref", end = ' ')
        # for k in range(self.Datas.NP_2TH):
        #     print(self.results_2th.loc[k, 'p_sc_ref'], end = ' ')
        # print("")
        # print("p_grid_ref", end = ' ')
        # for k in range(self.Datas.NP_2TH):
        #     print(self.results_2th.loc[k, 'p_grid_ref'], end = ' ')
        # print("")
        # print("pv_forecasted_2th", end = ' ')
        # for k in range(self.Datas.NP_2TH):
        #     print(self.pv_forecasted_2th.loc[k,'data'], end = ' ')
        # print("")
        # print("load_forecasted_2th", end = ' ')
        # for k in range(self.Datas.NP_2TH):
        #     print(self.load_forecasted_2th.loc[k,'data'], end = ' ')
        # print("")
        
        # print(f"p_sc_ref: {self.results_2th.loc[0, 'p_sc_ref']}")
        # print(f"p_grid_ref: {self.results_2th.loc[0, 'p_grid_ref']}")
        # print(f"k_pv_ref: {self.results_2th.loc[0, 'k_pv_ref']}")
        # print(f"p_pv_forecast: {self.pv_forecasted_2th.loc[0,'data']}")
        # print(f"load_pv_forecast: {self.load_forecasted_2th.loc[0,'data']}")
        # balance =   (self.results_2th.loc[0, 'p_bat_ref'] + self.results_2th.loc[0, 'p_sc_ref'] +
        #             self.results_2th.loc[0, 'p_grid_ref'] + self.results_2th.loc[0, 'k_pv_ref']*self.pv_forecasted_2th.loc[0,'data'] +
        #             - self.load_forecasted_2th.loc[0,'data'])
        # print(f"balance: {balance}")
        
        time.sleep(0.05)
        wait_for_confirmation = 1
        confirmation = 0
        waint = 1
        while (wait_for_confirmation == 1):
            confirmation = self.modbus_client.read_holding_registers(1,1)[0]
            if confirmation == 3:
                wait_for_confirmation = 0
                # print("Veio a confirmacao que recebeu o controle")
            else:
                time.sleep(0.05)
                waint += 1
                if waint > 10:
                    self.modbus_client.write_single_register(1, is_signal_reference)
                    waint = 0




    def plot_result(self) -> None:
        time_steps = list(range(self.Datas.NP_3TH))
        
        plt.figure(figsize=(10, 5))
        
        if (self.Datas.operation_mode == "CONNECTED"):
            print("Plot p_grid")
            plt.plot(time_steps, self.Datas.R_3th.loc[:, 'p_grid_3th'], marker='o', linestyle='-', color='r', label='Grid')
        
        plt.plot(time_steps, self.Datas.R_3th.loc[:, 'p_bat_3th'], marker='o', linestyle='-', color='b', label='Battery')
        plt.plot(time_steps, self.pv_forecasted_3th.loc[:, 'pv_forecasted_3th'], marker='o', linestyle='-', color='orange', label='PV')
        plt.plot(time_steps, self.load_forecasted_3th.loc[:, 'load_forecasted_3th'], marker='o', linestyle='-', color='g', label='Load')
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

    tempo_inicio_total = time.time()
    EMS_instance = EMS()
    
    datas, t = EMS_instance.run()
    print(type(datas))

    print(f"datas.M.loc[{0}, 'soc_bat']: {datas.M.loc[0, 'soc_bat']}")
    print(f"datas.M.loc[{0}, 'soc_sc']: {datas.M.loc[0, 'soc_sc']}")
    print(f"datas.M.loc[{0}, 'p_bat']: {datas.M.loc[0, 'p_bat']}")
    print(f"datas.M.loc[{0}, 'p_sc']: {datas.M.loc[0, 'p_sc']}")
    
    M = datas.M.head(t)
    
    for k in range(t):
        M.loc[k, "p_load"] = - M.loc[k, "p_load"]
    
    try:
        M.to_csv("results.csv")
    except:
        print("\n\n")
        input_key = int(input("Fecha o CSV corno!"))
        if input_key == 1:
            M.to_csv("results.csv")
        else:
            pass
        
    tempo_total = time.time() - tempo_inicio_total
    print(f"Tempo total: {tempo_total}")
    