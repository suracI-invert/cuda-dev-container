### BENTOML Serving

## Introduction
Retrieval Augmented Generation system. Using bentoml as serving backend, celery + redis(backend) + rabbitmq(broker) tasks distributing scheme, FastAPI for API endpoints, gradio for frontend

## Usage
Create .env file as layout by .env.sample

Ship with docker compose
```
docker compose up
```

Access at 
```
localhost:7000
```