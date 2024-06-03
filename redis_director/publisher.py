from typing import Any, Callable, Dict, Iterable
from fun_things.math import weighted_distribution
from redis import Redis

from .subscriber import Subscriber


class Publisher:
    def __init__(
        self,
        redis: Redis,
        score_key: str,
        queue_key: str,
        add_payloads_callback: Callable[
            [
                "Publisher",
                Iterable,
            ],
            None,
        ] = None,  # type: ignore
        pop_payloads_callback: Callable[
            [
                "Publisher",
                int,
            ],
            list,
        ] = None,  # type: ignore
    ):
        self.__subscribers: Dict[str, Subscriber] = {}

        self.__redis = redis
        self.__score_key: str = score_key
        self.__queue_key: str = queue_key
        self.__add_payloads_callback = add_payloads_callback
        self.__pop_payloads_callback = pop_payloads_callback

        from redis_director.callback import (
            generic_sadd_callback,
            generic_srandpop_callback,
        )

        if add_payloads_callback == None:
            self.__add_payloads_callback = generic_sadd_callback

        if pop_payloads_callback == None:
            self.__pop_payloads_callback = generic_srandpop_callback

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

    @property
    def random_subscriber(self):
        """
        Returns 1 random subscriber
        based on their scores.

        The higher score has the higher chance
        of being chosen.
        """
        subscribers = weighted_distribution(
            self.__subscribers.values(),
            lambda subscriber: subscriber.score,
        )

        for subscriber in subscribers:
            return subscriber

        raise ValueError("No subscribers found!")

    @property
    def random_subscribers(self):
        """
        Infinitely returns a random subscriber
        based on their scores.

        The higher score has the higher chance
        of being chosen.
        """
        while True:
            yield self.random_subscriber

    @property
    def subscriber_max(self):
        """
        Returns the subscriber with the highest score.
        """
        try:
            return max(
                self.__subscribers.values(),
                key=lambda subscriber: subscriber.score,
            )

        except:
            pass

        return None

    @property
    def subscriber_min(self):
        """
        Returns the subscriber with the lowest score.
        """
        try:
            return min(
                self.__subscribers.values(),
                key=lambda subscriber: subscriber.score,
            )

        except:
            pass

        return None

    def add_payloads(self, *payloads):
        if self.__add_payloads_callback == None:
            raise TypeError("`add_payloads_callback` not provided!")

        self.__add_payloads_callback(
            self,
            payloads,
        )

        return self

    def __get_payloads(
        self,
        batch_size: int,
    ):
        if self.__pop_payloads_callback == None:
            raise TypeError("`pop_payloads_callback` not provided!")

        payloads = self.__pop_payloads_callback(
            self,
            batch_size,
        )

        if payloads == None:
            return []

        return payloads

    def publish_max(
        self,
        batch_size=1,
    ):
        """
        Publishes to the subscriber with the highest score.
        """
        payloads = self.__get_payloads(batch_size)

        for payload in payloads:
            subscriber = self.subscriber_max

            if subscriber == None:
                continue

            if subscriber.handler == None:
                continue

            subscriber.handler(subscriber, payload)

    def publish_min(
        self,
        batch_size=1,
    ):
        """
        Publishes to the subscriber with the lowest score.
        """
        payloads = self.__get_payloads(batch_size)

        for payload in payloads:
            subscriber = self.subscriber_min

            if subscriber == None:
                continue

            if subscriber.handler == None:
                continue

            subscriber.handler(subscriber, payload)

    def publish(
        self,
        batch_size=1,
    ):
        """
        Publishes to a random subscriber.

        High score increases the odds of being chosen.
        """
        payloads = self.__get_payloads(batch_size)

        for payload in payloads:
            for subscriber in self.random_subscribers:
                if subscriber.handler != None:
                    subscriber.handler(subscriber, payload)

                break

        return self
