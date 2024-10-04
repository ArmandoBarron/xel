BB_PATH="../BuildingBlocks/"

for i in `ls $BB_PATH`; do
    echo $i
    cp requirements.txt $BB_PATH$i"/" #requerimientos de la malla 

    cp building_middleware.py $BB_PATH$i"/app/"
    cp Postman.py $BB_PATH$i"/app/"
    cp C.py $BB_PATH$i"/app/"
    cp S.py $BB_PATH$i"/app/"
    cp genesis_client.py $BB_PATH$i"/app/"
    cp BB_dispatcher.py $BB_PATH$i"/app/"
    cp ClientPattern.py $BB_PATH$i"/app/"
    cp ThreadCreator.py $BB_PATH$i"/app/"

    cp conf.json $BB_PATH$i"/app/"

    rm -r $BB_PATH$i"/app/storage/"

    cp -r storage/ $BB_PATH$i"/app/"
    cp functions.py $BB_PATH$i"/app/"



    for j in `ls -d $BB_PATH$i/app/*/`; do
        folder_name=$(basename "$j")
    
        # Ignorar la carpeta 'storage'
        if [ "$folder_name" == "storage" ]; then
            echo "Ignorando la carpeta 'storage'"
            continue
        fi
        echo $j
        cp blackbox/blackbox_middleware.py $j
        cp blackbox/Trigger.py $j
        cp blackbox/utils.py $j
    done

done

echo "SERVICES HAVE BEEN UPDATED!"