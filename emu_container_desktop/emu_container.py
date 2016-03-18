import configparser as cp
from socketserver import TCPServer, ThreadingMixIn, BaseRequestHandler
from threading import Thread
import socket


# TODO: Server should handle requests to start, stop, etc. No need for a "local client". GUI/cmd line will make use of
# TODO: the same methods the server invokes
class ThreadedEmuServerRequestHandler(BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        response = data.decode()
        self.request.sendall(('Got message! {}'.format(response)).encode())


class EmuServer(ThreadingMixIn, TCPServer):
    allow_reuse_address = True
    pass


# class EmuContainerApp:
#     def __init__(self, ipaddr: str, port: int):
#         self._ipaddr = ipaddr
#         self._port = port
#
#     def send_message(self, message: str):
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         sock.connect((self._ipaddr, self._port))
#         try:
#             sock.sendall(message.encode())
#             response = sock.recv(1024)
#             print("Received: {}".format(response.decode()))
#         finally:
#             sock.close()


def start_server(address: str, port: int, name='EmuServer') -> EmuServer:
    server = EmuServer((address, port), ThreadedEmuServerRequestHandler)
    server_thread = Thread(target=server.serve_forever, name=name, daemon=True)
    server_thread.start()

    return server


def main():
    config = cp.ConfigParser()
    config.read("config/emucontainer.properties")
    for key in config.sections():
        print(key)
    emu_server = start_server('127.0.0.1', 55453)
    emu_app = EmuContainerApp('127.0.0.1', 55453)
    emu_app.send_message('Ooga booga!')
    emu_server.shutdown()
    print("Shutdown!")
    emu_server.server_close()

if __name__ == "__main__":
    main()
