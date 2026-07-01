from uuid import UUID
from fastapi import FastAPI, Header, HTTPException, Query, status, Depends
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from typing import Optional
from app.in_memory_storage import message_storage
from app.models import Message, MessageCreate, MessageDeleteRequest
import re


app = FastAPI(title="ostra-messaging-service")
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}$")

def get_user_id(user_id: str = Header(...)) -> str:
    if not EMAIL_PATTERN.match(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id must be a valid email address",
        )
    return user_id

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )

@app.post("/api/send", response_model=Message, status_code=status.HTTP_201_CREATED)
def post_message(msg: MessageCreate, user_id: str = Depends(get_user_id)):
    if not msg.recipient_id or not msg.sender_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sender_id and recipient_id are required"
        )
    if user_id != msg.sender_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user id and sender id need to match"
        )
    return message_storage.add_message(msg)

@app.get("/api/messages/{id}", response_model=Message)
def get_message(id: UUID, user_id: str = Depends(get_user_id)):
    msg = message_storage.get_user_message_by_id(user_id, id)
    if msg is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message {id} not found"
        )
    return msg

@app.patch("/api/messages/{id}/mark_read", response_model=Message)
def mark_message_read(id: UUID, user_id: str = Depends(get_user_id)):
    msg = message_storage.mark_read(user_id, id)
    if msg is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message {id} not found"
        )
    return msg

@app.delete("/api/messages/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_single_message(id: UUID, user_id: str=Depends(get_user_id)):
    success = message_storage.delete_message(user_id, id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message {id} not found"
        )


@app.delete("/api/messages", status_code=status.HTTP_204_NO_CONTENT)
def delete_multiple_messages(payload: MessageDeleteRequest,
                             user_id: str = Depends(get_user_id)):
    if not payload.ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No IDs provided"
        )
    for id in payload.ids:
        message_storage.delete_message(user_id, id)
        #For transparency it might be better to check that all ids are valid and 
        #throw an error if there are illegal ones

@app.get("/api/messages", response_model=list[Message])
def get_messages(only_unread: bool = Query(False),
                 start_index: Optional[int] = Query(None),
                 end_index: Optional[int] = Query(None),
                 user_id: str = Depends(get_user_id)):
    
    if (start_index is not None and start_index < 0) or (end_index is not None and end_index < 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indices must be positive integers"
        )
    if start_index is not None and end_index is not None and start_index > end_index:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_index must be less than, or equal to, end_index"
        )

    messages = message_storage.get_messages_by_recipient(user_id)

    if only_unread:
        messages = [obj for obj in messages if not obj.has_been_read]

    if start_index is not None or end_index is not None:
        start = start_index if start_index is not None else 0
        end = end_index + 1 if end_index is not None else None
        messages = messages[start:end]

    return messages

#mostly for debug, feel free to use
@app.get("/api/message_count", response_model=int)
def get_user_message_count(user_id: str = Depends(get_user_id)):
    return message_storage.message_count_for_user(user_id)