#!/bin/bash
# Example: run.sh -T 2021-07-13 -p 1 -d /data

INITIAL_DIR="$(pwd)"

# Clean output folder
rm /usr/src/app/output/*.png
rm /usr/src/app/output/*.csv

cd /usr/src/app

python forcoast_sm_a1.py -T $1 -lat $2 -lon $3 -lim $4
python bulletin_script.py

cp /usr/src/app/output/forcoast_a1_bulletin.png $INITIAL_DIR

exit 0

