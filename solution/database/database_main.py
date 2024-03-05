from datetime import datetime
from uuid import uuid4

from database.models import Country, Base, User, Friend, Post, Reaction
from config import load_configs
from sqlalchemy import select, update, or_, create_engine, delete, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.functions import count
from starlette import status
from starlette.responses import JSONResponse


class Database:
    def __init__(self):
        self.engine = create_engine(
            # url=f"postgresql+psycopg2://postgres:postgres@localhost:5432/postgres",
            url=load_configs(database=True).replace('postgres://',  'postgresql+psycopg2://', 1),
            echo=False
        )
        self.session_factory = sessionmaker(self.engine)

    @staticmethod
    def json_countries(countries: list[Country] | Country) -> list[dict[str, str]] | dict[str, str]:
        if isinstance(countries, Country):
            return {
                "name": countries.name,
                "alpha2": countries.alpha2,
                "alpha3": countries.alpha3,
                "region": countries.region
            }
        result = []
        for country in countries:
            result.append(
                {
                    "name": country.name,
                    "alpha2": country.alpha2,
                    "alpha3": country.alpha3,
                    "region": country.region
                }
            )
        return result

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_all_countries(self) -> list[dict[str, str]]:
        with self.session_factory() as session:
            query = select(Country)
            countries = session.execute(query)
            return self.json_countries(sorted(countries.scalars().all(),
                                              key=lambda item: item.alpha2))

    def get_country_with_alpha2(self, alpha2: str) -> JSONResponse | list[dict[str, str]] | dict[str, str]:
        with self.session_factory() as session:
            query = select(Country).where(Country.alpha2 == alpha2)
            country = session.execute(query)
            country = country.fetchone()
            if country is None:
                return JSONResponse(
                    status_code=404,
                    content={
                        'reason': 'Страна с указанным кодом не найдена'
                    }
                )
            return self.json_countries(country[0])

    def get_countries_for_region(self, regions: list[str]) -> list[dict[str, str]] | JSONResponse:
        with self.session_factory() as session:
            query = select(Country.region)
            regions_names = session.execute(query)
            regions_names = regions_names.scalars().all()
            if not all(i in regions_names for i in regions):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        'reason': 'Некорректный регион!'
                    }
                )
            query = select(Country).filter(Country.region.in_(regions))
            countries = session.execute(query)
            countries = self.json_countries(countries.scalars().all())
            if countries:
                return countries
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    'reason': 'Указанного региона/регионов не существует'
                }
            )

    def create_profile(self, new_user: User) -> None:
        with self.session_factory() as session:
            session.add(new_user)
            session.flush()
            session.commit()

    def check_country_code(self, code: str):
        with self.session_factory() as session:
            query = select(Country.alpha2)
            codes = session.execute(query)
            return code in codes.scalars().all()

    def check_user(
            self,
            login: str
    ) -> User | bool:
        with self.session_factory() as session:
            query = select(User).where(User.login == login)
            user = session.execute(query)
            user = user.fetchone()
            if user:
                return user[0]
            return False

    def check_user_with_email_and_phone(self, email: str, login: str, phone: str) -> User | bool:
        with self.session_factory() as session:
            if phone:
                query = select(User).where(or_(User.login == login, User.email == email, User.phone == phone))
            else:
                query = select(User).where(or_(User.login == login, User.email == email))
            user = session.execute(query)
            user = user.fetchone()
            if user:
                return user[0]
            return False

    def update_profile(self, login: str, **kwargs) -> None:
        with self.session_factory() as session:
            query = update(User).where(User.login == login).values(kwargs)
            session.execute(query)
            session.flush()
            session.commit()

    def add_user_friend(self, friend_login: str, user_login: str) -> None | bool:
        with self.session_factory() as session:
            if user_login == friend_login:
                return True
            data = datetime.utcnow()
            friend = Friend(login=friend_login, addedAt=data)
            query = select(User).where(User.login == user_login)
            user = session.execute(query).fetchone()[0]
            if friend_login not in [item.login for item in user.friends]:
                user.friends.append(friend)
                session.flush()
                session.commit()

    def remove_user_friend(self, friend_login: str, user_login: str) -> JSONResponse | bool:
        with self.session_factory() as session:
            if user_login == friend_login:
                return True
            query = select(User).where(User.login == user_login)
            user = session.execute(query).fetchone()[0]
            if friend_login in [item.login for item in user.friends]:
                query = delete(Friend).where(
                    Friend.user_fk == user_login, Friend.login == friend_login
                )
                session.execute(query)
                session.flush()
                session.commit()
            else:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={
                        'reason': 'Пользователь с указанным логином не найден.'
                }
            )

    def get_user_friends(self, login: str, limit: int, offset: int) -> list[User]:
        with self.session_factory() as session:
            query = select(Friend).where(Friend.user_fk == login).order_by(Friend.addedAt).limit(limit).offset(offset)
            friends = session.execute(query).scalars().all()
            return [
                item.user_response()
                for item in reversed(friends)
            ]

    def create_user_post(self, login: str, is_public: bool, post_data):
        with self.session_factory() as session:
            new_post = {
                'id': uuid4(),
                'content': post_data.content,
                'author': login,
                'tags': post_data.tags,
                "createdAt": datetime.utcnow()
            }
            query = insert(Post).values(
                **new_post, isPublic=is_public
            )
            session.execute(query)
            session.flush()
            session.commit()
            new_post['likesCount'] = 0
            new_post["dislikesCount"] = 0
            return new_post

    def get_post_for_id(self, post_id: str) -> Post | JSONResponse:
        with self.session_factory() as session:
            query = select(Post).where(Post.id == post_id)
            post = session.execute(query).fetchone()
            if not post:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={
                        'reason': 'Поста с таким id не существует'
                    }
                )
            return post[0].user_response()

    def get_user_posts(self, login: str, limit: int, offset: int, my: str = False) -> list[Post] | JSONResponse:
        try:
            with self.session_factory() as session:
                query = select(
                    Post
                ).where(
                    Post.author == login
                ).order_by(
                    Post.createdAt
                ).limit(limit).offset(offset)
                posts = session.execute(query).scalars().all()
                if my or login == posts[0].author:
                    return [
                        item.user_response()
                        for item in reversed(posts)
                    ]
                if posts and not posts[0].isPublic:
                    return JSONResponse(
                        status_code=status.HTTP_404_NOT_FOUND,
                        content={
                            'reason': 'У вас нет доступа к постам пользователя!'
                        }
                    )
        except IntegrityError:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    'reason': 'Поста с таким id не существует'
                }
            )

    def set_post_reaction(self, login: str, post_id: str, reaction: bool) -> Post:
        try:
            with self.session_factory() as session:
                query = select(Reaction).where(Reaction.post_id == post_id, Reaction.login == login)
                user_reaction = session.execute(query).fetchone()
                if user_reaction:
                    query = f"UPDATE reactions SET user_reaction={reaction} WHERE post_id = '{post_id}' AND login = '{login}'"
                else:
                    query = f"INSERT INTO reactions (post_id, login, user_reaction) VALUES ('{post_id}', '{login}', {reaction})"
                session.execute(text(query))
                session.flush()
                session.commit()
                post = session.get(Post, post_id)
                return post.user_response()
        except IntegrityError:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    'reason': 'Поста с таким id не существует'
                }
            )

database = Database()
