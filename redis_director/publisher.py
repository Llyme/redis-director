from typing import Any, Callable, Dict
from fun_things.math import weighted_distribution
from redis import Redis

from .subscriber import Subscriber


class Publisher:
    def __init__(
        self,
        redis: Redis,
        score_key: str,
        queue_key: str,
    ):
        self.__subscribers: Dict[str, Subscriber] = {}

        self.__redis = redis
        self.__score_key: str = score_key
        self.__queue_key: str = queue_key

    @property
    def redis(self):
        return self.__redis

    @property
    def score_key(self):
        return self.__score_key

    @property
    def queue_key(self):
        return self.__queue_key

    def reset_scores(self):
        for subscriber in self.__subscribers.values():
            subscriber.reset_score()

    def add_subscriber(
        self,
        score_member: str,
        handler: Callable[[Subscriber, Any], None],
        default_score: float = 100,
        min_score: float = 1,
        max_score: float = 100,
    ):
        return self.add_subscribers(
            Subscriber.new(
                redis=self.__redis,
                score_key=self.__score_key,
                score_member=score_member,
                default_score=default_score,
                min_score=min_score,
                max_score=max_score,
                handler=handler,
            )
        )

    def add_subscribers(self, *subscribers: Subscriber):
        for subscriber in subscribers:
            self.__subscribers[subscriber.score_member] = subscriber

        return self

    def get_subscriber(self, member: str) -> Subscriber:
        if member not in self.__subscribers:
            return None  # type: ignore

        return self.__subscribers[member]

    def publish(
        self,
        batch_size=1,
    ):
        payloads = self.__redis.spop(
            self.__queue_key,
            batch_size,
        )

        if payloads == None:
            return self

        for payload in payloads:
            subscribers = weighted_distribution(
                self.__subscribers.values(),
                lambda subscriber: subscriber.score,
            )

            for subscriber in subscribers:
                if subscriber.handler != None:
                    subscriber.handler(subscriber, payload)

                break

        return self
