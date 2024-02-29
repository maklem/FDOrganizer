FROM python:3.10-slim-bookworm

WORKDIR /server

RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential \
libsasl2-dev \
libldap2-dev \
libssl-dev \
iputils-ping \
&& \
apt-get clean \
&& \
rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /server/init_db.sh
RUN chmod +x /server/start.sh
RUN chmod +x /server/init_organisation.sh