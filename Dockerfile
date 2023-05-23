FROM python:3.10-alpine

WORKDIR /server

RUN apk add build-base openldap-dev python3-dev linux-headers pcre-dev openssl-dev

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /server/init_db.sh
RUN chmod +x /server/start.sh