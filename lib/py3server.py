import socketserver
from lib.server import HoneyPokeServer
import sys
import traceback
import os

class TCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        print(os.geteuid())
        print(os.getegid())
        print(os.getuid())
        print(os.getgid())
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

class UDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        print(os.geteuid())
        print(os.getegid())
        print(os.getuid())
        print(os.getgid())
        data = self.request[0].strip()
        port = self.server.server_address[1]
        self.server.on_handle(self.client_address, data.decode('utf-8'))
        # server.write_input(server.get_log_path(port, "udp"), )
        

class Py3HoneyPokeServer(HoneyPokeServer):

    def __init__(self, port, protocol):
        super(Py3HoneyPokeServer, self).__init__(port, protocol)

    def start(self):
        if self._protocol == "tcp":
            try:
                server = socketserver.TCPServer(('', self._port), TCPHandler)
                server.allow_reuse_address = True
                server.on_handle = self.on_handle
                print(server.server_address)
                server.server_activate()
                self.drop_privileges()
                print("Starting TCP server at " + str(self._port) + "\n")
                server.serve_forever()
            except Exception as e:
                print("!- Error at starting TCP thread for port " + str(self._port) + ", Error: " + str(e))
        elif self._protocol == "udp":
            try:
                server = socketserver.UDPServer(('', self._port), UDPHandler)
                server.allow_reuse_address = True
                server.on_handle = self.on_handle
                server.server_activate()
                self.drop_privileges()
                print( "Starting UDP server at " + str(self._port) + "\n")
                server.serve_forever()
            except Exception as e:
                print ("!- Error at starting UDP thread for port " + str(self._port) + ", Error: " + str(e))
        else:
            print("Invalid protocol")
            
    def on_handle(self, client_ip, data):
        self.write_input(client_ip[0], client_ip[1], data)