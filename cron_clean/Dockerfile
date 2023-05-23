FROM python:3.10-alpine

WORKDIR /

COPY reset_dbs.sh /usr/local/
COPY create_database.py /usr/local/
COPY reset_database.py /usr/local/
RUN chmod -R +x /usr/local/reset_dbs.sh

# RUN apk add py3-setuptools
# RUN pip install --upgrade setuptools
RUN pip install requests python-dotenv

COPY cronjobs /etc/crontabs/root

CMD ["crond", "-f", "-d", "8"]