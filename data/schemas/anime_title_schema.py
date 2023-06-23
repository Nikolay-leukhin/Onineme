from typing import Any


class AnimeTitleSchema:
    id: int
    name: str
    scenes_went: Any
    scenes_total: Any
    image_path: str
    link: str
    is_ended: bool

    def __init__(self, name, start, end, image_path, link, is_ended, id=None):
        self.id = id
        self.name = name
        self.scenes_total = end
        self.image_path = image_path
        self.link = link
        self.is_ended = is_ended
        self.scenes_went = start

    def __repr__(self) -> str:
        return (
            f"AnimeTitleSchema(name='{self.name}')"

        )

    def __eq__(self, other):
        return self.name == other.name
