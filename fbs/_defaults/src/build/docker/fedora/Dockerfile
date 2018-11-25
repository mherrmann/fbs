# Build on an old Fedora version on purpose, to maximize compatibility:
FROM fedora:25

# Python 3.6:
RUN dnf install -y python36

# Absolute minimum requirements for building a PyQt5 app with PyInstaller:
RUN dnf install -y libstdc++ freetype binutils

# fpm:
RUN dnf install -y ruby-devel gcc make rpm-build libffi-devel && \
    gem install --no-ri --no-rdoc fpm

ADD .bashrc /root

WORKDIR /root/${app_name}

ADD base.txt linux.txt ubuntu.txt fedora.txt /tmp/requirements/

# Set up virtual environment:
RUN python3.6 -m venv venv && \
    venv/bin/python -m pip install -r /tmp/requirements/fedora.txt && \
    rm -rf /tmp/requirements/

ENTRYPOINT ["/bin/bash"]