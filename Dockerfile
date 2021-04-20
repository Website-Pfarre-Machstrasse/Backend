FROM python:3.9-slim-buster
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y gcc musl-dev libpq-dev && \
    apt-get clean
ADD requirements.txt /
RUN pip3 install -r requirements.txt --no-cache-dir
RUN apt-get clean
ADD ./server /server
ADD gunicorn_config.py /
ADD start.sh /
EXPOSE 5000
RUN chmod +x ./start.sh
ENTRYPOINT ["sh", "start.sh"]
