import asyncio

from database.models import Country, Base, User
from config import load_configs
from sqlalchemy import select, update, or_, create_engine
from sqlalchemy.orm import sessionmaker
from starlette import status
from starlette.responses import JSONResponse


class Database:
    def __init__(self):
        self.engine = create_engine(
            # url=f"postgresql+psycopg2://postgres:postgres@localhost:5432/postgres",
            url=load_configs(database=True).replace('postgres://', 'postgresql+psycopg2://', 1),
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
        with (self.session_factory() as session):
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
            email: str = None,
            login: str = None,
            phone: str = None,
            auth: bool = False
    ) -> User | bool:
        with self.session_factory() as session:
            if auth:
                query = select(User).where(User.login == login)
            else:
                query = select(User).where(or_(User.email == email, User.login == login, User.phone == phone))
            result = session.execute(query)
            result = result.fetchone()
            if result:
                return result[0]
            return False
