FROM python:3.9

RUN apt-get update && apt-get -y install netcat && apt-get clean

WORKDIR /app

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

COPY ./.env.sample .env

RUN chmod +x ./run*.sh

