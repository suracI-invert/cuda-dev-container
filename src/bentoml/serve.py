import subprocess
from threading import Thread

import argparse

class NamedProcess(subprocess.Popen):
    def __init__(self, *args, name, port, **kwargs):
        self.name = name
        self.port = port
        super().__init__(*args, **kwargs)
    
def start(services):
    ps = []
    for i, s in enumerate(services):
        port = 3000 + i
        cmd = ['bentoml', 'serve', f'services:{s}','-p' , str(port)]
        ps.append(NamedProcess(cmd, name=s, port=port, stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
    return ps

def poll(p: NamedProcess):
    pid = p.name + '-' + str(p.port)
    while p.poll() is None:
        for l in p.stdout:

            print(f'{pid:<10}| {l.decode().rstrip()}')
    print(f'{p.name} shutdown')
    

def run(services):
    ps = start(services)

    ts = [Thread(target=poll, args=(p,)) for p in ps]

    for t in ts:
        t.start()

    for t in ts:
        t.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('services', type=str, nargs='+')
    args = parser.parse_args()
    run(args.services)