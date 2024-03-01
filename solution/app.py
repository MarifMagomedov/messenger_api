import uvicorn
from fastapi import FastAPI, Query
from starlette import status
from database.database_main import Database
from auth.auth_main import router as auth_router
from solution.profile.profile_main import router as profile_router


app = FastAPI(
    title='PROD'
)
db = Database()


app.include_router(auth_router)
app.include_router(profile_router)


@app.get('/api/ping', status_code=status.HTTP_200_OK)
async def ping():
    db.create_tables()
    return {'status': 'ok'}


@app.get('/api/countries')
async def get_all_countries(region: list[str] = Query(default=None)):
    if region is not None:
        return db.get_countries_for_region(region)
    return db.get_all_countries()


@app.get('/api/countries/{alpha2}')
async def get_one_country(alpha2: str):
    country = db.get_country_with_alpha2(alpha2)
    return country


if __name__ == "__main__":
    uvicorn.run("app:app", port=8080, reload=True, access_log=True)
