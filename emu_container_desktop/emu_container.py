import configparser as cp
import os
import signal
from socketserver import BaseRequestHandler, ThreadingTCPServer
from threading import Thread
import json
import subprocess
import sys

# TODO: Server should handle requests to start, stop, etc. No need for a "local client". GUI/cmd line will make use of
# TODO: the same methods the server invokes


class ThreadedEmuServerRequestHandler(BaseRequestHandler):
    def handle(self):
        data = json.loads(self.request.recv(1024).decode())
        response = json.dumps(data)
        self.request.sendall(('Got message! {}'.format(response)).encode())
        if data["command"] == "start":
            self.start_emulator(data["emulator"])
        elif data["command"] == "stop":
            self.stop_emulator(data["emulator"])
        elif data["command"] == "shutdown":
            self.shutdown()

    def get_config(self):
        return self.server.config

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


class EmuServer(ThreadingTCPServer):
    def __init__(self, address: str, port: int, request_handler: BaseRequestHandler, config: cp):
        ThreadingTCPServer.__init__(self, (address, port), request_handler)
        self.allow_reuse_address = True
        self._config = config

    @property
    def config(self):
        return self._config


def start_server(address: str, port: int, config: cp, name='EmuServer') -> EmuServer:
    server = EmuServer(address, port, ThreadedEmuServerRequestHandler, config)
    server_thread = Thread(target=server.serve_forever, name=name, daemon=False)
    server_thread.start()
    # server.serve_forever()


def main():
    config = cp.ConfigParser()
    config.read("config/emucontainer.properties")
    try:
        start_server('127.0.0.1', 55453, config)
    except KeyboardInterrupt:
        sys.exit()

if __name__ == "__main__":
    main()
