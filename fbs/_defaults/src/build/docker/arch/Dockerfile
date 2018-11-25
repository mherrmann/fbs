# Build on an old Arch version on purpose, to maximize compatibility:
FROM base/devel:2018.04.01

RUN echo 'Server=https://archive.archlinux.org/repos/2018/04/01/$repo/os/$arch' > /etc/pacman.d/mirrorlist && \
    pacman -Syy

# Python 3.6:
RUN pacman -S --noconfirm python

# fpm:
RUN pacman -S --noconfirm ruby ruby-rdoc && \
    export PATH=$PATH:$(ruby -e "puts Gem.user_dir")/bin && \
    gem update && \
    gem install --no-ri --no-rdoc fpm

ADD .bashrc /root/.bashrc

WORKDIR /root/${app_name}

ADD base.txt linux.txt arch.txt /tmp/requirements/

# Set up virtual environment:
RUN python -m venv venv && \
    venv/bin/python -m pip install -r /tmp/requirements/arch.txt && \
    rm -rf /tmp/requirements/