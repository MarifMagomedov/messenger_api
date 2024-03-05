from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, ForeignKey, DateTime, ARRAY, String


class Base(DeclarativeBase):
    pass


class Country(Base):
    __tablename__ = 'countries'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str]
    alpha2: Mapped[str]
    alpha3: Mapped[str]
    region: Mapped[str]


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    countryCode: Mapped[str] = mapped_column(nullable=False)
    isPublic: Mapped[bool] = mapped_column(nullable=False)
    phone: Mapped[str] = mapped_column(nullable=True, unique=True)
    image: Mapped[str] = mapped_column(nullable=True)

    friends: Mapped[list["Friend"]] = relationship(back_populates='friend', uselist=True)
    posts: Mapped[list["Post"]] = relationship(back_populates='post', uselist=True)

    def user_response(self):
        return {
            key: value for key, value in self.__dict__.items()
            if value is not None and key not in ['password', 'id']
        }


class Friend(Base):
    __tablename__ = 'friends'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    login: Mapped[str] = mapped_column()
    addedAt: Mapped[datetime] = mapped_column(DateTime)
    friend: Mapped['User'] = relationship(back_populates='friends', uselist=False)
    user_fk: Mapped[str] = mapped_column(ForeignKey('users.login'))

    def user_response(self):
        return {
            'login': self.login,
            'addedAt': self.addedAt.strftime('%Y-%m-%dT%H:%M:%SZ')
        }


class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[str] = mapped_column(primary_key=True)
    content: Mapped[str]
    author: Mapped[str] = mapped_column(ForeignKey('users.login'))
    tags = mapped_column(ARRAY(String))
    createdAt: Mapped[str] = mapped_column(DateTime)
    post: Mapped['User'] = relationship(back_populates='posts', uselist=False)
    isPublic: Mapped[bool]
    user_reactions: Mapped[list['Reaction']] = relationship(back_populates='reaction', uselist=True)

    def user_response(self):
        data = {
            key: value for key, value in self.__dict__.items()
            if value is not None
        }
        data['createdAt'] = data['createdAt'].strftime('%Y-%m-%dZ%H:%M:%SZ')
        data['likesCount'] = sum(1 for i in self.user_reactions if i.user_reaction)
        data['dislikesCount'] = sum(1 for i in self.user_reactions if not i.user_reaction)
        return data


class Reaction(Base):
    __tablename__ = 'reactions'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    post_id: Mapped[str] = mapped_column(ForeignKey('posts.id'))
    user_reaction: Mapped[bool]
    login: Mapped[str]
    reaction: Mapped['Post'] = relationship(back_populates='user_reactions', uselist=False)
