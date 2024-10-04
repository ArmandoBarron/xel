
import os
from mictlanx.v4.client import Client
from mictlanx.utils.index import Utils as UtilsX
import json

class mictlanx_client:

    def __init__ (self,bucket_id,LOGER = None):

        self.LOGER = LOGER
        MICTLANX_CLIENT_ID         = os.environ.get("MICTLANX_CLIENT_ID","client-0")
        self.MICTLANX_DEFAULT_BUCKET_ID = bucket_id
        self.OUTPUT_PATH = os.environ.get("MICTLANX_OUTPUTH_PATH","mictaln/data")
        MICTLANX_DEBUG             = bool(int(os.environ.get("MICTLANX_DEBUG","1")))
        MICTLANX_MAX_WORKERS       = int(os.environ.get("MICTLANX_MAX_WORKERS","2"))
        MICTLANX_LOG_PATH          = os.environ.get("MICTLANX_LOG_PATH","./log")
        routers = list(UtilsX.routers_from_str(os.environ.get("MICTLANX_ROUTERS","mictlanx-router-0:148.247.201.141:60667")))
        self.client = Client(
            client_id      = MICTLANX_CLIENT_ID,
            routers         = routers,
            debug           = MICTLANX_DEBUG,
            max_workers     = MICTLANX_MAX_WORKERS,
            bucket_id       = self.MICTLANX_DEFAULT_BUCKET_ID,
            log_output_path = MICTLANX_LOG_PATH    
        )

    # for storage
    def put(self,token_data,datapath,metadata={},chunk_size="1MB",bucket_id=None):

        bucket_id = bucket_id if bucket_id is not None else self.MICTLANX_DEFAULT_BUCKET_ID

        result = self.client.update_from_file(
            path       = datapath,
            chunk_size = chunk_size,
            bucket_id  = bucket_id,
            key=token_data,
            tags       = {"metadata":json.dumps(metadata)}
        )

        #delete if exist
        #del_result = self.client.delete(
        #    bucket_id       = bucket_id,
        #    key = token_data
        #)
        ##put new file
        #result = self.client.put_file_chunked(
        #    path       = datapath,
        #    chunk_size = chunk_size,
        #    bucket_id  = bucket_id,
        #    key=token_data,
        #    tags       = {"metadata":json.dumps(metadata)}
        #)
        if result.is_ok:
            return {"status":"OK"}
        else:
            self.LOGER.error("_"*40)
            self.LOGER.error("el error es {}".format(str(result.unwrap_err())))
            return {"status":"ERROR"}

    def get(self,bucket_id,token_data):
        bucket_id = bucket_id if bucket_id is not None else self.MICTLANX_DEFAULT_BUCKET_ID

        return self.client.get(
            bucket_id=bucket_id,
            key=token_data,
            chunk_size="1MB",
            headers = {
                "Consistency-Model":"STRONG"
            }
        )
    
    def get_to_flie(self,bucket_id,token_data,path):
        bucket_id = bucket_id if bucket_id is not None else self.MICTLANX_DEFAULT_BUCKET_ID

        return self.client.get_to_file_with_retry(
            bucket_id=bucket_id,
            key=token_data,
            output_path=path,
            chunk_size="1MB"#,
            #headers = {
            #    "Consistency-Model":"STRONG"
            #}
        )
        
    def locate(self,token_data):
        url_data = "http://localhost:60666/api/v3/%s" % (token_data)
        return url_data