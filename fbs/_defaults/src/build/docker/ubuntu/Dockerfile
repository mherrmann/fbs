# Build on an old Ubuntu version on purpose, to maximize compatibility:
FROM ubuntu:16.04

ARG requirements

ARG python_version=3.6.12
# List from https://github.com/pyenv/pyenv/wiki#suggested-build-environment:
ARG python_build_deps="make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev"

RUN apt-get update && \
    apt-get upgrade -y

# Install pyenv:
RUN apt-get install -y curl git
ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
RUN curl https://pyenv.run | bash
RUN pyenv update

# Install Python:
RUN echo $python_build_deps | xargs apt-get install -y --no-install-recommends
RUN CONFIGURE_OPTS=--enable-shared pyenv install $python_version && \
    pyenv global $python_version && \
    pyenv rehash

# Add missing file libGL.so.1 for PyQt5.QtGui:
RUN apt-get install libgl1-mesa-glx -y

# fpm:
RUN apt-get install ruby ruby-dev build-essential -y && \
    gem install --no-document fpm

WORKDIR /root/${app_name}

# Install Python requirements:
ADD *.txt /tmp/requirements/
RUN pip install --upgrade pip && \
    pip install -r "/tmp/requirements/${requirements}"
RUN rm -rf /tmp/requirements/

# Welcome message, displayed by ~/.bashrc:
ADD motd /etc/motd

ADD .bashrc /root/.bashrc

# Requirements for our use of reprepro:
ADD gpg-agent.conf gpg.conf /root/.gnupg/
# Avoid GPG warning "unsafe permissions":
RUN chmod -R 600 /root/.gnupg/
RUN apt-get install reprepro gnupg-agent gnupg2 -y
ADD private-key.gpg public-key.gpg /tmp/
RUN gpg -q --batch --yes --passphrase ${gpg_pass} --import /tmp/private-key.gpg /tmp/public-key.gpg && \
    rm /tmp/private-key.gpg /tmp/public-key.gpg