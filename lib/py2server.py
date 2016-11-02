import SocketServer
from server import HoneyPokeServer
import sys
import traceback
import os

class TCPHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        
        if os.geteuid() != 0 and os.getegid() != 0:
            while True:
                data = self.rfile.readline().strip()
                if data != "":
                    port = self.server.server_address[1]
                    self.server.on_handle(self.client_address, data)
                # server.write_input(server.get_log_path(port, "tcp"), self.client_address, data)
        else:
            print("Permissions not dropped")

class UDPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        if os.geteuid() != 0 and os.getegid() != 0:
            data = self.request[0].strip()
            port = self.server.server_address[1]
            self.server.on_handle(self.client_address, data)
            # server.write_input(server.get_log_path(port, "udp"), )
        else:
            print("Permissions not dropped")

class Py2HoneyPokeServer(HoneyPokeServer):

    def __init__(self, port, protocol, queue):
        super(Py2HoneyPokeServer, self).__init__(port, protocol, queue)
        self._server = None

    def stop(self):
        if self._server != None:
            self._server.shutdown()

    def run(self):
        if self._protocol == "tcp":
            try:
                self._server = SocketServer.TCPServer(('', self._port), TCPHandler)
                self._server.allow_reuse_address = True
                self._server.on_handle = self.on_handle
                self._server.server_activate()
                self.ready()
                while os.geteuid() == 0 or os.getegid() == 0:
                    pass
                print "Starting TCP server at " + str(self._port) + "\n"
                self._server.serve_forever()
            except Exception as e:
                print "!- Error at starting TCP thread for port " + str(self._port) + ", Error: " + str(e) + str(sys.exc_info()) + traceback.format_exc()
        elif self._protocol == "udp":
            try:
                self._server = SocketServer.UDPServer(('', self._port), UDPHandler)
                self._server.allow_reuse_address = True
                self._server.on_handle = self.on_handle
                self._server.server_activate()
                self.ready()
                while os.geteuid() == 0 or os.getegid() == 0:
                    pass
                print "Starting UDP server at " + str(self._port) + "\n"
                self._server.serve_forever()
            except Exception as e:
                print "!- Error at starting UDP thread for port " + str(self._port) + ", Error: " + str(e)
        else:
            print("Invalid protocol")
            
    def on_handle(self, client_ip, data):
        self.write_input(client_ip[0], client_ip[1], data)
