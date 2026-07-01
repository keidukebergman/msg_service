from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
import re

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}$")

class MessageCreate(BaseModel):
    sender_id: str = Field(pattern = EMAIL_PATTERN)
    recipient_id: str = Field(pattern = EMAIL_PATTERN)
    subject: str = ""
    contents: str = ""

class Message(MessageCreate):
    msg_id: UUID
    received_at: datetime
    has_been_read: bool = False

    model_config = ConfigDict(frozen=True)

class MessageDeleteRequest(BaseModel):
    ids: list[UUID]