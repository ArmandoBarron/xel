
from Client import CltFunxion,DAG,Service

Client = CltFunxion()
#Client.FlushTokenSolution()

#Client.FlushTokenSolution()
datos_acceso = Client.login()

#crear servicio
serv1 = Service("query sexo","transform_ds",{"query_flt":"SEXO=='Total'",
                                        "exec_code":"",
                                        "query_list":"",
                                        },"Query a todos los sexos",actions="EVAL")

Client.dag.add_service(serv1)


#Client.ForceExec()
deploy_info = Client.deploy()


datamap = Client.create_datamap(token="85e9be65f2281528a45b3956293ed2177e93246c2b63458eb05f6e64b60fc0c9",
                                task = "query",
                                source="SOLUTION")

Client.run(datamap)
Client.monitoring(clean_after_complete=False)
Client.share()


Client.save_context()