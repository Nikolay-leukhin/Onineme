from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    chat_id: int = Column(Integer, primary_key=True, nullable=False, autoincrement=False)
    username: str = Column(String, nullable=True)


class Titles(Base):
    __tablename__ = 'titles'

    id: int = Column(Integer, primary_key=True, nullable=False)
    name: str = Column(String, nullable=False, unique=True)
    link: str = Column(String, nullable=False)
    image_path: str = Column(String, nullable=False)
    scenes_went: int = Column(Integer, nullable=True)
    scenes_total: int = Column(Integer, nullable=True)
    is_ended: bool = Column(Boolean, nullable=False)


class UsersTitles(Base):
    __tablename__ = 'users_titles'

    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey('users.chat_id'))
    title_id: int = Column(Integer, ForeignKey('titles.id'))

    rel_users = relationship('Users', backref='users_titles')
    rel_titles = relationship('Titles', backref='users_titles')
