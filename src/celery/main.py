from asyncio import sleep
import json

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from database.connect import MongoDB, VectorDB
from database.crud import find_doc, search

from schemas.query import QueryRequest

from tasks import add, matmul, call_embedding_api, call_rerank_api, ping_mongo_db, ping_vector_db, call_mongodb, call_vectordb

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def hello():
    return 'BENTOML IS WEIRD'

# @app.post('/query')

@app.get('/test')
async def test():
    async def generator():
        for i in range(10):
            yield f'event: Test\ndata: {i}\n\n'
            await sleep(1)
    return StreamingResponse(generator(), 200, media_type='text/event-stream')

@app.post('/query')
async def query(q: QueryRequest):
    async def generator():
        chain = {
            'create_embedding': call_embedding_api.s(), 
            'search_similar_documents':call_vectordb.s(), 
            'query_similar_documents':call_mongodb.s(), 
            'rerank_similar_documents': call_rerank_api.s(q.text)}
        res = q.text
        for e, t in chain.items():
            res = t.delay(res).get()
            ret = {"stage": e, "content": res}
            yield f'{json.dumps(ret)}\n'
        yield f'{json.dumps({"stage": "DONE", "content": ""})}\n'
    return StreamingResponse(generator(), 200)
    

# emb = call_embedding_api.delay('Hello, what exactly is a string?').get()
# print(len(emb))
# # with VectorDB() as client:
# #     doc_ids = search(client, emb['embedding'])
# doc_ids = call_vectordb.delay(emb['embedding']).get()
# print(doc_ids)
# # with MongoDB() as client:
# #     docs = find_doc(client, [d['id'] for d in doc_ids])
# docs = call_mongodb.delay(doc_ids).get()
# print(docs)
# ctx = call_rerank_api.delay('Hello, what exactly is a string?', docs).get()
# print(ctx)

# res = (call_embedding_api.s() | call_vectordb.s() | call_mongodb.s() | call_rerank_api.s())

# res.delay(text='Hello, what exactly is a string?')
# print(res.get(text='Hello, what exactly is a string?'))

#https://stackoverflow.com/questions/9034091/how-to-check-task-status-in-celery