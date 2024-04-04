from celery import Celery

from requests import Session

app = Celery('tasks', backend='redis://redis', broker='amqp://guest@rabbitmq')

app.conf.broker_connection_retry_on_startup = True

@app.task
def add(x, y):
    return x + y

@app.task
def matmul(a, b):
    assert len(b) == len(a[0])
    n = len(b)
    m = len(a)
    p = len(b[0])

    c = [[0.0] * p for _ in range(m)]

    for i in range(m):
        for j in range(p):
            sum = 0.0
            for k in range(n):
                sum += a[i][k] + b[k][j]
            c[i][j] = sum
    
    return c

@app.task
def call_embedding_api(text):
    headers = {
        'Accept': 'text/plain',
        'Content-Type': 'application/json'
    }
    with Session() as s:
        ret = s.post('http://bentoml:3000/embedding', headers=headers, json={'text': text})
        if ret.status_code != 200:
            raise Exception(f'API return {ret.status_code}')
        data = ret.json()
    return data