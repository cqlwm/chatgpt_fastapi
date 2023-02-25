# chatgpt_fastapi

## start

```shell
pip install -r requirements.txt

uvicorn main:app --host 0.0.0.0 --port 80


```

## build

```shell
docker build -t chatgpt_fastapi:0.0.1 . && docker run -p 8080:80 --name chatgpt_fastapi_c --rm chatgpt_fastapi:0.0.1 
```
