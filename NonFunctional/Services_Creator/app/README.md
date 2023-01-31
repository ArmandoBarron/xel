# Services_creator

## Basic configuration

In the *conf.json* file located at the root, change the values of **server_ip** and **server_port** with the desired address and ports.

## Deploy

To start the service it is necessary to go to the root folder (Services_Creator) and run 

```sh
docker-compose up
```

## Endpoints
### start_services

Responsible for deploying on-demand services. It receives a JSON with the following fields:

DAG: The workflow. From this flow the services to be deployed will be obtained.

id_stack: The id to be given to the deployed stack. In case the service does not exist, it will create its own id and return it to the user.

replicas: "Global" number of replicas to create for each service. Each service can have its own "replicas" value. In case a service does not contain such value, this "global" value will be applied. The value must be integer.

**Response**: A json indicating whether the services were deployed correctly or not. If the deployment was successful, an "ok" response is received. If there was a problem in the deployment you will receive an "error" response and the cause of the problem.

### remove_services
In charge of stopping and deleting a stack of services. It receives by url an **id** parameter that will be the identifier of the stack to stop. This identifier is the same that is sent to the **start_services** endpoint or in case no such endpoint is sent, it creates it and returns it in the response.

**Response**: A json that indicates if the services were stopped and removed (shutdown) correctly or not. If the shutdown was successful, an "ok" response is received. If there was a problem in the shutdown you receive an "error" response and the cause of the problem.

## Client

Inside the root folder there is a folder called "Client". Inside this folder you can run an example of "Services_Creator". To run the complete example it is necessary to run the exe.py file using Python. Inside the "Client" folder there are the following files:

client.py: File containing the methods to execute **start_services** and **remove_services**. So you can execute such methods as if it were a library. The **start_services** method receives as parameter the JSON to send. The **remove_services** method receives as parameter the identifier of the stack to stop.

conf.json: Configuration file where the values to consume the service (ip, port, endpoint names, etc.) are defined.

exe.py: File that can be executed to run a complete example. Inside it the methods of client.py are called as a library.

start_services_data.json. File containing a JSON example to be sent to the **start_services** endpoint. The exe.py file makes use of this JSON example
