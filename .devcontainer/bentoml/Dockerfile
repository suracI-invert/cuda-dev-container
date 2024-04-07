FROM pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime as base

RUN pip install --upgrade pip

FROM python:3.12.1-slim-bookworm as pre-image
WORKDIR /downloads
RUN pip install gdown
RUN gdown --folder https://drive.google.com/drive/folders/1fLz0GXvPnXVe61Zg_9NNVYQIR3CDNcjG?usp=sharing

FROM base as prod

WORKDIR /workspaces

COPY --from=pre-image /downloads/ /workspaces/

COPY bentoml/requirements /workspaces/.devcontainer/bentoml/
COPY bentoml/install_dep.py /workspaces/.devcontainer/bentoml/

RUN python /workspaces/.devcontainer/bentoml/install_dep.py

COPY ../src/bentoml/services.py /workspaces/src/



CMD [ "bentoml", "serve", "src.services:Models" ]