import json
from typing import Union

import uvicorn as uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

chatbots = {}


@app.get("/active")
def active():
    return {"active": True}


class AskRequest(BaseModel):
    c: dict
    prompt: str
    conversation_id: str
    parent_id: str
    timeout = 360


@app.post("/api/conversation")
def ask(req: AskRequest):
    y = json.dumps(dict(req))
    print(y)
    return req


def create_conversation():
    return {"conversation_id": True}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    uvicorn.run(app="chatgpt_fastapi:app", host="127.0.0.1", port=8080, reload=True)
