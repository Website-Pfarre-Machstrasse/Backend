FROM python:3.9-slim-buster
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y gcc musl-dev libpq-dev && \
    apt-get clean
ADD requirements.txt /
ADD ./server /server
ADD setup.py /
ADD setup.cfg /
ADD README.md /
ADD backup.sh /
ADD restore.sh /
RUN pip3 install -r requirements.txt --no-cache-dir
RUN apt-get clean
ADD gunicorn_config.py /
ADD start.sh /
EXPOSE 5000
RUN chmod +x ./start.sh
ENTRYPOINT ["sh", "start.sh"]
