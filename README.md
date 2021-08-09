# Feed Manager
This project is a RSS scraper and feed manager backend service with `python 3.9`. The service is for saving RSS feeds to a database and users can read and bookmark them.
This is developed using FastAPI and Nameko for microservice design with isolated databases for each service. I also use sqlite database for development and use pytest for nameko services.
The project services are:

1. gateway service:
    This service is developed using FastAPI for routing and authenticating with jwt tokens.
   
2. users service:
   This service is developed using Nameko for registering user and getting user information and also is for login process.
   
3. feeds service:
    This service is developed using Nameko for managing feeds and feeds items parsed for each Feed. The user can have multiple feeds, add bookmark/ favourite to feed items and comment on a feed item.
   
4. Celery:
    The feed manager updates the feeds asynchronously with static time intervals that can be tune in config file. Celery is scheduled for this task.

5. RabbitMQ:
    RabbitMQ has been used as a message broker between Nameko services and also for Celery worker. 
 

## Run via docker compose

Just run following command: (supposed to docker and docker compose have been installed before)
```shell script
docker-compose up --build
```
Project will run on http://localhost:8080

* You can see OpenApi documentation on http://localhost:8080/swagger
