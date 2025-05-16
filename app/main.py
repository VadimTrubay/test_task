from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED

from app.database import SessionLocal, get_db
from app.schemas import NameResponse, PopularNamesResponse
from app.crud import get_popular_names
from app.services import process_name_request
from app.auth import authenticate_user, create_access_token

app = FastAPI(
    title="Name Origin Service",
    description="API for predicting country of origin based on names",
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token")
async def login_for_access_token(username: str, password: str):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/names/", response_model=NameResponse)
async def get_name_origin(
    name: str = Query(..., min_length=1, max_length=100),
    token: str = Depends(oauth2_scheme),
    db: SessionLocal = Depends(get_db),
):
    return process_name_request(db, name)


@app.get("/popular-names/", response_model=PopularNamesResponse)
async def get_popular_names_by_country(
    country: str = Query(..., min_length=2, max_length=2),
    token: str = Depends(oauth2_scheme),
    db: SessionLocal = Depends(get_db),
):
    names = get_popular_names(db, country.upper())
    if not names:
        raise HTTPException(
            status_code=404, detail="No data available for this country"
        )
    return {"country": country.upper(), "names": names}
