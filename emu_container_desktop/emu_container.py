import configparser as cp
import os
import signal
from socketserver import BaseRequestHandler, TCPServer, ThreadingMixIn
from threading import Thread
import json
import subprocess
import sys
import glob

# TODO: Server should handle requests to start, stop, etc. No need for a "local client". GUI/cmd line will make use of
# TODO: the same methods the server invokes


class ThreadedEmuServerRequestHandler(BaseRequestHandler):
    def handle(self):
        print("Received message...")
        # print(self.request.recv(1024).decode('UTF-8'))
        data = json.loads(self.request.recv(1024).decode('UTF-8'))
        response = json.dumps(data)
        if data["command"] == "start":
            self.request.sendall(('Got message! {}\n'.format(response)).encode())
            self.start_emulator(emulator_name=data["emulator"])
        elif data["command"] == "play_rom":
            self.request.sednall(("Got message! {}\n".format(response)).encode())
            self.play_rom(emulator_name=data["emulator"], rom_path=data["rom_path"])
        elif data["command"] == "stop":
            self.request.sendall(('Got message! {}\n'.format(response)).encode())
            self.stop_emulator(emulator_name=data["emulator"])
        elif data["command"] == "shutdown":
            self.request.sendall(('Got message! {}\n'.format(response)).encode())
            self.shutdown()
        elif data["command"] == "get_emulators":
            emulators = '{'
            for i in range(len(self.get_config().sections())):
                if i == len(self.get_config().sections()) - 1 :
                    emulators += '"{}": "logo"}}\n'.format(self.get_config().sections()[i])
                else:
                    emulators += '"{}": "logo_path", '.format(self.get_config().sections()[i])
            self.request.sendall(emulators.encode())
        elif data["command"] == "get_roms":
            platform = data["emulator"]
            rom_path = self.get_config()[platform]['Roms']
            rom_extension = self.get_config()[platform].get('RomExtension', '')
            response = '{"roms": "'
            if not(rom_path.endswith('/')):
                rom_path += '/'
            if not(rom_extension == ''):
                rom_path += '*.{}'.format(rom_extension)
            roms = glob.glob(rom_path)
            for i in range(len(roms)):
                rom = roms[i]
                if i == len(roms) - 1:
                    response += rom+'"}}\n'
                else:
                    response += rom+', '
            self.request.sendall(response.encode())

    def get_config(self):
        return self.server.config

    def play_rom(self, emulator_name: str, rom_path: str):
        stdout, stderr = subprocess.Popen([self.get_config()[emulator_name]['Emulator'], rom_path])
        print(stdout.decode())
        print(stderr.decode())

    def start_emulator(self, emulator_name: str):

        stdout,stderr = subprocess.Popen([self.get_config()[emulator_name]['Emulator']],
                                         stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
        print(stdout.decode())
        print(stderr.decode())

    def stop_emulator(self, emulator_name: str):
        pid = subprocess.check_output(["pidof", self.get_config()[emulator_name]['Emulator']])
        os.kill(int(pid), signal.SIGTERM)

    def shutdown(self):
        self.server.shutdown()
        self.server.server_close()


class EmuServer(ThreadingMixIn, TCPServer):
    def __init__(self, address: str, port: int, request_handler: BaseRequestHandler, config: cp):
        TCPServer.allow_reuse_address = True
        TCPServer.__init__(self, (address, port), request_handler)
        self._config = config

    @property
    def config(self):
        return self._config


def start_server(address: str, port: int, config: cp, name='EmuServer') -> EmuServer:
    server = EmuServer(address, port, ThreadedEmuServerRequestHandler, config)
    server_thread = Thread(target=server.serve_forever, name=name, daemon=False)
    server_thread.start()


def main():
    config = cp.ConfigParser()
    config.read("config/emucontainer.properties")
    try:
        start_server('', 55453, config)
    except KeyboardInterrupt:
        sys.exit()

if __name__ == "__main__":
    main()
