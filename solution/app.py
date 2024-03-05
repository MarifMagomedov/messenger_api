import uvicorn
from fastapi import FastAPI, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

from database.database_main import database as db
from auth.auth_main import router as auth_router
from solution.profile.profile_main import router as profile_router
from friends.friends_main import router as friends_router
from posts.posts_main import router as posts_router


app = FastAPI(
    title='PROD'
)


app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(friends_router)
app.include_router(posts_router)


@app.on_event("startup")
async def startup():
    db.create_tables()


@app.get('/api/ping', status_code=status.HTTP_200_OK)
async def ping():
    return {'status': 'ok'}


@app.get('/api/countries')
async def get_all_countries(region: list[str] = Query(default=None)):
    if region is not None:
        return db.get_countries_for_region(region)
    return db.get_all_countries()


@app.get('/api/countries/{alpha2}')
async def get_one_country(alpha2: str):
    country = db.get_country_with_alpha2(alpha2.upper())
    return country


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'reason': 'Вы отправили некорректную форму'
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'reason': 'Вы отправили некорректную форму'
        }
    )

if __name__ == "__main__":
    uvicorn.run("app:app", port=8080, reload=True, access_log=True)
