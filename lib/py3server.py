import socketserver
from lib.server import HoneyPokeServer
import sys
import traceback
import os

class TCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        if os.geteuid() != 0 and os.getegid() != 0:
            while True:
                data = self.rfile.readline().strip()

                port = self.server.server_address[1]

                decoded_data = ""
                try:
                    decoded_data = data.decode('utf-8')
                except UnicodeDecodeError:
                    decoded_data = "(BINARY DATA)"

                if decoded_data != "":
                    self.server.on_handle(self.client_address, decoded_data)
                # server.write_input(server.get_log_path(port, "tcp"), self.client_address, data)
        else:
            print("Permissions not dropped")

class UDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        if os.geteuid() != 0 and os.getegid() != 0:
            data = self.request[0].strip()
            port = self.server.server_address[1]
            self.server.on_handle(self.client_address, data.decode('utf-8'))
            # server.write_input(server.get_log_path(port, "udp"), )
        else:
            print("Permissions not dropped")
        

class Py3HoneyPokeServer(HoneyPokeServer):

    def __init__(self, port, protocol, queue):
        super(Py3HoneyPokeServer, self).__init__(port, protocol, queue)
        self._server = None

    def stop(self):
        if self._server != None:
            self._server.shutdown()

    def run(self):
        if self._protocol == "tcp":
            try:
                self._server = socketserver.TCPServer(('', self._port), TCPHandler)
                self._server.allow_reuse_address = True
                self._server.on_handle = self.on_handle
                self._server.server_activate()
                self.ready()
                while os.geteuid() == 0 or os.getegid() == 0:
                    pass
                print("Starting TCP server at " + str(self._port) + "\n")
                self._server.serve_forever()
            except Exception as e:
                print("!- Error at starting TCP thread for port " + str(self._port) + ", Error: " + str(e))
        elif self._protocol == "udp":
            try:
                self._server = socketserver.UDPServer(('', self._port), UDPHandler)
                self._server.allow_reuse_address = True
                self._server.on_handle = self.on_handle
                self._server.server_activate()
                self.ready()
                while os.geteuid() == 0 or os.getegid() == 0:
                    pass
                print( "Starting UDP server at " + str(self._port) + "\n")
                self._server.serve_forever()
            except Exception as e:
                print ("!- Error at starting UDP thread for port " + str(self._port) + ", Error: " + str(e))
        else:
            print("Invalid protocol")
            
    def on_handle(self, client_ip, data):
        self.write_input(client_ip[0], client_ip[1], data)
