from elasticsearch import Elasticsearch
import datetime
import platform 
from geolite2 import geolite2

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

        
        location = None

        reader = geolite2.reader()
        raw_loc_data = reader.get(remote_ip)

        if raw_loc_data and 'location' in raw_loc_data:
            location = {
                "lat": round(raw_loc_data['location']['latitude'], 2),
                "lon": round(raw_loc_data['location']['longitude'], 2),
            }
            

        es.index(index='honeypoke', doc_type='connection', body={
            "time": datetime.datetime.utcnow().isoformat(),
            "remote_ip": remote_ip,
            "remote_port": remote_port,
            "protocol": protocol,
            "port": port,
            "input": str(data),
            "is_binary": is_binary,
            "location": location,
            "host": platform.node()
        })
