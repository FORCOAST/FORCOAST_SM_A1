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

FROM python:3.9

RUN apt-get update 

WORKDIR /usr/src/app

COPY ["requirements.txt", "./"]
RUN pip3 install --no-cache-dir -r requirements.txt

# Folders
RUN mkdir -p /usr/src/app/output
COPY ["icons/", "/usr/src/app/icons"]

# Files
COPY ["*.py", "/usr/src/app"]
COPY ["*.png", "/usr/src/app"]
COPY ["*.ttf", "/usr/src/app"]
COPY ["*.sh", "/usr/src/app"]

RUN chmod 755 /usr/src/app/run.sh

# ENTRYPOINT ["bash", "-c"]
ENTRYPOINT ["/usr/src/app/run.sh"]
