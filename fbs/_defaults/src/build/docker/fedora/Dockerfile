# Build on an old Fedora version on purpose, to maximize compatibility:
FROM fmanbuildsystem/fedora:25

ARG requirements

ARG python_version=3.6.12
ARG python_build_deps="libstdc++ freetype binutils git findutils"

# Updates:
RUN dnf -y update && dnf clean all

# Install pyenv:
# Pyenv minimum requirements : https://github.com/pyenv/pyenv/wiki#suggested-build-environment
RUN dnf install -y curl git make gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel \
    libffi-devel xz
ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
RUN curl https://pyenv.run | bash
RUN pyenv update

# https://python-docs.readthedocs.io/en/latest/writing/gotchas.html
ENV PYTHONDONTWRITEBYTECODE true

# Install Python:
RUN echo $python_build_deps | xargs dnf install -y
RUN CONFIGURE_OPTS=--enable-shared pyenv install $python_version && \
    pyenv global $python_version && \
    pyenv rehash


# fpm: Set fallbacks for --no-document when later ruby is used which fails due to --no-ri --no-rdoc no longer existing
RUN dnf install -y ruby-devel gcc make rpm-build libffi-devel && \
    gem install --no-ri --no-rdoc fpm||gem install --no-document fpm

WORKDIR /root/${app_name}

# Set up virtual environment, upgrade pip, and install requirements:
ADD *.txt /tmp/requirements/
RUN pip install --upgrade pip && \
    pip install -r "/tmp/requirements/${requirements}"
RUN rm -rf /tmp/requirements/

# Welcome message, displayed by ~/.bashrc:
ADD motd /etc/motd

ADD .bashrc /root/.bashrc

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
