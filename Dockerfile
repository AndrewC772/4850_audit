FROM ubuntu

WORKDIR /app

RUN apt-get update --fix-missing

RUN apt-get install -y python3

RUN apt -y install python3-pip

COPY . .

RUN apt install -y libmysqlclient-dev

RUN pip install -r requirements.txt 

EXPOSE 8110:8110

CMD [ "python3", "app.py" ]