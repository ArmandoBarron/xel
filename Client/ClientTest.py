
from Client import CltFunxion,DAG,Service


print("lib loaded")
Client = CltFunxion()
#Client.FlushTokenSolution()
Client.login()

#crear servicio
serv1 = Service("query","transform_ds",{"query_flt":"CAUSA_DEF=='C50'",
                                        "exec_code":"",
                                        "query_list":"",
                                        },"Query a C50",actions="EVAL")
#serv2 = Service("query sexo","transform_ds",{"query_flt":"SEXO='Total'"},"Query a todos los sexos",actions="EVAL")

Client.dag.add_service(serv1)
#   Client.dag.add_service(serv2,"query")


#Client.ForceExec()
deploy_info = Client.deploy()


datamap = Client.create_datamap("Chiapas_cancer.csv")

Client.run(datamap)
#Cliente.monitoring(clean_after_complete=True)
Client.monitoring(clean_after_complete=False)
Client.share()


Client.save_context()