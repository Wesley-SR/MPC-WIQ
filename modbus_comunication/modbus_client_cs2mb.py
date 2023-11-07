#!/usr/bin/env python3

# Esse client código lê os dados de um CSV e escreve na rede Modbus
# Fonte:
    # https://www.youtube.com/watch?v=FYPQgnQE9fk&ab_channel=Johannes4GNU_Linux
    # https://github.com/Johannes4Linux/Simple-ModbusTCP-Server/blob/master/Simple_ModbusServer.py
    # https://pymodbustcp.readthedocs.io/en/latest/examples/server.html?highlight=server
    # https://pymodbustcp.readthedocs.io/en/latest/package/class_ModbusServer.html?highlight=server#class-modbusserver

# read_register
# read 10 registers and print result on stdout

import time

from pyModbusTCP.client import ModbusClient
import pandas as pd

if __name__ == '__main__':

    # caminho = "C:\Users\wesle\Dropbox\Lactec\DADOS\MPC_MATLAB_Peak_shaving_Suavizacao_Regulacao\Curva_carga_dia_08_11_17.csv"
    caminho_do_arquivo = "cs2mb_datas.csv"
    
    # Faz a leitura do arquivo
    medidas = pd.read_csv(caminho_do_arquivo)
    
    # init modbus client
    host = 'localhost'
    # host = '127.1.0.0'
    port = 502
    client_ID = 2
    
    try:
        client = ModbusClient(host = host, port=port, unit_id = client_ID, debug=False, auto_open=True)
        # print("Client info: {}".format())
        time.sleep(1)
    except ValueError:
        print("Error with host or port params")
    
    cont_mb = 0
    new_mb_data = 0

    while True:
        
        #try:
        # Confere se chegou dados novos
        print("\n\n")
        registers = client.read_holding_registers(1, 1)
        new_mb_data = int(registers[0])
        if new_mb_data:
            registers = client.read_holding_registers(0, 9)
            if registers:
                print("cont_mb = {}, new_mb_data = {}, p_pv = {}, p_load = {}, p_grid = {}, p_bat = {}, p_sc = {}, soc_bat = {}, soc_sc = {}".format(registers[0], registers[1], registers[2], registers[3], registers[4], registers[5], registers[6], registers[7], registers[8]))
                medidas.loc[cont_mb, 'p_pv'] = registers[2]/1000
                medidas.loc[cont_mb, 'p_load'] = registers[3]/1000
                cont_mb += 1
                new_mb_data = 0
                client.write_multiple_registers(0, [cont_mb, new_mb_data])
            else:
                print('unable to read registers \n')
        else:
            print("Don't have new data")

        time.sleep(2)
        
        #except Exception as e:
        #    print("Erro de conexao devido: {}".format(e))
        #    client.close()
        #    break
               
    print("Cliente encerrado")