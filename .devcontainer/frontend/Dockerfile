FROM suraci345/pyenv-ubuntu_22.04:3.12.1 as base

RUN pip install --upgrade pip

EXPOSE 8000

FROM base as prod

WORKDIR /workspaces

COPY requirements.txt /workspaces/
RUN pip install -r requirements.txt

COPY ../src/frontend/ /workspaces/