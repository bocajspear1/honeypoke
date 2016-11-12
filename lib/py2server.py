import SocketServer
from socket import error as SocketError
from server import HoneyPokeServer
import errno
import sys
import traceback
import os

class TCPHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        
        if os.geteuid() == 0 or os.getegid() == 0:
            print("Permissions not dropped")
            return

        full_data = ""
        try:
            data = self.rfile.readline()
            failsafe = False
            while data != "" and failsafe == False:
                full_data += data
                data = self.rfile.readline()
                
                # Fail safe, don't got over 100M
                if len(full_data) > 104857600:
                    print("failsafe hit!")
                    failsafe = True

            port = self.server.server_address[1]

            binary = False

            try:
                unicode(full_data)
            except UnicodeDecodeError:
                binary = True

            if "\0" in full_data:
                binary = True
            
            self.server.on_handle(self.client_address, full_data, binary)
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise 
            self.server.on_handle(self.client_address, "--SCAN--", False)
        
                
            

class UDPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        if os.geteuid() == 0 or os.getegid() == 0:
            print("Permissions not dropped")
            return

        data = self.request[0].strip()
        port = self.server.server_address[1]

        try:
            unicode(data)
        except UnicodeDecodeError:
            binary = True

        if "\0" in data:
            binary = True

        self.server.on_handle(self.client_address, data, binary)

class Py2HoneyPokeServer(HoneyPokeServer):

    def __init__(self, port, protocol, loggers, queue):
        super(Py2HoneyPokeServer, self).__init__(port, protocol, queue)
        self._server = None
        self._loggers = loggers

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
            
    def on_handle(self, client_ip, data, is_binary):

        if len(data) > 2048 or is_binary:
            large_file = self.save_large(data)
            data = "Output saved at " + large_file
            print(data)

        for logger in self._loggers:
            logger.log(client_ip[0], client_ip[1], self._protocol, self._port, data, is_binary)
        # self.write_input(client_ip[0], client_ip[1], data)
