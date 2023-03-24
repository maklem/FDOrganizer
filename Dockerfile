FROM python:3.10-alpine

EXPOSE 5000
WORKDIR /server

RUN apk add build-base openldap-dev python3-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["./init.sh"]