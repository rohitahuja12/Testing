import json
import PySimpleGUI as sg
from controller_gui.choose_transports_screen import choose_transports_screen
from controller_gui.controller_screen import controller_screen
from multiprocessing import Process


async def handle(args):
    with open(args['<configPath>'],'r') as f:
        config = json.load(f)
    for window in config['windows']:
        p = Process(
            target=controller_screen, 
            args=(window['transport'], window['name'])
        )
        p.start()

if __name__ == "__main__":
    main()
