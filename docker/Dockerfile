FROM artifactory.infra.corp.arista.io/bsn-docker-internal/ubuntu/focal:latest

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y --no-install-recommends \
        build-essential \
        curl \
        git \
        gnupg \
        maven \
        openjdk-11-jdk \
        openssh-client \
        python3 \
        python3-arrow \
        python3-pip \
        python3-requests \
        python3-setuptools \
        rsync

RUN curl --fail -L https://jenkins-dl.eng.bigswitch.com/github-known-hosts/master/builds/lastSuccessfulBuild/archive/ssh_known_hosts \
    >/etc/ssh/ssh_known_hosts

RUN pip3 install pytest

RUN useradd -m -d /loxi -c 'loxi build user' -u 1000 -s /bin/bash loxi
COPY run-as-loxi /
ENTRYPOINT [ "/run-as-loxi" ]
