import socket

class EmuContainerApp:
    def __init__(self, ipaddr: str, port: int):
        self._ipaddr = ipaddr
        self._port = port
        self._alive = False

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
    messager = EmuContainerApp('127.0.0.1', 55453)
    messager.send_message('{"command": "stop", "emulator": "SNES"}')