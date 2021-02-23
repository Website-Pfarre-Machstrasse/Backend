FROM python:3.8-slim
ADD requirements.txt /
RUN pip3 install -r requirements.txt
ADD ./server /server
ADD gunicorn_config.py start.sh /
EXPOSE 5000
RUN chmod +x ./start.sh
ENTRYPOINT ["sh", "start.sh"]
