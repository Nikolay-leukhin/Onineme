from dataclasses import dataclass


@dataclass
class UserSchema:
    chat_id: int
    username: str

    def __repr__(self):
        return f"UserSchema(chat_id = {self.chat_id}), username = {self.username}"
