FROM debian:9.6

ARG name
ARG email
ARG passphrase
ARG keylength=1024

RUN apt-get update

ADD gpg-agent.conf /root/.gnupg/gpg-agent.conf
RUN chmod -R 600 /root/.gnupg/
RUN apt-get install gnupg2 pinentry-tty -y

WORKDIR /root

ADD genkey.sh /root/genkey.sh
RUN chmod +x genkey.sh