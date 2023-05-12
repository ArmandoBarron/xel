#!/bin/bash
#BASH FOR CREATE DATASET FOR GROBID

# Basic while loop
counter=1
A=100
B=200

### 100 A
while [ $counter -le $A ]
do
filename=FileA_$counter.pdf
cp File.pdf $filename
zip ${A}FilesA.zip $filename
rm $filename
((counter++))
done
echo All done
counter=1

### 100 B
while [ $counter -le $A ]
do
filename=FileB_$counter.pdf
cp File.pdf $filename
zip ${A}FilesB.zip $filename
rm $filename
((counter++))
done
echo All done

counter=1
### 200
while [ $counter -le $B ]
do
filename=FileC_$counter.pdf
cp File.pdf $filename
zip ${B}FilesC.zip $filename
rm $filename
((counter++))
done
echo All done
