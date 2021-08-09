from constants import ConfigKeys, RPCMicroServices
from nameko.standalone.rpc import ServiceRpcProxy


def rpc_proxy(service):
    config = {ConfigKeys.AMQPUri: "amqp://guest:guest@rabbit/"}
    return ServiceRpcProxy(service, config)


def add_items_to_feeds():
    with rpc_proxy(RPCMicroServices.FeedService) as rpc:
        rpc.create_feeds_items()

