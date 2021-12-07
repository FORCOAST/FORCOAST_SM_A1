#!/bin/bash
# Example: python forcoast_sm_a1.py -p sado_estuary -T 2021-09-26 -lat 38.7229344 -lon -9.0917642 -lim 2
# Example: python forcoast_sm_a1.py -p limford -T 2021-11-26 -lat 56.9404 -lon 9.0434 -lim 1



INITIAL_DIR="$(pwd)"

# Clean output folder
rm /usr/src/app/output/*.png
rm /usr/src/app/output/*.csv

cd /usr/src/app

python forcoast_sm_a1.py -T $1 -lat $2 -lon $3 -lim $4
python bulletin_script.py

cp /usr/src/app/output/bulletin.png $INITIAL_DIR

exit 0

