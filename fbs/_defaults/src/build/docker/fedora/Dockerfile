# Build on an old Fedora version on purpose, to maximize compatibility:
FROM fmanbuildsystem/fedora:25

ARG requirements

# Python 3.6:
RUN dnf install -y python36

# Absolute minimum requirements for building a PyQt5 app with PyInstaller:
RUN dnf install -y libstdc++ freetype binutils

# fpm:
RUN dnf install -y ruby-devel gcc make rpm-build libffi-devel && \
    gem install --no-ri --no-rdoc fpm

WORKDIR /root/${app_name}

# Set up virtual environment:
ADD *.txt /tmp/requirements/
RUN python3.6 -m venv venv && \
    venv/bin/python -m pip install -r "/tmp/requirements/${requirements}"
RUN rm -rf /tmp/requirements/

# Welcome message, displayed by ~/.bashrc:
ADD motd /etc/motd

ADD .bashrc /root

ADD gpg-agent.conf /root/.gnupg/gpg-agent.conf
RUN chmod -R 600 /root/.gnupg
ADD private-key.gpg public-key.gpg /tmp/
RUN dnf install -y gpg rpm-sign && \
    gpg -q --batch --yes --passphrase ${gpg_pass} --import /tmp/private-key.gpg /tmp/public-key.gpg && \
    rpm --import /tmp/public-key.gpg && \
    rm /tmp/private-key.gpg /tmp/public-key.gpg

ADD .rpmmacros /root

RUN dnf install -y createrepo_c

ENTRYPOINT ["/bin/bash"]