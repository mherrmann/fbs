# Build on an old Arch version on purpose, to maximize compatibility:
FROM fmanbuildsystem/archlinux:2018.04.01

# Alternatively Build on an latest Arch version on purpose, to maximize compatibility as its rolling release:
# FROM library/archlinux:latest

ARG requirements

WORKDIR /root/${app_name}

ADD *.txt /tmp/requirements/

RUN echo 'Server=https://mirror.rackspace.com/archlinux/$repo/os/$arch' > /etc/pacman.d/mirrorlist && \
    pacman -Syy

# Set of all dependencies needed for pyenv and building a PyQt5 app with PyInstaller to work on
RUN pacman -S --noconfirm base-devel openssl zlib xz git

# Install base system libraries additionally specified by user.
ENV USER_OS_DEPENDS /tmp/requirements/base_os_dependencies.txt
RUN if [ -f "${USER_OS_DEPENDS}" ] && [ -s "${USER_OS_DEPENDS}" ] ; then  \
    pacman -S --noconfirm $(cat "${USER_OS_DEPENDS}"); fi ||True


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
RUN pacman -S --noconfirm ruby ruby-rdoc && \
    export PATH=$PATH:$(ruby -e "puts Gem.user_dir")/bin && \
    gem update && \
    gem install --no-document fpm||gem install --no-document fpm

# Welcome message, displayed by ~/.bashrc:
ADD motd /etc/motd

ADD .bashrc /root/.bashrc

# Import GPG key for code signing the installer:
ADD private-key.gpg public-key.gpg /tmp/
RUN gpg -q --batch --yes --passphrase ${gpg_pass} --import /tmp/private-key.gpg /tmp/public-key.gpg && \
    rm /tmp/private-key.gpg /tmp/public-key.gpg

ADD gpg-agent.conf /root/.gnupg/gpg-agent.conf
RUN gpgconf --kill gpg-agent
