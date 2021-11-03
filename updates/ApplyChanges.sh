BB_PATH="../BuildingBlocks/"

for i in `ls $BB_PATH`; do
    echo $i
    cp building_middleware.py $BB_PATH$i"/app/"
    cp Postman.py $BB_PATH$i"/app/"
    cp C.py $BB_PATH$i"/app/"
    cp S.py $BB_PATH$i"/app/"

    for j in `ls -d $BB_PATH$i/app/*/`; do
        echo $j
        cp blackbox/blackbox_middleware.py $j
        cp blackbox/Trigger.py $j
        cp blackbox/utils.py $j
    done

done

echo "SERVICES HAVE BEEN UPDATED!"