#!/usr/bin/env python3

# Esse client código lê os dados de um CSV e escreve na rede Modbus
# Fonte:
    # https://www.youtube.com/watch?v=FYPQgnQE9fk&ab_channel=Johannes4GNU_Linux
    # https://github.com/Johannes4Linux/Simple-ModbusTCP-Server/blob/master/Simple_ModbusServer.py
    # https://pymodbustcp.readthedocs.io/en/latest/examples/server.html?highlight=server
    # https://pymodbustcp.readthedocs.io/en/latest/package/class_ModbusServer.html?highlight=server#class-modbusserver

# read_register

import time

from pyModbusTCP.client import ModbusClient
import pandas as pd
from datas import Datas


if __name__ == '__main__':

    data_base = Datas()
    
    # Faz a leitura do arquivo
    medidas_csv = pd.read_csv(data_base.caminho_do_arquivo)
    
    # init modbus client
    host = 'localhost'
    port = 502
    client_ID = 1
    try:
        client = ModbusClient(host = host, port=port, unit_id = client_ID, auto_open=True)
    except ValueError:
        print("Error with host or port params")
    
    # Execution variables
    counter_mb = 0
    last_counter_mb = - 1
    updated_data_switch = 0
    got_reference_signals = False

    run = 1
    #except Exception as e:
    #    print("Erro de conexao devido: {}".format(e))
    #    client.close()
    
    soc_bat_init = data_base.soc_bat
    soc_sc_init  = data_base.soc_sc
    k_pv_init    = data_base.k_pv
    p_sc_init    = data_base.p_sc
    
    soc_bat = 0
    soc_sc  = 0
    k_pv    = 0
    p_sc    = 0
    p_bat   = 0
    p_grid  = 0
    
    print("-----------------------------------")
    print("MODBUS MG - MODBUS MG - MODBUS MG - MODBUS MG")
    while run:
        
        
        # Check reset need
        reset = client.read_holding_registers(100, 1)[0]
        if reset == 1:
            print("\n\n\n\n\n\n")
            print("RESET")
            print("Lendo tudo de novo")
            medidas_csv = pd.read_csv(data_base.caminho_do_arquivo)
            counter_mb = 0
            last_counter_mb = - 1
            updated_data_switch = 0
            got_reference_signals = False
            client.write_single_register(100,0)
            
            soc_bat = soc_bat_init
            soc_sc = soc_sc_init
            k_pv = k_pv_init
            p_sc = p_sc_init
        
        number_of_register_to_read = 18
        registers = client.read_holding_registers(0, number_of_register_to_read)
        counter_mb = int(registers[0])
        updated_data_switch = int(registers[1])
        
        
        # -------------------- MEDIDAS --------------------
        if (counter_mb != last_counter_mb) and (updated_data_switch == 1):
            print(f"\ncounter_mb: {counter_mb}")
            print("MEDIDAS do CSV")
            last_counter_mb = counter_mb
            updated_data_switch = 0
            
            p_pv = medidas_csv.loc[counter_mb, 'p_pv']
            p_load = medidas_csv.loc[counter_mb, 'p_load']
            if counter_mb == 0:
                if (data_base.operation_mode == data_base.ISOLATED):
                    soc_bat = data_base.soc_bat
                    soc_sc  = data_base.soc_sc
                    k_pv    = data_base.k_pv
                    p_sc    = data_base.p_sc
                    # Power balance
                    # k_pv*p_pv + p_bat + p_sc - p_load = 0
                    p_bat = - k_pv*p_pv - p_sc + p_load
                    p_grid = 0
                else: # (data_base.operation_mode == data_base.CONNECTED):
                    pass
            else:
                if (got_reference_signals):
                    if (data_base.operation_mode == data_base.ISOLATED):
                        p_bat = p_bat_ref
                        p_sc_power_balance = - k_pv_ref*p_pv - p_bat + p_load
                        p_sc = p_sc_power_balance
                        p_grid = 0
                        soc_bat = soc_bat - p_bat*(data_base.TS_2TH/60/60)/data_base.Q_BAT
                        soc_sc = soc_sc - p_sc*(data_base.TS_2TH/60/60)/data_base.Q_SC
                        
                        power_balance = p_bat + k_pv_ref*p_pv + p_sc - p_load
                        if power_balance >= -0.001 and power_balance <= 0.001:
                            pass
                        else:
                            print("DEU CHABU!!!!!!!!!!!!!!!!!!!!!")
                            print(f"power_balance: {power_balance} = {p_bat} + {k_pv_ref*p_pv} + {p_sc} - {p_load}")
                            break
                    else: # (data_base.operation_mode == data_base.CONNECTED):
                        pass
                        
                    got_reference_signals = False
                        
            p_pv_to_send    = int(p_pv * data_base.MB_MULTIPLIER)
            p_load_to_send  = int(p_load * data_base.MB_MULTIPLIER)
            p_grid_to_send  = int(p_grid * data_base.MB_MULTIPLIER)
            
            p_bat_to_send   = int(p_bat * data_base.MB_MULTIPLIER)
            if p_bat_to_send < 0:
                p_bat_to_send = - p_bat_to_send
                p_bat_neg = 1
            else:
                p_bat_neg = 0
                
            p_sc_to_send    = int(p_sc * data_base.MB_MULTIPLIER)
            if p_sc_to_send < 0:
                p_sc_to_send = - p_sc_to_send
                p_sc_neg = 1
            else:
                p_sc_neg = 0
            soc_bat_to_send = int(soc_bat * data_base.MB_MULTIPLIER)
            soc_sc_to_send  = int(soc_sc * data_base.MB_MULTIPLIER)
            # 0	1	2	3	4	5	6	7	8	9	10	11
            # counter_mb	updated_data_switch	operation_mode	p_pv	p_load	p_grid	p_bat	p_sc	soc_bat	soc_sc	p_bat_neg	p_sc_neg
            data_to_write = [updated_data_switch, data_base.operation_mode, p_pv_to_send, p_load_to_send, p_grid_to_send, p_bat_to_send, p_sc_to_send, soc_bat_to_send, soc_sc_to_send, p_bat_neg, p_sc_neg]
            print(f"p_pv: {p_pv_to_send}, p_load: {p_load_to_send}, p_grid: {p_grid_to_send}, p_bat: {p_bat_to_send}, p_sc: {p_sc_to_send}, soc_bat: {soc_bat_to_send}, soc_sc: {soc_sc_to_send}, p_bat_neg: {p_bat_neg}, p_sc_neg: {p_sc_neg}")
            
            # print(f"Send data: updated_data_switch: {data_to_write[0]}, operation_mode: {data_to_write[1]}, p_pv: {data_to_write[2]}, p_load: {data_to_write[3]}")
            # print(f"data_to_write: {data_to_write}")
            client.write_multiple_registers(1, data_to_write) # mg2bm doesn't touch the counter_mb (register[0])
        
        
        # -------------------- CONTROLE --------------------
        if (updated_data_switch == 2):
            print("CONTROL SIGNAL RECEIVED")
            print(f"registers: {registers}")
            got_reference_signals = True
            updated_data_switch = 0
            # 12        13          14          15          16              17
            # p_bat_ref	p_sc_ref	p_grid_ref	k_pv_ref	p_bat_ref_neg	p_sc_ref_neg
            p_bat_ref  = float(registers[12] / data_base.MB_MULTIPLIER)
            p_sc_ref   = float(registers[13] / data_base.MB_MULTIPLIER)
            p_grid_ref = float(registers[14] / data_base.MB_MULTIPLIER)
            k_pv_ref = float(registers[15] / data_base.MB_MULTIPLIER)
            p_bat_ref_neg = registers[16]
            p_sc_ref_neg = registers[17]
            
            if p_bat_ref_neg == 1:
                p_bat_ref = - p_bat_ref
            if p_sc_ref_neg == 1:
                p_sc_ref = - p_sc_ref
            
            print("Referencias recebidas")
            print(f"p_bat_ref: {p_bat_ref}, p_sc_ref: {p_sc_ref}, p_grid_ref: {p_grid_ref}, k_pv_ref: {k_pv_ref}")
            client.write_single_register(1, 3)
        
        #except Exception as e:
        #    print("Erro de conexao devido: {}".format(e))
        #    client.close()
        #    break
        time.sleep(0.01)

    print("Cliente encerrado")