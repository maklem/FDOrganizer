FROM nginx:1.23.4-alpine

WORKDIR /

# RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx

COPY /ssl/ca.crt /etc/ssl/
COPY /ssl/ca.key /etc/ssl/

RUN chown -R root:root /etc/ssl/ca.crt
RUN chown -R root:root /etc/ssl/ca.key
RUN chmod -R 644 /etc/ssl/ca.crt
RUN chmod -R 644 /etc/ssl/ca.key