import socketserver
from lib.server import HoneyPokeServer
import sys
import traceback
import os

class TCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        if os.geteuid() == 0 or os.getegid() == 0:
            # print("Permissions not dropped")
            return

        # print(dir(self.connection))
        full_data = b""
        try:
            data = self.rfile.readline()
            failsafe = False
            while data != b"" and failsafe == False:
                full_data += data
                data = self.rfile.readline()

                # Fail safe, don't got over 100M
                if len(full_data) > 104857600:
                    print("failsafe hit!")
                    failsafe = True

            port = self.server.server_address[1]

            decoded_data = ""
            try:
                decoded_data = full_data.decode('utf-8')
                self.server.on_handle(self.client_address, decoded_data, False)
            except UnicodeDecodeError:
                decoded_data = full_data
                self.server.on_handle(self.client_address, decoded_data, True)
        except ConnectionResetError:
            self.server.on_handle(self.client_address, "--SCAN--", False)

           

class UDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        if os.geteuid() == 0 or os.getegid() == 0:
            # print("Permissions not dropped")
            return

        data = self.request[0].strip()
        port = self.server.server_address[1]

        try:
            decoded_data = data.decode('utf-8')
            self.server.on_handle(self.client_address, decoded_data, False)
        except UnicodeDecodeError:
            self.server.on_handle(self.client_address, data, True)


class Py3HoneyPokeServer(HoneyPokeServer):

    def __init__(self, port, protocol, loggers, queue):
        super(Py3HoneyPokeServer, self).__init__(port, protocol, queue)
        self._server = None
        self._loggers = loggers

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
            
    def on_handle(self, client_ip, data, is_binary):

        if len(data) > 2048 or is_binary:
            large_file = self.save_large(data)
            data = "Output saved at " + large_file
            print(data)

        for logger in self._loggers:
            logger.log(client_ip[0], client_ip[1], self._protocol, self._port, data, is_binary)
        # self.write_input(client_ip[0], client_ip[1], data)
