from elasticsearch import Elasticsearch
import datetime

class ElasticSearchLogger(object):

    def __init__(self, config):
        self.__server = config['server']

    
    def log(self, remote_ip, remote_port, protocol, port, data, is_binary):
        es = Elasticsearch(self.__server)

        es.index(index='honeypoke', doc_type='connection', body={
            "time": datetime.datetime.now().isoformat(),
            "remote_ip": remote_ip,
            "remote_port": remote_port,
            "protocol": protocol,
            "port": port,
            "input": str(data),
            "is_binary": is_binary
        })
