FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y upgrade && apt-get clean all

#RUN apt install cuda-10-1
#RUN apt install libcudnn7

RUN apt-get install -y libsm6 libxext6 libxrender-dev
# For: libGL.so.1
RUN apt-get install -y libgl1-mesa-glx
RUN apt-get install -y libglib2.0-0
RUN apt-get install -y openssl libssl-dev libbz2-dev
RUN apt-get install -y python3 python3-pip
RUN pip3 install --upgrade pip
RUN apt-get install -y openjdk-8-jdk
RUN apt-get install -y libvips
#RUN apt-get install -y openslide-tools

COPY requirements.txt /image-storage/requirements.txt
WORKDIR /image-storage
RUN pip3 install -r requirements.txt

COPY . /image-storage

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONPATH=/image-storage

ENTRYPOINT ["python3", "/image-storage/convert.py"]
