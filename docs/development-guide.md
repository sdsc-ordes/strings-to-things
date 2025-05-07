# Development Guide

This guide documents our procedures and policies for project maintenance tasks,
including managing our conventions, pull/merge-requests, continuous integration,
releasing.

## Commit Convention

We use the
[conventional commits](https://www.conventionalcommits.org/en/v1.0.0/)
specification for commit messages and pull/merge-request titles.

## Docker Development

```bash 
docker build -t string2things -f tools/docker/Dockerfile . 
```

```bash
docker run -it --rm --env-file .env -p 1234:1234 -v .:/app --entrypoint bash string2things 
```

```bash
python3 -m uvicorn --reload strings2things.api:app --host 0.0.0.0 --port 1234
uvicorn strings2things.api:app --reload --host 0.0.0.0 --port 1234

export PYTHONPATH="/app/src:$PYTHONPATH"
```


<!-- Additional 'scopes' should be described here.-->
<!-- ### Scopes -->
