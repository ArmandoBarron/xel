BB_PATH="../BuildingBlocks/"

for i in `ls $BB_PATH`; do
    echo $i
    cp building_middleware.py $BB_PATH$i"/app/"
    cp Postman.py $BB_PATH$i"/app/"
    cp C.py $BB_PATH$i"/app/"
    cp S.py $BB_PATH$i"/app/"

done
