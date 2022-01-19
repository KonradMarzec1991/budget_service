FROM python:3.8

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN apt-get update
RUN pip install -r requirements.txt

COPY ./server /app

WORKDIR /app

COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]
