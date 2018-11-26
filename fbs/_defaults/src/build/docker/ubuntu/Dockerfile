# Build on an old Ubuntu version on purpose, to maximize compatibility:
FROM ubuntu:14.04

RUN apt-get update && \
    apt-get upgrade -y

# Python 3.6:
RUN DEBIAN_FRONTEND=noninteractive apt-get install software-properties-common -y && \
    add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update && \
    apt-get install python3.6 python3.6-dev python3.6-venv -y

# Add missing file libGL.so.1 for PyQt5.QtGui:
RUN apt-get install libgl1-mesa-glx -y

# This installs libgtk-3.so.0, which PyInstaller places in our frozen directory.
# Without this .so file, running the frozen app produces a segmentation fault.
RUN apt-get install libgtk-3-0 -y

# fpm:
RUN apt-get install ruby ruby-dev build-essential -y && \
    gem install --no-ri --no-rdoc fpm

ADD .bashrc /root/.bashrc

WORKDIR /root/${app_name}

ADD base.txt linux.txt ubuntu.txt /tmp/requirements/

# Set up virtual environment:
RUN python3.6 -m venv venv && \
    venv/bin/python -m pip install -r /tmp/requirements/ubuntu.txt && \
    rm -rf /tmp/requirements/