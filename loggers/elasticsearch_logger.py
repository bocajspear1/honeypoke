from elasticsearch import Elasticsearch
import datetime
import platform 

class ElasticSearchLogger(object):

    def __init__(self, config):
        self.__server = config['server']
        if "https:" in self.__server:
            self.__use_ssl = True
        else:
            self.__use_ssl = False

        self.__verify_certs = config['verify']

    
    def log(self, remote_ip, remote_port, protocol, port, data, is_binary):
        es = Elasticsearch(self.__server, use_ssl=self.__use_ssl, verify_certs=self.__verify_certs)

        es.index(index='honeypoke', doc_type='connection', body={
            "time": datetime.datetime.now().isoformat(),
            "remote_ip": remote_ip,
            "remote_port": remote_port,
            "protocol": protocol,
            "port": port,
            "input": str(data),
            "is_binary": is_binary,
            "host": platform.node()
        })
