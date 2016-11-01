import os
import datetime
import threading
import pwd
import grp

class HoneyPokeServer(threading.Thread):

    def __init__(self, port, protocol):
        threading.Thread.__init__(self)
        self._port = port
        self._protocol = protocol
        self._log_path = "./logs/port-" + self._protocol + "-" + str(self._port) + ".log"
        self.daemon = True

    def write_input(self, remote_host, remote_port, data):
        output_file = open(self._log_path, "a")
        now = datetime.datetime.now().isoformat()
        output_file.write(now + " - From {}:{} - {}\n".format(remote_host, remote_port, data))
        output_file.close()

    def run(self):
        start()

    def start(self):
        raise NotImplementedError

    def drop_privileges(self):
        print("Dropping!")
        nobody_uid = pwd.getpwnam('nobody').pw_uid
        nobody_gid = grp.getgrnam('nogroup').gr_gid

        os.setgroups([])

        os.setgid(nobody_uid)
        os.setuid(nobody_gid)

