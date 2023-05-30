FROM python:3.10-alpine

EXPOSE 5000
WORKDIR /server

RUN apk add build-base openldap-dev python3-dev

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /server/init.sh
CMD ["/bin/sh", "/server/init.sh"]