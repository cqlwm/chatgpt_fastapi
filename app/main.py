import json
import logging
import uuid
import requests
import uvicorn as uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from V1 import Chatbot

app = FastAPI()

logger = (lambda log: (
    log,
    log.addHandler(logging.StreamHandler()),
    log.setLevel(logging.INFO),
    log.info("setLevel INFO")
))(logging.getLogger(__name__))[0]


def e_termination(msg: str, e):
    detail = json.dumps({
        "msg": msg,
        "e_id": str(uuid.uuid4())
    })
    logger.info(msg=detail, exc_info=e)
    return ChatBaseException(detail=detail)


class BaseResponse:
    code: str
    body: dict

    def __init__(self, code: str = "200", body: dict = None):
        if body is None:
            body = {}
        self.code = code
        self.body = body


def OkResponse(body: dict):
    return BaseResponse(code='200', body=body)


def FailedResponse(body: dict):
    return BaseResponse(code='600', body=body)


class ChatBaseException(HTTPException):

    def __init__(self, detail=None):
        super().__init__(status_code=200, detail={"code": '600', "body": detail})


class AskRequest(BaseModel):
    config: dict
    prompt: str
    conversation_id: str = None
    parent_id: str = None
    timeout: int = 360


def create_chatbot(config: dict):
    try:
        bot = Chatbot(config=config)
        return bot
    except Exception as e:
        raise e_termination("create chatbot failed", e)


@app.post("/api/conversation")
def ask(req: AskRequest):
    logger.info(json.dumps(dict(req)))

    bot = create_chatbot(req.config)

    try:
        res = None
        for data in bot.ask(prompt=req.prompt, conversation_id=req.conversation_id, parent_id=req.parent_id):
            res = data
        return OkResponse(res)
    except Exception as e:
        raise e_termination('bot ask failed', e)


class DeleteChatRequest(BaseModel):
    config: dict
    conversation_id: str = None


@app.post("/api/conversation/remove")
def delete_conversation(req: DeleteChatRequest):
    logger.info(json.dumps(dict(req)))

    bot = create_chatbot(req.config)

    try:
        bot.delete_conversation(req.conversation_id)
        return OkResponse({"success": True})
    except Exception as e:
        raise e_termination("create chatbot failed", e)


class QaRequest(BaseModel):
    model: str = "text-davinci-003"
    api_key: str
    prompt: str
    max_tokens: int = 2048
    temperature: float = 0.8


@app.post("/api/qa")
def qa(req: QaRequest):
    url = 'https://api.openai.com/v1/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + req.api_key
    }
    data = {
        'model': req.model,
        'prompt': req.prompt,
        'max_tokens': req.max_tokens,
        'temperature': req.temperature,
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        content = dict(json.loads(response.content))
        if 'error' in content:
            raise ChatBaseException(content)
        return OkResponse(content)
    except Exception as e:
        raise e_termination('qa failed detail_id', e)


@app.get("/active")
def active():
    return {"active": True}


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8080, reload=True)
