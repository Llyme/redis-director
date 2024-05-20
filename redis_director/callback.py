from typing import Iterable

from redis_director.publisher import Publisher


def generic_sadd_callback(
    publisher: Publisher,
    payloads: Iterable[str],
):
    return publisher.redis.sadd(
        publisher.queue_key,
        *payloads,
    )


def generic_rpush_callback(
    publisher: Publisher,
    payloads: Iterable[str],
):
    return publisher.redis.rpush(
        publisher.queue_key,
        *payloads,
    )


def generic_spop_callback(
    publisher: Publisher,
    batch_size: int,
):
    return publisher.redis.spop(
        publisher.queue_key,
        batch_size,
    )


def generic_lpop_callback(
    publisher: Publisher,
    batch_size: int,
):
    return publisher.redis.lpop(
        publisher.queue_key,
        batch_size,
    )
