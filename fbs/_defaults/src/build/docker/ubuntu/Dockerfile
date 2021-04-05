# Build on an old Ubuntu version on purpose, to maximize compatibility:
FROM fmanbuildsystem/ubuntu:16.04


ARG requirements

WORKDIR /root/${app_name}

ADD *.txt /tmp/requirements/

# Set of all dependencies needed for pyenv and building a PyQt5 app with PyInstaller to work on Ubuntu
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get upgrade -y \
        && apt-get install -y --no-install-recommends software-properties-common ca-certificates make build-essential \
        libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev \
        libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev mecab-ipadic-utf8 git

# Install base system libraries additionally specified by user.
ENV USER_OS_DEPENDS /tmp/requirements/base_os_dependencies.txt
RUN if [ -f "${USER_OS_DEPENDS}" ] && [ -s "${USER_OS_DEPENDS}" ] ; then apt-get update && \
    apt-get install -y $(cat "${USER_OS_DEPENDS}") && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /etc/dpkg/dpkg.cfg.d/02apt-speedup; fi ||True

# Add missing file libGL.so.1 for PyQt5.QtGui:
RUN apt-get install libgl1-mesa-glx -y

# Set-up necessary Env vars for PyEnv
ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

# Reference: https://github.com/pyenv/pyenv/wiki#how-to-build-cpython-with---enable-shared
ENV PYTHON_CONFIGURE_OPTS="--enable-shared"

# Set default python version to file if provided and trim any whitepace.
ENV DEFAULT_PYTHON_VERSION 3.6.12
ENV PYTHON_VERSION_FILE /tmp/requirements/.python-version.txt
RUN if [ -f "${PYTHON_VERSION_FILE}" ] && [ -s "${PYTHON_VERSION_FILE}" ] ; then \
    echo "Existing PYTHON VERSION File found: ${PYTHON_VERSION_FILE}"; else \
    echo "${DEFAULT_PYTHON_VERSION}" > "${PYTHON_VERSION_FILE}" ; fi

# Install pyenv
RUN set -ex \
    && PYTHON_VERSION=$(cat /tmp/requirements/.python-version.txt | sed -e 's/^[[:space:]]*//') && cd "${HOME}" \
    && curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash \
    && pyenv update \
    && pyenv install "${PYTHON_VERSION}" \
    && pyenv global "${PYTHON_VERSION}" \
    && pyenv rehash


# https://python-docs.readthedocs.io/en/latest/writing/gotchas.html
ENV PYTHONDONTWRITEBYTECODE true

# fpm: Set fallbacks for --no-document when later ruby is used which fails due to --no-ri --no-rdoc no longer existing
RUN apt-get install ruby ruby-dev build-essential -y && \
    gem install --no-ri --no-rdoc fpm||gem install --no-document fpm

# Upgrade pip and install Python pip packages needed:
RUN pip install --upgrade pip && pip install -r "/tmp/requirements/${requirements}"
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
