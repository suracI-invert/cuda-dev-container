import gradio as gr

import time
import json

import requests

BACKEND = "http://celery:8000"

def query(text):
    ret = ''
    res = requests.post(f'{BACKEND}/re/query', json={'text': text})
    data = res.json()
    task_id = data['id']
    while True:
        res = requests.get(f'{BACKEND}re/query/status/{task_id}')
        task_state = res.json()
        if task_state['state'] == 1:
            ret = task_state['data']['response']
            break
        elif task_state['state'] == 2:
            ret = 'Failed'
            break
        else:
            continue
    return ret

def test(text):
    progress = gr.Progress()
    progress((0, None), desc='Est')
    for i in range(1, 10):
        progress((i, None), desc=f'Step {i}')
        time.sleep(1)
    return text + ' processed'

def query_rag(text):
    ret = {}
    progress = gr.Progress()
    progress((0, 7), desc='Establishing connection ...')
    with requests.Session() as s:
        data = {'text': text}
        res = s.post(f'{BACKEND}/query', json=data, stream=True)
        if res.status_code == 200:
            for i, l in enumerate(res.iter_lines()):
                res_data = json.loads(l)
                ret[res_data['stage']] = res_data['content']
                progress((i, 7), desc=res_data['stage'])
    return ret['call_gpt']

demo = gr.Interface(
    fn=query_rag,
    inputs=["text"],
    outputs=["text"],
)

if __name__ == '__main__':
    demo.launch(server_name='0.0.0.0', server_port=7000)