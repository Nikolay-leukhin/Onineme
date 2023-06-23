import dataclasses


@dataclasses.dataclass
class UserUpdateItem:
    user_id: int
    status: bool


@dataclasses.dataclass
class UpdateSchema:
    anime_id: int
    scene: int
    sound: str
    user_list: list

    def __repr__(self):
        return f"""
        ---UPDATE ANIME---
NAME:{self.anime_id}
SCENE:{self.scene}
SOUND:{self.sound}
USERS:{self.user_list}
        """
