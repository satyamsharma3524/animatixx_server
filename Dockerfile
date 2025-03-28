FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY . /code/
COPY --chmod=777 ./scripts /scripts
COPY .env /code/.env
RUN export MYSQL_DATABASE=animatrixx

RUN apt-get update && apt-get install -y default-mysql-client redis\
    && pip install --no-cache-dir --default-timeout=300 --upgrade pip \
    && pip install --no-cache-dir --default-timeout=300 -r requirements.txt \
    && apt-get clean

RUN mkdir -p /vol/web/media/ && mkdir -p /var/log/django
RUN chmod 777 ./scripts/entrypoint.sh
EXPOSE 8000

CMD ["./scripts/entrypoint.sh"]
