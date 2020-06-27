from socketIO_client import SocketIO, LoggingNamespace
from os import getenv

class api_centinel:
    def __init__(self):
        url = getenv('CENTINEL') #read url}
        self.socket =  SocketIO(url, LoggingNamespace)

    def UpdateTaskStatus(self,workflow,task,status):
        message = workflow+","+ task +","+status
        self.socket.emit('status',message)
