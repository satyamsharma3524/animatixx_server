FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY . /code/

RUN apt-get update \
    && pip install --no-cache-dir --default-timeout=300 --upgrade pip \
    && pip install --no-cache-dir --default-timeout=300 -r requirements.txt \
    && apt-get clean

ENTRYPOINT ["python3", "manage.py", "runserver"]