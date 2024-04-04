from fastapi import FastAPI

from tasks import add, matmul, call_embedding_api

app = FastAPI()

@app.get('/')
def hello():
    return 'BENTOML IS WEIRD'

@app.post('/bentoml/emb')
def bentoml_emb(text: str):
    

result = call_embedding_api.delay('Hello, what exactly is a string?')

print(result.get())