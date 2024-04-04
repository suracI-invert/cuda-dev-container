from fastapi import FastAPI

from database.connect import MongoDB, VectorDB
from database.crud import find_doc, search

from tasks import add, matmul, call_embedding_api, call_rerank_api

# app = FastAPI()

# @app.get('/')
# def hello():
#     return 'BENTOML IS WEIRD'

# @app.post('/bentoml/emb')
# def bentoml_emb(text: str):
    

emb = call_embedding_api.delay('Hello, what exactly is a string?').get()
print(len(emb))
with VectorDB() as client:
    doc_ids = search(client, emb['embedding'])
print(doc_ids)
with MongoDB() as client:
    docs = find_doc(client, [d['id'] for d in doc_ids])
print(docs)
ctx = call_rerank_api.delay('Hello, what exactly is a string?', [d['abstract'] for d in docs]).get()
print(ctx)