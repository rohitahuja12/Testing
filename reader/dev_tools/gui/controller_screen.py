import PySimpleGUI as sg
import sys
sys.path.insert(0, '.')
import reader.lib_hardware_interface.client as hwclient
from itertools import chain as flatten
import builtins


def controller_screen(transport, window_name='Controller'):

    def get_arg_comps(cmd, name, arg_type):
        if arg_type in ['int', 'float', 'bool']:
            wdgt = sg.Input(size=(10,1), key=f'{cmd}-input-{name}')
        elif arg_type in ['str']:
            wdgt = sg.Input(size=(30,1), key=f'{cmd}-input-{name}')
        elif arg_type in ['list']:
            wdgt = sg.Multiline(size=(30,3), key=f'{cmd}-input-{name}')
        else:
            raise Exception(f"arg type {arg_type} not supported")
        return [sg.Text(name), wdgt]

    def get_return_comp(cmd, arg_type):
        key=f'{cmd}-output'
        if arg_type in ['list']:
            wdgt = sg.Multiline(size=(50,3), key=key)
        else:
            wdgt = sg.Input(size=(50,1), key=key)
        return wdgt

    def get_cmd_comps(cmd, args):
        arg_comps = [
            get_arg_comps(cmd, name, arg_type) 
            for name, arg_type in args.items()
            if name != 'return'
        ]
        print(args.items())
        ret_type = next((t for (n,t) in args.items() if n == 'return'), None)
        return [
            sg.Text(cmd),
            *list(flatten(*arg_comps)),
            sg.Button('Run', key=f'{cmd}-run'),
            sg.Text("Output:"),
            get_return_comp(cmd, ret_type)
        ]
        
    def get_handlers(cmd, args):

        def str_to_class(classname):
            if classname == 'bool':
                return lambda x: x == 'True'
            if classname == 'list':
                return lambda x: [str(n) for n in x.split('\n')]
            if classname == 'bytes':
                return lambda x: str(x)
            return getattr(builtins, classname)

        def run_cmd(values, client, window):
            arg_values = {
                k.replace(f'{cmd}-input-',''):v for k,v in values.items()
                if k.startswith(f'{cmd}-input-')
            }
            arg_types = {
                k:str_to_class(v) for k,v in args.items()
            }
            arg_values_casted = [
                arg_types[k](v) for k,v in arg_values.items()
            ]
            try:
                print([(type(a),a) for a in arg_values_casted])
                res = getattr(client, cmd)(*arg_values_casted)
                window[f'{cmd}-output'].update(str(res))
            except Exception as e:
                window[f'{cmd}-output'].update(f"ERROR: {e}")

        return {
            f'{cmd}-run': run_cmd
        }

    controller_client = hwclient.HardwareClient(transport)
    print(f'Retrieving spec from controller at transport {transport}...')
    spec = controller_client.spec()
    layout = [
        get_cmd_comps(cmd, args['args'])
        for cmd, args in spec.items()
    ]
    window = sg.Window(window_name, layout, finalize=True, modal=False)

    handlers = [ 
        get_handlers(cmd, args['args']) 
        for cmd, args in spec.items()
    ]
    # merge all the handlers together
    handlers = {k:v for h in handlers for k,v in h.items()}

    while True:
        event, values = window.read()
        # print(event, values)
        if event == sg.WIN_CLOSED:
            raise Exception('Window closed.')
        if event == 'load':
            transports = values['transports']
            window.close()
            return transports.split('\n')
        handlers[event](values, controller_client, window)



