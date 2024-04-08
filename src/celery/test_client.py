from requests import Session
import json

with Session() as s:
    data = {'text': 'Hello, What is a string?'}
    result = s.post('http://localhost:8000/query', json=data, stream=True)
    if result.status_code == 200:
        for l in result.iter_lines():
            # print(l)
            data = json.loads(l)
            print(data['stage'])
            print('-' * 50)
            print(data['content'])
            print('\n' + '=' * 50 + '\n')
    
    