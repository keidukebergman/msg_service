from app.models import Message, MessageCreate
from datetime import datetime, timezone
from uuid import UUID, uuid4

class MessageStorage:
    def __init__(self):
        self._inboxes: dict[str, dict[UUID, Message]] = {}

    def add_message(self, message: MessageCreate) -> Message:
        msg_id = uuid4()
        msg = Message(
            **message.model_dump(),
            msg_id=msg_id,
            received_at=datetime.now(timezone.utc),
        )
        user_inbox = self._inboxes.setdefault(message.recipient_id, {})
        user_inbox[msg_id] = msg
        return msg

    def get_user_message_by_id(self, user: str, msg_id: UUID) -> Message | None:
        return self._inboxes.get(user, {}).get(msg_id)

    def get_messages_by_recipient(self, user: str) -> list[Message]:
        messages = list(self._inboxes.get(user, {}).values())
        return sorted(messages, key=lambda m: m.received_at) #Slight performance cost, but there are practically no cases where a user would expect messages not to be sorted by time

    def delete_message(self, user: str, msg_id: UUID) -> bool:
        inbox = self._inboxes.get(user, {})
        if msg_id in inbox:
            del inbox[msg_id]
            return True
        return False

    def mark_read(self, user: str, msg_id: UUID) -> Message | None:
        inbox = self._inboxes.get(user, {})
        if msg_id not in inbox:
            return None
        
        updated = inbox[msg_id].model_copy(update={"has_been_read": True})
        inbox[msg_id] = updated
        return updated
    
    #Debug
    def message_count_for_user(self, user:str) -> int:
        inbox = self._inboxes.get(user, {})
        length = len(inbox)
        return length

message_storage = MessageStorage()