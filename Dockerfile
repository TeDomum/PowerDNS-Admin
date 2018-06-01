FROM python:3-alpine

RUN apk add --no-cache libldap libffi xmlsec libxslt libxml2 musl libsasl

COPY requirements.txt /requirements.txt
RUN apk add --no-cache --virtual build-dep \
      gcc musl-dev libxml2-dev libxslt-dev xmlsec-dev libffi-dev openldap-dev \
      libgsasl-dev mariadb-dev \
 && pip install -r /requirements.txt \
 && apk del build-dep

COPY . /app
WORKDIR /app

RUN cp configs/docker.py config.py

VOLUME /data

CMD /app/run_prod.sh
