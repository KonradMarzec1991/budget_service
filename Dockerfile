FROM python:3.8

COPY ./requirements.txt /code/
COPY entrypoint.sh /code/

RUN apt-get update
RUN pip install -r /code/requirements.txt

COPY ./ /code/
WORKDIR /code

RUN chmod a+x /code/entrypoint.sh
CMD /code/entrypoint.sh
