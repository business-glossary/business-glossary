FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7

RUN apk --no-cache --update add bash nano

RUN apk add --no-cache libressl-dev musl-dev libffi-dev gcc && \
    apk add --no-cache mariadb-dev 

ENV STATIC_URL /static
ENV STATIC_PATH /glossary/business-glossary/app/static/
ENV UWSGI_INI /glossary/business-glossary/uwsgi.ini

RUN mkdir /glossary && \
    mkdir /glossary/bg_files && \
    mkdir /glossary/bg_interface && \
    mkdir /glossary/bg_pages

COPY . /glossary/business-glossary

COPY ./nginx.conf /etc/nginx/conf.d

WORKDIR /glossary/business-glossary

RUN pip install -r requirements.txt
