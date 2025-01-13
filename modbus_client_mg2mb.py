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

def calculate_power_balance(conected_mode, p_pv, p_load, soc_bat, soc_sc):
    pass


def run_modbus_client_mgs2mb():
    
    from datas import Datas
    datas = Datas()
    
    # Faz a leitura do arquivo
    medidas_csv = pd.read_csv(datas.caminho_do_arquivo)
    
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
    
    soc_bat_init = datas.soc_bat
    soc_sc_init  = datas.soc_sc
    k_pv_init    = datas.k_pv
    p_sc_init    = datas.p_sc
    
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
            print("RESET")
            print("\n\n\n\n\n\n")
            # print("Lendo tudo de novo")
            # medidas_csv = pd.read_csv(datas.caminho_do_arquivo)
            # counter_mb = 0
            # last_counter_mb = - 1
            # updated_data_switch = 0
            # got_reference_signals = False
            client.write_single_register(100,0)
            
            # soc_bat = soc_bat_init
            # soc_sc = soc_sc_init
            # k_pv = k_pv_init
            # p_sc = p_sc_init
            client.close()
            return 0
        
        number_of_register_to_read = 25
        registers = client.read_holding_registers(0, number_of_register_to_read)
        # counter_mb vem do EMS, que dita em que "t" estamos para ler p_pv e p_load
        counter_mb = int(registers[0])
        updated_data_switch = int(registers[1])
        
        
        # -------------------- ENVIAR STATUS DA MG --------------------
        if (counter_mb != last_counter_mb) and (updated_data_switch == 1):
            print(f"\ncounter_mb: {counter_mb}")
            print("MEDIDAS do CSV")
            last_counter_mb = counter_mb
            updated_data_switch = 0
            
            p_pv = medidas_csv.loc[counter_mb, 'p_pv']
            p_load = medidas_csv.loc[counter_mb, 'p_load']
            if counter_mb == 0:
                soc_bat = datas.soc_bat
                soc_sc  = datas.soc_sc
                k_pv    = datas.k_pv
                p_sc    = datas.p_sc
                # CONNECTED
                if datas.connected_mode:
                    p_grid  = datas.p_grid
                    # Power balance - The battery starts balancing the power of the microgrid
                    # k_pv*p_pv + p_bat + p_sc - p_load + p_grid = 0
                    p_bat = - k_pv*p_pv - p_sc + p_load - p_grid
                # ISOLATED
                else:
                    p_grid  = 0
                    # Power balance - The battery starts balancing the power of the microgrid
                    # k_pv*p_pv + p_bat + p_sc - p_load = 0
                    p_bat = - k_pv*p_pv - p_sc + p_load
            else:
                if (got_reference_signals):
                    if datas.connected_mode:
                        p_bat = p_bat_ref
                        p_grid = p_grid_ref
                        p_sc_power_balance = - k_pv_ref*p_pv - p_bat + p_load - p_grid
                        p_sc = p_sc_power_balance
                        soc_bat = soc_bat - p_bat*(datas.TS_2TH/60/60)/datas.Q_BAT
                        soc_sc = soc_sc - p_sc*(datas.TS_2TH/60/60)/datas.Q_SC
                        power_balance = p_bat + k_pv_ref*p_pv + p_sc - p_load + p_grid
                    else:
                        p_bat = p_bat_ref
                        p_grid = 0
                        p_sc_power_balance = - k_pv_ref*p_pv - p_bat + p_load
                        p_sc = p_sc_power_balance
                        soc_bat = soc_bat - p_bat*(datas.TS_2TH/60/60)/datas.Q_BAT
                        soc_sc = soc_sc - p_sc*(datas.TS_2TH/60/60)/datas.Q_SC
                        power_balance = p_bat + k_pv_ref*p_pv + p_sc - p_load
                        
                    if not ((power_balance >= -0.001) and (power_balance <= 0.001)):
                        print(f"power_balance: {power_balance} = {p_bat} + {k_pv_ref*p_pv} + {p_sc} - {p_load} + {p_grid}")
                        raise("Error in power balance.")
                        
                    if (soc_bat >= datas.SOC_BAT_MAX) or (soc_bat <= datas.SOC_BAT_MIN):
                        print(f"soc_bat: {soc_bat}")
                        raise("Error in power SOC bat")

                    if (soc_sc >= datas.SOC_SC_MAX) or (soc_sc <= datas.SOC_SC_MIN):
                        print(f"soc_sc: {soc_sc}")
                        raise("Error in power soc_sc")
                    if (soc_sc > datas.SOC_SC_MAX_RECOMMENDED) or (soc_sc < datas.SOC_SC_MIN_RECOMMENDED):
                        print(f"************ soc_sc: {soc_sc}!!")
                        
                    got_reference_signals = False
            
            print(f"p_pv: {p_pv}")
            print(f"p_load: {p_load}")
            p_pv_to_send    = int(p_pv * datas.MB_MULTIPLIER)
            p_load_to_send  = int(p_load * datas.MB_MULTIPLIER)
            
            p_bat_to_send   = int(p_bat * datas.MB_MULTIPLIER)
            if p_bat_to_send < 0:
                p_bat_to_send = - p_bat_to_send
                p_bat_neg = 1
            else:
                p_bat_neg = 0
                
            p_sc_to_send    = int(p_sc * datas.MB_MULTIPLIER)
            if p_sc_to_send < 0:
                p_sc_to_send = - p_sc_to_send
                p_sc_neg = 1
            else:
                p_sc_neg = 0
            
            p_grid_to_send = int(p_grid * datas.MB_MULTIPLIER)
            if p_grid_to_send < 0:
                p_grid_to_send = - p_grid_to_send
                p_grid_neg = 1
            else:
                p_grid_neg = 0
            
            soc_bat_to_send = int(soc_bat * datas.MB_MULTIPLIER)
            soc_sc_to_send  = int(soc_sc * datas.MB_MULTIPLIER)
            """ Sequência dos sinais de status da MG
                0 counter_mb (Esse não envia) Notar que write_multiple_register inicia na posição 1
                1 updated_data_switch
                2 connected_mode
                3 p_pv
                4 p_load
                5 p_grid
                6 p_bat
                7 p_sc
                8 soc_bat
                9 soc_sc
                10 p_bat_neg
                11 p_sc_neg
                12 p_grid_neg
            """
            data_to_write = [updated_data_switch, datas.connected_mode, p_pv_to_send, p_load_to_send, p_grid_to_send, p_bat_to_send, p_sc_to_send, soc_bat_to_send, soc_sc_to_send, p_bat_neg, p_sc_neg, p_grid_neg]
            print(f"modo: {datas.connected_mode}, p_pv: {p_pv_to_send}, p_load: {p_load_to_send}, p_grid: {p_grid_to_send}, p_bat: {p_bat_to_send}, p_sc: {p_sc_to_send}, soc_bat: {soc_bat_to_send} (real: {soc_bat}), soc_sc: {soc_sc_to_send}, p_bat_neg: {p_bat_neg}, p_sc_neg: {p_sc_neg}, p_grid_neg: {p_grid_neg}")
            
            # print(f"Send data: updated_data_switch: {data_to_write[0]}, connected_mode: {data_to_write[1]}, p_pv: {data_to_write[2]}, p_load: {data_to_write[3]}")
            # print(f"data_to_write: {data_to_write}")
            client.write_multiple_registers(1, data_to_write) # mg2bm doesn't touch the counter_mb (register[0])
        
        
        # -------------------- LER SINAIS DE CONTROLE --------------------
        if (updated_data_switch == 2):
            print("CONTROL SIGNAL RECEIVED")
            print(f"registers: {registers}")
            got_reference_signals = True
            updated_data_switch = 0
            
            """ Sequência dos sinais de controle
                15 p_bat_ref
                16 p_sc_ref
                17 p_grid_ref
                18 k_pv_ref
                19 p_bat_ref_neg
                20 p_sc_ref_neg
                21 p_grid_ref_neg
            """
            p_bat_ref  = float(registers[15] / datas.MB_MULTIPLIER) # No main_EMS, deve iniciar de 15 também
            p_sc_ref   = float(registers[16] / datas.MB_MULTIPLIER)
            p_grid_ref = float(registers[17] / datas.MB_MULTIPLIER)
            k_pv_ref = float(registers[18] / datas.MB_MULTIPLIER)
            p_bat_ref_neg = registers[19]
            p_sc_ref_neg = registers[20]
            p_grid_ref_neg = registers[21]
            
            if p_bat_ref_neg == 1:
                p_bat_ref = - p_bat_ref
            if p_sc_ref_neg == 1:
                p_sc_ref = - p_sc_ref
            if p_grid_ref_neg == 1:
                p_grid_ref = - p_grid_ref
            
            print("Referencias recebidas")
            print(f"p_bat_ref: {p_bat_ref}, p_sc_ref: {p_sc_ref}, p_grid_ref: {p_grid_ref}, k_pv_ref: {k_pv_ref}")
            client.write_single_register(1, 3)
        
        #except Exception as e:
        #    print("Erro de conexao devido: {}".format(e))
        #    client.close()
        #    break
        time.sleep(0.01)

    print("Cliente encerrado")


if __name__ == '__main__':
    while(True):
        print("========= INICIANDO MODBUS CLIENT MG2MB =========")
        run_modbus_client_mgs2mb()