FROM python:3.8-slim
RUN mkdir /server
WORKDIR /server
ADD requirements.txt /server
RUN pip3 install -r requirements.txt
ADD ./server /server
EXPOSE 5000
RUN chmod +x ./start.sh
ENTRYPOINT ["sh", "start.sh"]
