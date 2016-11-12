
# Watches for missed ports
from scapy.all import *

import threading
import netifaces

class HoneyPokeWatcher(threading.Thread):
    def __init__(self, ignore_list, check_server):
        threading.Thread.__init__(self)
        self._check_server = check_server
        self.daemon = True
        self._ignore_list = ignore_list
        

    def is_incoming(self, packet):
        if IP in packet:
            for iface in netifaces.interfaces():
                address_list = netifaces.ifaddresses(iface)
                ipv4_addresses = address_list[netifaces.AF_INET]


                for addr in ipv4_addresses:
                    if str(packet[IP].dst) == addr['addr'] and str(packet[IP].src) not in self._ignore_list:
                        return True
        
        return False

    def check_port(self, packet):

        if self.is_incoming(packet):
            if TCP in packet:
                self._check_server(packet[TCP].dport, "tcp")
            elif UDP in packet:
                self._check_server(packet[UDP].dport, "udp")

    def run(self):
        sniff(filter="ip", prn=self.check_port)
        print("Done sniffing")
    