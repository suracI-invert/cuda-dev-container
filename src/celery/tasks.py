import os
import json
from dotenv import load_dotenv

load_dotenv('./.env', override=True)

from time import sleep

from sseclient import SSEClient
import requests

from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown

from database.connect import VectorDB, MongoDB

from requests import Session

from database.crud import find_doc, search

app = Celery('tasks', backend='redis://redis', broker='amqp://guest@rabbitmq')

app.conf.broker_connection_retry_on_startup = True

vector_db = None
mongo_db = None

@worker_process_init.connect
def init_worker(**kwargs):
    global vector_db
    global mongo_db

    vector_db = VectorDB()
    mongo_db = MongoDB()

@worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    global vector_db
    global mongo_db

    if vector_db:
        vector_db.close()
    if mongo_db:
        mongo_db.close()

@app.task
def ping_vector_db():
    return repr(vector_db)

@app.task
def ping_mongo_db():
    return repr(mongo_db)

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
        ret = s.post('http://bentoml:3000/emb', headers=headers, json={'text': text})
        if ret.status_code != 200:
            raise Exception(f'API return {ret.status_code}')
        data = ret.json()
    return data['embedding']

@app.task
def call_rerank_api(docs, text):
    headers = {
        'Accept': 'text/plain',
        'Content-Type': 'application/json'
    }
    with Session() as s:
        ret = s.post('http://bentoml:3000/rerank', headers=headers, json={'text': text, 'docs': docs})
        if ret.status_code != 200:
            raise Exception(f'API return {ret.status_code}')
        data = ret.json()
    return data['scores']

@app.task
def call_mongodb(doc_ids):
    client = mongo_db.client
    docs = find_doc(client, doc_ids)
    return [d['abstract'] for d in docs]

@app.task
def call_vectordb(embedding):
    client = vector_db.client
    res = search(client, embedding)
    return [r['id'] for r in res]

@app.task
def call_gpt(context, text):
    url = 'https://s.aginnov.com/openai/fsse/chat/completions'
    headers = {
                'Connection': 'keep-alive',
                'Accept': 'text/event-stream',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Authorization': f'Bearer {os.environ['API_TOKEN']}'
            }
    
    def extract_context(context):
        context_str = '\n\n'.join([f"Retrieval score: {c['score']}\n\n{c['content']}" for c in context[:2]])
        return context_str
    

    context_str = extract_context(context)

    system_template = """You are an expert Q&A system that is trusted around the world.
Always answer the query using the provided context information.
Some rules to follow:
1. Never directly reference the given context in your answer.
2. Avoid statements like 'Based on the context, ...' or 'The context information ...' or anything along those lines."""

    user_template = f"""Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {text}
Answer: """

    msg = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_template},
            {"role": "user", "content": user_template}
        ]
    }

    response = []

    attempt = 2
    while attempt > 0:
        res = requests.post(url, json=msg, headers=headers, stream=True)
        if res.status_code != 200:
            sleep(1)
            attempt -= 1
            continue
        else:
            client = SSEClient(res)
            for event in client.events():
                if event.data != '[DONE]':
                    data = json.loads(event.data)
                    if 'content' in data['choices'][0]['delta']:
                        response.append(data['choices'][0]['delta']['content'])
            break
    if attempt == 0 and len(response) == 0:
        raise Exception('Request to GPT API failed')
    response = ''.join(response)
    return response