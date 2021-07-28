FROM fmanbuildsystem/archlinux:2018.04.01

# Alternatively Build on an latest Arch version on purpose, to maximize compatibility as its rolling release:
# FROM library/archlinux:latest

ARG requirements

ARG python_version=3.6.12
ARG python_build_deps="base-devel openssl zlib xz git"

RUN echo 'Server=https://mirror.rackspace.com/archlinux/$repo/os/$arch' > /etc/pacman.d/mirrorlist && \
    pacman -Syy

# Install pyenv:
RUN pacman -S --noconfirm curl git
ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
RUN curl https://pyenv.run | bash
RUN pyenv update

# https://python-docs.readthedocs.io/en/latest/writing/gotchas.html
ENV PYTHONDONTWRITEBYTECODE true

# Install Python:
RUN echo $python_build_deps | xargs pacman -S --noconfirm
RUN CONFIGURE_OPTS=--enable-shared pyenv install $python_version && \
    pyenv global $python_version && \
    pyenv rehash


# fpm: Set fallbacks for --no-document when later ruby is used which fails due to --no-ri --no-rdoc no longer existing
RUN pacman -S --noconfirm ruby ruby-rdoc && \
    export PATH=$PATH:$(ruby -e "puts Gem.user_dir")/bin && \
    gem update && \
    gem install --no-document fpm||gem install --no-document fpm

WORKDIR /root/${app_name}

# Set up virtual environment, upgrade pip, and install requirements:
ADD *.txt /tmp/requirements/
RUN pip install --upgrade pip && \
    pip install -r "/tmp/requirements/${requirements}"
RUN rm -rf /tmp/requirements/

# Welcome message, displayed by ~/.bashrc:
ADD motd /etc/motd
