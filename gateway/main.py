import os

from fastapi import FastAPI, Depends, Request, HTTPException
from nameko.standalone.rpc import ServiceRpcProxy
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from schema import Settings, UserDTO, AuthDTO
from dotenv import load_dotenv
from constants import ConfigKeys, RPCMicroServices
from passlib.context import CryptContext

load_dotenv()

app = FastAPI(title="Api Gateway",
              description="""This is a api gateway for our nameko microservices""",
              version="0.0.1",
              docs_url=os.getenv(ConfigKeys.DocUrl),
              )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def rpc_proxy(service):
    config = {ConfigKeys.AMQPUri: os.getenv(ConfigKeys.AMQPUri)}
    return ServiceRpcProxy(service, config)


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.post("/register", response_model=AuthDTO)
def register(user: UserDTO, Authorize: AuthJWT = Depends()):
    with rpc_proxy(RPCMicroServices.UserService) as rpc:
        result = rpc.create_user(dto=user.dict())
        if result:
            auth_resp = AuthDTO(access_token=Authorize.create_access_token(subject=result['username']),
                                refresh_token=Authorize.create_refresh_token(subject=result['username']))
            return auth_resp.dict()
        else:
            raise HTTPException(status_code=400, detail="User exists!")


@app.get("/users/me", response_model=UserDTO, response_model_exclude_none=True)
def get_user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    username = Authorize.get_jwt_subject()

    with rpc_proxy(RPCMicroServices.UserService) as rpc:
        result = rpc.get_user(username=username)
        if result:
            return result
        else:
            raise HTTPException(status_code=400, detail="User not exists!")


@app.post("/login", response_model=AuthDTO, response_model_exclude_none=True)
def login_user(user: UserDTO, Authorize: AuthJWT = Depends()):
    with rpc_proxy(RPCMicroServices.UserService) as rpc:
        result = rpc.login_user(email=user.email, password=user.password)

        if result:
            auth_resp = AuthDTO(access_token=Authorize.create_access_token(subject=result['username']),
                                refresh_token=Authorize.create_refresh_token(subject=result['username']))
            return auth_resp.dict()
        else:
            raise HTTPException(status_code=400, detail="User not exist with these credentials!")
