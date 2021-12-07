FROM python:3.9

RUN apt-get update 

WORKDIR /usr/src/app

COPY ["requirements.txt", "./"]
RUN pip3 install --no-cache-dir -r requirements.txt

# Folders
COPY ["icons/", "/usr/src/app/icons"]
COPY ["output/", "/usr/src/app/output"]

# Files
COPY ["*.py", "/usr/src/app"]
COPY ["*.png", "/usr/src/app"]
COPY ["*.ttf", "/usr/src/app"]
COPY ["*.sh", "/usr/src/app"]

RUN chmod 755 /usr/src/app/run.sh

ENTRYPOINT ["bash", "-c"]
# ENTRYPOINT ["/usr/src/app/run.sh"]
