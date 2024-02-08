import PySimpleGUI as sg
from choose_transports_screen import choose_transports_screen
from controller_screen import controller_screen
from multiprocessing import Process


def main():
    # transports = choose_transports_screen()
    host = '192.168.1.24'
    # host = 'localhost'
    transports = [
        ('Board', f'tcp://{host}:8120'),
        ('Stage', f'tcp://{host}:8100'),
        ('Camera', f'tcp://{host}:8110'),
        ('Locations', f'tcp://{host}:8130'),
        ('TaskWorker', f'tcp://{host}:8140'),
        ('Cache', f'tcp://{host}:8131'),
        # ('BarcodeReader', f'tcp://{host}:8150'),
    ]

    for name, transport in transports:  
        p = Process(target=controller_screen, args=(transport, name))
        p.start()

if __name__ == "__main__":
    main()
