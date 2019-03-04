# Build on an old Arch version on purpose, to maximize compatibility:
FROM fmanbuildsystem/archlinux:2018.04.01

ARG requirements

RUN echo 'Server=https://archive.archlinux.org/repos/2018/04/01/$repo/os/$arch' > /etc/pacman.d/mirrorlist && \
    pacman -Syy

# Python 3.6:
RUN pacman -S --noconfirm python

# fpm:
RUN pacman -S --noconfirm ruby ruby-rdoc && \
    export PATH=$PATH:$(ruby -e "puts Gem.user_dir")/bin && \
    gem update && \
    gem install --no-ri --no-rdoc fpm

WORKDIR /root/${app_name}

# Set up virtual environment:
ADD *.txt /tmp/requirements/
RUN python -m venv venv && \
    venv/bin/python -m pip install -r "/tmp/requirements/${requirements}"
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