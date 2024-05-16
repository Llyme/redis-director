from .subscriber import Subscriber


def generic_set_handler(
    key: str,
    add_score: float = -1,
):
    def handler(route: Subscriber, payload):
        route.add_score(add_score)
        route.redis.sadd(key, payload)

    return handler


def generic_list_handler(
    key: str,
    add_score: float = -1,
):
    def handler(route: Subscriber, payload):
        route.add_score(add_score)
        route.redis.lpush(key, payload)

    return handler
