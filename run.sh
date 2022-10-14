#!/bin/bash

#(C) Copyright FORCOAST H2020 project under Grant No. 870465. All rights reserved.

# Copyright notice
# --------------------------------------------------------------------
#  Copyright 2022 Deltares
#   Daniel Twigt
#
#   daniel.twigt@deltares.nl
#
#    This work is licenced under a Creative Commons Attribution 4.0 
#	 International License.
#
#
#        https://creativecommons.org/licenses/by/4.0/
# --------------------------------------------------------------------

# Example: python forcoast_sm_a1.py -p sado_estuary -T 2021-12-04 -lat 38.7229344 -lon -9.0917642 -lim 2
# Example: python forcoast_sm_a1.py -p limford -T 2021-11-26 -lat 56.9404 -lon 9.0434 -lim 1
# Example: ./run.sh sado_estuary 2021-12-04 38.7229344 -9.0917642 2 5267228188:AAGx60FtWgHkScBb3ISFL1dp6Oq_9z9z0rw -1001299880558
# Example: ./run.sh limfjord 2021-11-26 56.9404 9.0434 1 5267228188:AAGx60FtWgHkScBb3ISFL1dp6Oq_9z9z0rw -1001299880558

INITIAL_DIR="$(pwd)"

# Clean output folder
rm /usr/src/app/output/*.png
rm /usr/src/app/output/*.csv

cd /usr/src/app

python forcoast_sm_a1.py -p $1 -T $2 -lat $3 -lon $4 -lim $5
python bulletin_script.py

cp /usr/src/app/output/bulletin.png $INITIAL_DIR

echo "python send_bulletin.py -T $6 -C $7-B /usr/src/app/output/bulletin.png -M file"
python send_bulletin.py -T $6 -C $7 -B /usr/src/app/output/bulletin.png -M file

exit 0

