import PySimpleGUI as sg


def choose_transports_screen():
    sg.theme('DarkBlue3')
    layout = [
        [sg.Text('Some text')],
        [sg.Text('input transports')],
        [sg.Multiline(size=(30,3), key='transports')],
        [sg.Button('load')]
    ]
    window = sg.Window("Tittle", layout, finalize=True)


    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            raise Exception('Window closed.')
        if event == 'load':
            transports = values['transports']
            window.close()
            return transports.split('\n')

