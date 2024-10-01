# set base image python:3.8-slim-buster
FROM python:3.8

# set working directory as app
WORKDIR /containers

# copy requirements.txt file from local (source) to file structure of container (destination) 
COPY requirements.txt requirements.txt

# Install the requirements specified in file using RUN
RUN pip3 install -r requirements.txt

# copy all items in current local directory (source) to current container directory (destination)
COPY . .

# command to run when image is executed inside a container
ENTRYPOINT [ "python3", "batch.py" ]