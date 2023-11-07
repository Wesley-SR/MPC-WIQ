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

if __name__ == '__main__':

    caminho_do_arquivo = "microgrid_measurements.csv"
    
    # Faz a leitura do arquivo
    medidas_csv = pd.read_csv(caminho_do_arquivo)
    
    # init modbus client
    host = 'localhost'
    # host = '127.1.0.0'
    port = 502
    client_ID = 2
    
    try:
        client = ModbusClient(host = host, port=port, unit_id = client_ID, debug=False, auto_open=True)
        # print("Client info: {}".format())
    except ValueError:
        print("Error with host or port params")
    
    Np_2th = 288
    cont_mb = 0
    last_cont_mb = 0
    new_mb_data = 0
    run = 0

    #try:
    registers = client.read_holding_registers(1, 1)
    cont_mb = int(registers[0])
    new_mb_data = 1
    p_pv = int((medidas_csv.loc[cont_mb, 'p_pv'])*1000)
    p_load = int((medidas_csv.loc[cont_mb, 'p_load'])*1000)
    data_to_write = [new_mb_data, p_pv, p_load]
    print("Send first data: {}  {}  {}".format(data_to_write[0], data_to_write[1], data_to_write[2]))
    client.write_multiple_registers(1, data_to_write)
    
    run = 1
    #except Exception as e:
    #    print("Erro de conexao devido: {}".format(e))
    #    client.close()
    
    while run:
        
        number_of_register_to_read = 9
        time.sleep(0.3)
        #try:
        
        registers = client.read_holding_registers(0, 2)
        cont_mb = int(registers[0])
        new_mb_data = int(registers[1])
        if (cont_mb != last_cont_mb) and (not new_mb_data):
            last_cont_mb = cont_mb
            new_mb_data = 1
            p_pv = int((medidas_csv.loc[cont_mb, 'p_pv'])*1000)
            p_load = int((medidas_csv.loc[cont_mb, 'p_load'])*1000)
            data_to_write = [new_mb_data, p_pv, p_load]
            print("Send data: {}  {}  {}".format(data_to_write[0], data_to_write[1], data_to_write[2]))
            client.write_multiple_registers(1, data_to_write) # mg2bm doesn't touch the cont_mb
        
        #except Exception as e:
        #    print("Erro de conexao devido: {}".format(e))
        #    client.close()
        #    break

    print("Cliente encerrado")