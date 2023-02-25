import json
import logging

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
    def __init__(self, simple_message: str, exc_info: Exception):
        super().__init__(status_code=200, detail=BaseResponse(code='600', body={
            "simple_message": simple_message,
            "exc_info": exc_info,
        }))


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
        msg = "create chatbot failed"
        logger.info(msg=msg, exc_info=e)
        raise ChatBaseException(msg, e)


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
        raise ChatBaseException(simple_message='bot ask failed', exc_info=e)


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
        msg = "create chatbot failed"
        logger.info(msg=msg, exc_info=e)
        raise ChatBaseException(simple_message=msg, exc_info=e)


@app.get("/active")
def active():
    return {"active": True}


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8080, reload=True)
