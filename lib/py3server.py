import socketserver
from lib.server import HoneyPokeServer
import sys
import traceback
import os
import socket
import ssl

class TCPHandler(socketserver.StreamRequestHandler):

    def handle(self):

        self.request.settimeout(60)
        full_data = b""
        port = self.server.server_address[1]

        try:

            if self.server.use_ssl:
                self.request.do_handshake()

            if os.geteuid() == 0 or os.getegid() == 0:
                # print("Permissions not dropped")
                return

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

            except ConnectionResetError:
                self.server.on_handle(self.client_address, "--SCAN--", False)
                return

        except socket.timeout:
            print("Timeout!")
            pass
        except ssl.SSLError:
            full_data = "--SSL Error--".encode("utf-8")
           
        decoded_data = ""
        try:
            decoded_data = full_data.decode('utf-8')
            self.server.on_handle(self.client_address, decoded_data, False)
        except UnicodeDecodeError:
            decoded_data = full_data
            self.server.on_handle(self.client_address, decoded_data, True)

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

    def __init__(self, port, protocol, use_ssl, loggers, queue):
        super(Py3HoneyPokeServer, self).__init__(port, protocol, queue)
        self._server = None
        self._loggers = loggers
        self._use_ssl = use_ssl

    def stop(self):
        if self._server != None:
            self._server.shutdown()

    def run(self):
        if self._protocol == "tcp":
            try:
                self._server = socketserver.ThreadingTCPServer(('', self._port), TCPHandler)
                if self._use_ssl:
                    self._server.socket = ssl.wrap_socket(
                        self._server.socket, 
                        keyfile="honeypoke_key.pem", 
                        certfile="honeypoke_cert.pem", 
                        do_handshake_on_connect=False, 
                        cert_reqs=ssl.CERT_NONE
                    )
                self._server.allow_reuse_address = True
                self._server.on_handle = self.on_handle
                self._server.use_ssl = self._use_ssl
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
                self._server = socketserver.ThreadingUDPServer(('', self._port), UDPHandler)
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

        print(is_binary, data)
        if is_binary:
            data = repr(bytes(data))

        if len(data) > 512:
            large_file = self.save_large(self._protocol, self._port, data.encode('utf-8'))
            data = "Output saved at " + large_file
            print(data)

        for logger in self._loggers:
            logger.log(client_ip[0], client_ip[1], self._protocol, self._port, data, is_binary, self._use_ssl)
        # self.write_input(client_ip[0], client_ip[1], data)
