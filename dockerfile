FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    iproute2 \
    tcpdump \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip3 install pandas matplotlib

CMD ["/bin/bash"]

