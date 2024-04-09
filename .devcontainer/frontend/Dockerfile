FROM suraci345/pyenv-ubuntu_22.04:3.12.1 as base

RUN pip install --upgrade pip

EXPOSE 7000

FROM base as prod

WORKDIR /workspaces

COPY .devcontainer/frontend/requirements.txt /workspaces/
RUN pip install -r requirements.txt

COPY src/frontend/main.py /workspaces/

CMD [ "python", "main.py" ]