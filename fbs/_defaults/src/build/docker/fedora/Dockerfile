# Build on an old Fedora version on purpose, to maximize compatibility:
FROM fmanbuildsystem/fedora:25

ARG requirements

ARG python_version=3.6.12
# List from https://github.com/pyenv/pyenv/wiki#suggested-build-environment:
ARG python_build_deps="make gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel"

RUN dnf -y update && dnf clean all

# Install pyenv:
RUN dnf install -y curl git
ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
RUN curl https://pyenv.run | bash
RUN pyenv update

# Install Python:
# findutils contains xargs, which is needed for the next step:
RUN dnf install -y findutils
RUN echo $python_build_deps | xargs dnf install -y
RUN CONFIGURE_OPTS=--enable-shared pyenv install $python_version && \
    pyenv global $python_version && \
    pyenv rehash

# Install fpm:
RUN dnf install -y ruby-devel gcc make rpm-build libffi-devel && \
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

ADD gpg-agent.conf /root/.gnupg/gpg-agent.conf
# Avoid GPG warning "unsafe permissions":
RUN chmod -R 600 /root/.gnupg
ADD private-key.gpg public-key.gpg /tmp/
RUN dnf install -y gpg rpm-sign && \
    gpg -q --batch --yes --passphrase ${gpg_pass} --import /tmp/private-key.gpg /tmp/public-key.gpg && \
    rpm --import /tmp/public-key.gpg && \
    rm /tmp/private-key.gpg /tmp/public-key.gpg

ADD .rpmmacros /root

RUN dnf install -y createrepo_c

ENTRYPOINT ["/bin/bash"]