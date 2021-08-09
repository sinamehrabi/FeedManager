import os

from fastapi import FastAPI, Depends, Request, HTTPException
from nameko.standalone.rpc import ServiceRpcProxy
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from schema import Settings, UserDTO, AuthDTO, FeedDTO, ListFeedDTO, ListFeedItemDTO
from dotenv import load_dotenv
from constants import ConfigKeys, RPCMicroServices

load_dotenv()

app = FastAPI(title="Api Gateway",
              description="""This is a api gateway for our nameko microservices""",
              version="0.0.1",
              docs_url=os.getenv(ConfigKeys.DocUrl),
              )


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


@app.get("/feeds", response_model=ListFeedDTO)
def read_feeds(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    with rpc_proxy(RPCMicroServices.FeedService) as rpc:
        feeds = rpc.read_feeds()
        if feeds:
            return feeds
        else:
            raise HTTPException(status_code=404, detail="There is no feed!")


@app.get("/feeds/{feed_id}", response_model=FeedDTO)
def read_one_feed(feed_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    with rpc_proxy(RPCMicroServices.FeedService) as rpc:
        feed = rpc.read_one_feed(feed_id)
        if feed:
            return feed
        else:
            raise HTTPException(status_code=404, detail=f"There is no feed with {feed_id} id!")


@app.post("/feeds", status_code=201)
def create_feed(feed: FeedDTO, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    with rpc_proxy(RPCMicroServices.FeedService) as rpc:
        rpc.create_feed(feed.dict())


@app.get("/users/me/feeds", response_model=ListFeedDTO)
def read_user_feeds(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()

    with rpc_proxy(RPCMicroServices.FeedService) as rpc:
        feeds = rpc.read_user_feeds(username)
        if feeds:
            return feeds
        else:
            raise HTTPException(status_code=404, detail=f"There is no feed for you!")


@app.post("/users/me/feeds/{feed_id}/select", status_code=204)
def bookmark_feed(feed_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()

    with rpc_proxy(RPCMicroServices.FeedService) as rpc:
        result = rpc.select_feed(username, feed_id)
        if result:
            return
        else:
            raise HTTPException(status_code=400, detail=f"You selected this feed before!")


@app.delete("/users/me/feeds/{feed_id}/select", status_code=204)
def bookmark_feed(feed_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()

    with rpc_proxy(RPCMicroServices.FeedService) as rpc:
        result = rpc.deselect_feed(username, feed_id)
        if result:
            return
        else:
            raise HTTPException(status_code=400, detail=f"You didn't select this feed before!")


@app.get("/users/me/feeds/{feed_id}/items", response_model=ListFeedItemDTO)
def read_user_feeds(feed_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()

    with rpc_proxy(RPCMicroServices.FeedService) as rpc:
        feeds = rpc.read_user_feed_items(feed_id, username)
        if feeds:
            return feeds
        else:
            raise HTTPException(status_code=404, detail=f"There is no feed items for you!")