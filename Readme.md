# Xel
## _A mesh model for reliable and generic services_

Xel is a generic service mesh model for building reliable big data processing in multiclouds.

- Create your own service repository.
- Deploy your service repository in any kind of infrastructure, from local machines to cloud or multi-cloud.
- Use the deployed services to build dynamic solutions.
- Execute the solution and enjoy the ✨Magic ✨.

## Features

- Convert your applications with a black box model into services.
- Deploy your services on any infrastructure, whether locally, in a cluster, in the cloud and even in multiple clouds.
- Create replicas of your services to add reliability to your mesh.
- Create dynamic solutions using the services in the mesh.
## Tech

The GR-Dataservice prototype uses a number of open source projects in currently implemented services:

- [Tensorflow](https://www.tensorflow.org/)- open source library for numerical computation and large-scale machine learning.
- [scikit-learn](https://scikit-learn.org/stable/) Machine Learning in Python.
- [GROBID](https://grobid.readthedocs.io/en/latest/) Machine learning library. 
- [GloVe](https://nlp.stanford.edu/projects/glove/) Unsupervised learning algorithm for obtaining vector representations for words.
- [Docker](https://www.docker.com/) A containers plataform.


## Installation

GR-Dataservice requires [Python 3.7+](https://www.python.org/) to run.
The installation and deployment of this prototype is done using virtual containers, using the [Docker platform](https://www.docker.com/) and the [Docker-compose](https://docs.docker.com/compose/) tool.

Once Docker and Docker compose are installed, use the following command to build the container images:

```sh
docker-compose up -d
```
To see the lofs...
```sh
docker-compose up
```
To rebuild the images in case of any change...
```sh
docker-compose up --build
```
## Important files
 + [_AG/_](./AG). Contains the API Gateway scripts.
 + [_coordinator_structure.json_](./coordinator_structure.json). Draft of the configuration file of services deployed on the mesh (dynamically generated once deployed)
 + [_BuildingBlocks/_](./BuildingBlocks). Folder with all the building blocks.
 + [_Examples/_](Examples). Folder with mesh configuration examples and designed solutions.
 + [_IAG/_](./IAG)  Contains the  Internal API Gateway scripts.
 + [_localdata/_](./localdata). Folder with datasets for testing.
 + [_NonFunctional/_](./NonFunctional). Folder with non-functional requirements scripts.

#### Using diferent mesh configurations
You can deploy multiple replicas of the same service by using the configurations that the docker platform offers, or create multiple containers with different specifications. In the **_Examples/Infrastructure/_** folder there are some examples of configurations that can be made. Additionally, tools such as Docker-swarm or kubernetes can be used for the deployment and coordination of the containers in the cloud. For a simple cloud deployment example, docker-swarm may be the easiest option. To do this, the following commands are used:

Create a repository:
```sh
$ docker service create --name registry --publish published=5000,target=5000 registry:2
```
To create the images with compose
```sh
$ cd Examples/Infrastructure/B/
$ docker-compose up -d
```
Push images to repository
```sh
$ docker-compose push
```
Push the images to swarm
```sh
$ docker stack deploy --compose-file docker-compose.yml Xel
```


## Running and designing solutions

### Design
Once a mesh of deployed services exists, they can be used to create solutions.
The solutions are designed based on instructions defined as a tree, following the following structure:
```json
{
 "data-map":{"data":"","type":"LAKE"},
 "auth":{"workspace": "<catalog>", "user": "<token_user>"},
 "DAG":{ 
    "id": "root",
    "service": "root",
    "root": true,
    "childrens": [
      {
        "name": "Acquisition",
        "childrens": [],
        "params": {
          "DOWNLOAD_server": "BB_FILES",
          "NAMEFILE": "Covid(reduced)",
          "EXT": "csv",
          "URL": "",
          "ID_FILE": "",
          "USER": "",
          "PASS": "",
          "SAVE_DATA": false
        }
    },
    ]
    }
}
```
where:
+ **service** is the name of the service defined in docker-compose.yml file.
+ **params** is a set of params defined in a key-valye format that will be used for the app to preform the data transformation.
+ **childrens** is a set of childres with the instructions to be executed for services after finish _this_ parent.

As well as the instructions, the dataset to be transformed must be sent. Below are the available ways up to this version of xel to provide a dataset

+ **Upload it as a file**. Dataset can be send to the mesh as _multipart/form-data_ to the path /UploadDataset. In addition to the file, information must be provided for storage in the lake, such as the user identifier and the catalog (or workspace) where it will be stored, this is done as follows:
  ```json
    {"workspace": "<catalog>", "user": "<token_user>"}
   ```

  Once the file has been uploaded it needs to be specified in the json with the instructions. In this case, the dataset will be in the data lake of xel, and it is specified as follows:

  ```json
    {"data_map":{"data":{"token_user":"<token_user>","catalog":"<catalog>","filename":"<name of the dataset>"},"type":"LAKE"}}
  ```

+ Using the Acquisition _BB_ to access remote or local datasets (in localdata folder). In this case, since an acquisition BB will be used to obtain the data, xel is not required to provide input data. This is specified in the statement json as follows:
  ```json
    {"data_map":{"data":,"type":"DUMMY"}}
  ```
  
### Execution

To execute the solutions can be done in 2 ways:
+ Using the GUI deployed in http://www.adaptivez.org.mx/AEM-Eris/meteo/ specifying the IP of the API GATEWAY of the mesh (or using the already deployed services in the adaptivez server)
+ Using the Client.py app.  Execute this client with the following command:
    ```sh
    $ python3 Client.py localhost:25000 ./Examples/Solutions/map_reduce.json ./localdata/EC_mun.csv 
    ```
    where:
    + 127.0.0.1:25000 is the host ip with the AG.
    + ./Examples/Solutions/map_reduce.json  is the path for the json file with the instructions.
    + ./localdata/EC_mun.csv is the path with the file of dataset (this is optional depending of the instructions).
    
    

## Credits
* Author: J.Armando Barrón-Lugo
* Email: juan.barron@cinvestav.mx, juanbarronlugo@gmail.com

This work has been partially supported by the project 41756 ``Plataforma tecnológica para la gestión, aseguramiento, intercambio y preservación de grandes volúmenes de datos en salud y construcción de un repositorio nacional de servicios de análisis de datos de salud'' by the  FORDECYT-PRONACES.

