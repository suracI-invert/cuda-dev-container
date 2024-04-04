import subprocess

from torch.cuda import is_available

def run(cmd_args):
    with subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
        for line in p.stdout:
            print(line.decode('utf8').rstrip('\n'))

def install_gpu_dep():
    cmd = ['pip', 'install', '-r', '/workspaces/.devcontainer/bentoml/requirements/gpu_requirements.txt']
    run(cmd)

def install_cpu_dep():
    cmd = ['pip', 'install', '-r', '/workspaces/.devcontainer/bentoml/requirements/cpu_requirements.txt']
    run(cmd)

def install_dep():
    cmd = ['pip', 'install', '-r', '/workspaces/.devcontainer/bentoml/requirements/requirements.txt']
    run(cmd)

    if is_available():
        install_gpu_dep()
    else:
        install_cpu_dep()

if __name__ == '__main__':
    install_dep()