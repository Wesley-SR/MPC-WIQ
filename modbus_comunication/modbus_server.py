#!/usr/bin/env python3

# Modbus/TCP server
#
# run this as root to listen on TCP priviliged ports (<= 1024)
# add "--host 0.0.0.0" to listen on all available IPv4 addresses of the host

# import argparse
from pyModbusTCP.server import ModbusServer, DataBank
from time import sleep
from random import uniform

if __name__ == '__main__':

    # parse args
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-H', '--host', type=str, default='localhost', help='Host (default: localhost)')
    # parser.add_argument('-p', '--port', type=int, default=502, help='TCP port (default: 502)')
    # args = parser.parse_args()
    # IP_server = '127.1.0.0'
    IP_server = 'localhost'
    port =  502

    print("host= {}".format(IP_server))
    print("port= {}".format(port))
    
    server = ModbusServer(IP_server, port, no_block=False)
    databank = DataBank
    
    print(server.ServerInfo())
    try:
        print("Start server...")
        server.start()
        
        print("Server is online")
        state = [0]
        cont = 1
        address = 0
        data_list = [int(cont),int(cont)]
        # databank.set_holding_registers(address, data_list,srv_info = None)
        sleep(0.5)
        print("databank 1 = {}".format(databank.get_words(address)))
        while True:
            if state != databank.get_words(address):
                state = databank.get_words(address)
                print("State = {}".format(state))
                print("Mudou")
            else:
                print("databank = {}".format(databank.get_words(address)))
                print("Nao Mudou")

            sleep(0.5)
            cont = cont + 1
    
    except Exception as error:
        print(error)
        print("Shutdown server ...")
        server.stop()
        print("Server is offline 1")
        
    finally:
        server.stop()
        print("Server is offline 2")
        