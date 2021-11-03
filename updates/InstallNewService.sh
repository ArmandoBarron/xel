
##wizard de instalacion de nuevos servicios. 

#Carpeta de instalacion
FOLDER_SERVICES="../BuildingBlocks/"

echo "Welcome to the installation assistant"
echo "1.-Introduce the name of the service:"
read SERVICE_NAME

#se crea la carpeta que contendra todos los modulos del servicio
mkdir -p ${FOLDER_SERVICES}${SERVICE_NAME}"/app/"

#se copian los elementos correspondientes a la carpeta del servicio
    cp building_middleware.py ${FOLDER_SERVICES}${SERVICE_NAME}"/app/"
    cp Postman.py ${FOLDER_SERVICES}${SERVICE_NAME}"/app/"
    cp C.py ${FOLDER_SERVICES}${SERVICE_NAME}"/app/"
    cp S.py ${FOLDER_SERVICES}${SERVICE_NAME}"/app/"
    cp -R TPS/ ${FOLDER_SERVICES}${SERVICE_NAME}"/app/"


    # se copia el docker-file y lista de dependencias
    cp requirements.txt ${FOLDER_SERVICES}${SERVICE_NAME}"/"
    cp Dockerfile ${FOLDER_SERVICES}${SERVICE_NAME}"/"


while true;
do
        echo "2.-Introduce the name of the first APP (by default is called REQUEST):"
        read APP_NAME
        if [ -z "$APP_NAME" ]
        then 
            APP_NAME="REQUEST"
        fi

        APP_NAME=${APP_NAME^^} #UPPERCASE 

        echo "3.- Intorduce the path of the application (e.g. /home/user1/app.py or /home/user1/apps/)"
        read path_app

        #se crea la carpeta que contendra todos los modulos de la app
        mkdir -p ${FOLDER_SERVICES}${SERVICE_NAME}"/app/"${APP_NAME}

        #se copian los elementos correspondientes a la carpeta del servicio
            cp blackbox/blackbox_middleware.py ${FOLDER_SERVICES}${SERVICE_NAME}"/app/"${APP_NAME}
            cp blackbox/Trigger.py ${FOLDER_SERVICES}${SERVICE_NAME}"/app/"${APP_NAME}
            cp blackbox/utils.py ${FOLDER_SERVICES}${SERVICE_NAME}"/app/"${APP_NAME}
            cp blackbox/AppConfig.json ${FOLDER_SERVICES}${SERVICE_NAME}"/app/"${APP_NAME}
            cp blackbox/CustomScript.py ${FOLDER_SERVICES}${SERVICE_NAME}"/app/"${APP_NAME}

            cp $path_app ${FOLDER_SERVICES}${SERVICE_NAME}"/app/"${APP_NAME}

        echo "APP created successfully"
        echo "4.- Do you wish to add another APP "
        read -r -p "Yes or no? " more   
        if [[ $more =~ ^([yY][eE][sS]|[yY])$ ]]
        then
            echo "You chose yes"
        else
            exit 0
        fi
done