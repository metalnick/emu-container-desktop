import socket
import time


class EmuContainerMessenger:
    def __init__(self, ipaddr: str, port: int):
        self._ipaddr = ipaddr
        self._port = port

    def send_message(self, message: str):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._ipaddr, self._port))
        try:
            sock.sendall(message.encode())
            response = sock.recv(1024).decode()
            print("Received: {}".format(response))
        finally:
            sock.close()

if __name__ == "__main__":
    messenger = EmuContainerMessenger('127.0.0.1', 55453)
    # messenger.send_message('{"command": "get_roms", "emulator": "SNES"}')
    # messenger.send_message('{"command": "get_emulators"}')
    messenger.send_message('{"command": "start", "emulator": "SNES"}')
    # time.sleep(5)
    # messenger.send_message('{"command": "stop", "emulator": "SNES"}')
    # messenger.send_message('{"command": "shutdown"}')
