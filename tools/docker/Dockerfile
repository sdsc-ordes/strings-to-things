FROM python:3.12-slim-bookworm

EXPOSE 8080

# gettext-base is required for envsubst (config templating)
RUN apt update && apt install -y gettext-base libc6-dev git && apt-get clean

# install uv
COPY --from=ghcr.io/astral-sh/uv:0.6.3 /uv /uvx /bin/

ADD . /app
WORKDIR /app

RUN pip install --no-cache-dir rdflib dotenv fastapi uvicorn


COPY --chmod=755 tools/docker/entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
