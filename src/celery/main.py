from fastapi import FastAPI
from celery import chain

from database.connect import MongoDB, VectorDB
from database.crud import find_doc, search

from tasks import add, matmul, call_embedding_api, call_rerank_api, ping_mongo_db, ping_vector_db, call_mongodb, call_vectordb

# app = FastAPI()

# @app.get('/')
# def hello():
#     return 'BENTOML IS WEIRD'

# @app.post('/bentoml/emb')
# def bentoml_emb(text: str):
#     pass
    

emb = call_embedding_api.delay('Hello, what exactly is a string?').get()
print(len(emb))
# with VectorDB() as client:
#     doc_ids = search(client, emb['embedding'])
doc_ids = call_vectordb.delay(emb['embedding']).get()
print(doc_ids)
# with MongoDB() as client:
#     docs = find_doc(client, [d['id'] for d in doc_ids])
docs = call_mongodb.delay(doc_ids).get()
print(docs)
ctx = call_rerank_api.delay('Hello, what exactly is a string?', docs).get()
print(ctx)
