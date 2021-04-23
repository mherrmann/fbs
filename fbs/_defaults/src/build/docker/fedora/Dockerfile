# Build on an old Fedora version on purpose, to maximize compatibility:
FROM fmanbuildsystem/fedora:25

ARG requirements

WORKDIR /root/${app_name}

ADD *.txt /tmp/requirements/

# Absolute minimum requirements for building a PyQt5 app with PyInstaller:
RUN dnf -y update && \
        dnf install -y libstdc++ freetype binutils git findutils && \
        dnf clean all

# Install base system libraries additionally specified by user.
ENV USER_OS_DEPENDS /tmp/requirements/os_dependencies_${requirements}
RUN if [ -f "${USER_OS_DEPENDS}" ] && [ -s "${USER_OS_DEPENDS}" ] ; then dnf upgrade -y && \
    dnf install -y $(cat "${USER_OS_DEPENDS}") && \
    dnf clean all; fi ||True


# Pyenv minimum requirements : https://github.com/pyenv/pyenv/wiki#suggested-build-environment
RUN dnf install -y make gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel \
    libffi-devel xz

# Set-up necessary Env vars for PyEnv
ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

# Reference: https://github.com/pyenv/pyenv/wiki#how-to-build-cpython-with---enable-shared
ENV PYTHON_CONFIGURE_OPTS="--enable-shared"

# Set default python version to global file ".python-version.txt" or distro specific if .python-version_fedora.txt
ENV DEFAULT_PYTHON_VERSION 3.6.12
ENV PYTHON_VERSION_FILE /tmp/requirements/.python-version.txt
ENV PYTHON_VERSION_FILE_DISTRO /tmp/requirements/.python-version_${requirements}
RUN if  [ -f "${PYTHON_VERSION_FILE_DISTRO}" ] && [ -s "${PYTHON_VERSION_FILE_DISTRO}" ] ; then \
    echo "DISTRO PYTHON VERSION File found: ${PYTHON_VERSION_FILE_DISTRO}"; \
    cp -f "${PYTHON_VERSION_FILE_DISTRO}" "${PYTHON_VERSION_FILE}"; \
    elif  [ -f "${PYTHON_VERSION_FILE}" ] && [ -s "${PYTHON_VERSION_FILE}" ] ; then \
    echo "Existing PYTHON VERSION File found: ${PYTHON_VERSION_FILE_DISTRO}" ; else \
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
RUN dnf install -y ruby-devel gcc make rpm-build libffi-devel && \
    gem install --no-ri --no-rdoc fpm||gem install --no-document fpm

# Upgrade pip and install Python pip packages needed:
RUN pip install --upgrade pip && pip install -r "/tmp/requirements/${requirements}"
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
