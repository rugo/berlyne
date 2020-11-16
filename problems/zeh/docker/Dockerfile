FROM debian:buster

RUN apt update && apt-get install -y xinetd && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/

# challenge files
RUN useradd -m -s /bin/bash ctf
COPY haupt .
RUN chmod 711 haupt
COPY haupt_svc /etc/xinetd.d/

CMD xinetd -dontfork
