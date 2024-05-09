FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY . /code/

RUN apt-get update && apt-get install -y default-mysql-client redis\
    && pip install --no-cache-dir --default-timeout=300 --upgrade pip \
    && pip install --no-cache-dir --default-timeout=300 -r requirements.txt \
    && apt-get clean

EXPOSE 8000

ENTRYPOINT ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
