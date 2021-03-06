
# Watches for missed ports
from scapy.all import *

import threading
import netifaces

class HoneyPokeWatcher(threading.Thread):
    def __init__(self, ssh_port, ignore_addr, check_server):
        threading.Thread.__init__(self)
        self._check_server = check_server
        self.daemon = True
        self._ignore_addr = ignore_addr
        self._ssh_port = ssh_port

        self._addresses = []

        for iface in netifaces.interfaces():
            address_list = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in address_list:
                ipv4_addresses = address_list[netifaces.AF_INET]
                for address in ipv4_addresses:
                    self._addresses.append(address['addr'])

    def is_incoming(self, packet):
        try:
            if IP in packet:
                if str(packet[IP].dst) in self._addresses and str(packet[IP].src) not in self._ignore_addr:
                    return True
                    
        except:
            pass
            
        return False

    def check_port(self, packet):
        if self.is_incoming(packet):
            if TCP in packet and packet[TCP].dport != self._ssh_port:
                self._check_server(packet[TCP].dport, "tcp")
            elif UDP in packet:
                self._check_server(packet[UDP].dport, "udp")
        packet = None 

    def run(self):
        sniff(filter="tcp or udp", prn=self.check_port, store=0)
        print("Done sniffing")
    