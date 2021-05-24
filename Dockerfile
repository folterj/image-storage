FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y upgrade && apt-get clean all

#RUN apt install cuda-10-1
#RUN apt install libcudnn7

RUN apt-get install -y libsm6 libxext6 libxrender-dev
RUN apt-get install -y libglib2.0-0
RUN apt-get install -y python3 python3-pip
RUN pip3 install --upgrade pip
#RUN apt-get install -y openslide-tools
#RUN apt-get install -y python-tifffile

COPY . /image-storage
WORKDIR /image-storage
RUN pip3 install -r requirements.txt

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONPATH=/image-storage

ENTRYPOINT ["python3", "/image-storage/convert.py"]
