# server/schema/hello/resolver.py
import asyncio

from ariadne import QueryType, SubscriptionType

from server.helpers.logger_helper import LoggerHelper


class HelloResolver:
    def __init__(self):
        self.__query = QueryType()
        self.__subscription = SubscriptionType()
        self._bind_queries()
        self._bind_subscriptions()
        LoggerHelper.info(f"{self.__class__.__name__} initialized")

    def _bind_queries(self):
        self.__query.set_field("hello", self.resolve_hello)

    def _bind_subscriptions(self):
        self.__subscription.set_source("helloStream", self.hello_stream_source)
        self.__subscription.set_field("helloStream", self.hello_stream_resolver)

    def resolve_hello(self, _, info):
        return "¡Hola desde Ariadne!"

    async def hello_stream_source(self, _, info):
        count = 0
        while True:
            await asyncio.sleep(1)
            count += 1
            yield f"Evento {count} desde subscription"

    def hello_stream_resolver(self, message, info):
        return message

    def get_resolvers(self):
        return [self.__query, self.__subscription]
