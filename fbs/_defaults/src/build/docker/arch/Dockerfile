# Build on :latest because Arch is a rolling release distribution:
FROM archlinux:latest

ARG requirements

# Python 3.7 is the earliest version that won't crash in Arch as of July 2021.
ARG python_version=3.7.11
# List from https://github.com/pyenv/pyenv/wiki#suggested-build-environment:
ARG python_build_deps="base-devel openssl zlib xz git"

RUN echo 'Server=https://mirror.rackspace.com/archlinux/$repo/os/$arch' > /etc/pacman.d/mirrorlist && \
    pacman -Syy

# Install pyenv:
RUN pacman -S --noconfirm curl git
ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
RUN curl https://pyenv.run | bash
RUN pyenv update

# Install Python:
RUN echo $python_build_deps | xargs pacman -S --noconfirm
RUN CONFIGURE_OPTS=--enable-shared pyenv install $python_version && \
    pyenv global $python_version && \
    pyenv rehash

# Install fpm:
RUN pacman -S --noconfirm ruby ruby-rdoc && \
    export PATH=$PATH:$(ruby -e "puts Gem.user_dir")/bin && \
    gem update && \
    gem install --no-document fpm

WORKDIR /root/${app_name}

# Install Python dependencies:
ADD *.txt /tmp/requirements/
RUN pip install --upgrade pip && \
    pip install -r "/tmp/requirements/${requirements}"
RUN rm -rf /tmp/requirements/

# Welcome message, displayed by ~/.bashrc:
ADD motd /etc/motd

ADD .bashrc /root/.bashrc

# Import GPG key for code signing the installer:
ADD private-key.gpg public-key.gpg /tmp/
RUN gpg -q --batch --yes --passphrase ${gpg_pass} --import /tmp/private-key.gpg /tmp/public-key.gpg && \
    rm /tmp/private-key.gpg /tmp/public-key.gpg

ADD gpg-agent.conf /root/.gnupg/gpg-agent.conf
RUN gpgconf --kill gpg-agent