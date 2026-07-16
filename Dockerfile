FROM python:3.12-bookworm

WORKDIR /server

RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential \
python3-dev \
python3-pip \
libpcre2-dev \
libsasl2-dev \
libldap2-dev \
iputils-ping \
&& \
apt-get clean \
&& \
rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /server/docker_init.sh
RUN chmod +x /server/start.sh
