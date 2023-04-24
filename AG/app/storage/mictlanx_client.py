
import os
from mictlanx.v3.client import Client
from mictlanx.v3.services.auth import Auth
from mictlanx.v3.services.proxy import Proxy
from mictlanx.v3.services.replica_manger import ReplicaManager
from mictlanx.v3.interfaces.payloads import PutPayload

class mictlanx_client:

    def __init__ (self):
        rm_service    = ReplicaManager(ip_addr = os.environ.get("MICTLANX_REPLICA_MANAGER_IP_ADDR"), port=int(os.environ.get("MICTLANX_REPLICA_MANAGER_PORT",20000)), api_version=3)
        auth_service  = Auth(ip_addr = os.environ.get("MICTLANX_AUTH_IP_ADDR"), port=int(os.environ.get("MICTLANX_AUTH_PORT",10000)), api_version=3)
        proxy_service = Proxy(ip_addr = os.environ.get("MICTLANX_PROXY_IP_ADDR"), port=int(os.environ.get("MICTLANX_PROXY_PORT",8080)), api_version=3)
        self.client  = Client(rm_service = rm_service, auth_service = auth_service,proxy = proxy_service,password = os.environ.get("MICTLANX_PASSWORD"))
        self.proxy_port = os.environ.get("MICTLANX_PROXY_PORT",8080)
        self.proxy_url = os.environ.get("MICTLANX_PROXY_IP_ADDR")

    # for storage
    def put(self,token_data,data_bytes,metadata={}):
        payload = PutPayload(key=token_data,bytes = data_bytes,metadata=metadata)
        res = self.client.put(payload)
        return res

    def get(token_data):
        return self.client.get(key = token_data)

    def locate(self,token_data):
        url_data = "http://%s:%s/api/v3/%s" % (self.proxy_url,self.proxy_port,token_data)
        return url_data