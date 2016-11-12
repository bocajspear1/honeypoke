# Need libpcap-dev

import time
import sys
import os
import argparse
import json
import pwd
import grp
import signal
import threading
import datetime

from loggers.elasticsearch_logger import ElasticSearchLogger
from loggers.file_logger import FileLogger

from lib.watcher import HoneyPokeWatcher

if sys.version_info.major == 2:
    from lib.py2server import Py2HoneyPokeServer as PyHoneyPokeServer
    from Queue import Queue
else:
    from lib.py3server import Py3HoneyPokeServer as PyHoneyPokeServer
    from queue import Queue

class ServerManager(object):

    def __init__(self, config):
        self._servers = []
        self._tcp_ports = []
        self._udp_ports = []
        self._config = config
        self._lock = threading.Lock()
        self._miss_lock = threading.Lock()
        self.__loggers = []
        self.setup_loggers()

    def setup_loggers(self):
        valid_loggers = ['elasticsearch', 'file']
        for item in self._config['loggers']:
            if item == 'elasticsearch':
                self.__loggers.append(ElasticSearchLogger(self._config['loggers'][item]['config']))
            elif item == "file":
                self.__loggers.append(FileLogger())
            else:
                print("Invalid logger")
                sys.exit(1)

        if len(self.__loggers) == 0:
            print("No loggers configured")
            sys.exit(1)

    # Used by HoneyPokeWatcher to see if a port has a server or not
    # If not, we record it and indicate we have seen it
    def check_server(self, port, protocol):

        if os.geteuid() == 0 or os.getegid() == 0:
            print("Permissions not dropped")
            return 

        if protocol == "tcp" and port not in self._tcp_ports or protocol == "udp" and port not in self._udp_ports:
            print("Missed port: " + protocol + " " + str(port))
            self._miss_lock.acquire()
            try:
                output_file = open("./logs/missed.log", "a")
                now = datetime.datetime.now().isoformat()
                output_file.write(now + " - Missed {} port {}\n".format(protocol, port))
                output_file.close()
            except Exception as e:
                print(e)
            finally:
                self._miss_lock.release()

            self.add_port(port, protocol)

    def add_port(self, port, protocol):
        self._lock.acquire()
        if protocol == "tcp":
            self._tcp_ports.append(port)
        elif protocol == "udp":
            self._udp_ports.append(port)
        self._lock.release()

    def add_server(self, port, protocol, loggers, queue):
        server = PyHoneyPokeServer(port, protocol, loggers, queue)
        self.add_port(port, protocol)
        server.start()
        self._servers.append(server)

    def start_servers(self):

        # Start watching for port misses
        watch = HoneyPokeWatcher(self._config['ignore_watch'], self.check_server)
        watch.start()

        # Prepare to start the servers
        server_count = len(self._config['ports'])
        print("Starting " + str(server_count) + " servers\n")
        wait = Queue(maxsize=server_count)

        # Add servers
        for port in self._config['ports']:
            self.add_server(int(port['port']), port['protocol'], self.__loggers, wait)

        # Wait until they indicate they have bound
        while not wait.full():
            pass

        # Drop privileges
        self.drop_privileges()

        # Wait until told to exit
        try:
            while True:
                time.sleep(2) 
        except KeyboardInterrupt:
            print("\nShutting down...")
            # for server in self._servers:
            #     server.stop()
            #     server.join()
            sys.exit(0)

    def drop_privileges(self):
        print("Dropping!")
        nobody_uid = pwd.getpwnam('nobody').pw_uid
        nobody_gid = grp.getgrnam('nogroup').gr_gid

        os.setgroups([])

        os.setgid(nobody_uid)
        os.setuid(nobody_gid)


parser = argparse.ArgumentParser(description='Look at what attackers are poking around with')
parser.add_argument('--config', help='Path to configuration file', required=True)

args = parser.parse_args()
config_file = args.config

if not os.path.exists(config_file):
    print("Config file does not exist")
    sys.exit(1)

config_data = open(config_file, "r").read()
config = json.loads(config_data)

if "loggers" not in config or "ports" not in config or "ignore_watch" not in config:
    print("Invalid config")
    sys.exit(1)

manager = ServerManager(config)
manager.start_servers()



