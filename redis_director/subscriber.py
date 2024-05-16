from typing import Any, Callable, NamedTuple
from redis import Redis
from redis.commands.core import Script
from .constants import INCREMENT_LUA_SCRIPT


class Subscriber(NamedTuple):
    redis: Redis
    score_key: str
    """
    The Redis key for the score.
    """
    score_member: str
    """
    The Redis member value for the score.
    """
    default_score: float
    """
    The default score.
    """
    min_score: float
    """
    The minimum score.
    """
    max_score: float
    """
    The maximum score.
    """
    handler: Callable[["Subscriber", Any], None]  # type: ignore
    increment_script: Script

    @staticmethod
    def new(
        redis: Redis,
        score_key: str = None,  # type: ignore
        score_member: str = None,  # type: ignore
        default_score: float = 0,
        min_score: float = 1,
        max_score: float = 100,
        handler: Callable[["Subscriber", Any], None] = None,  # type: ignore
    ):
        return Subscriber(
            redis=redis,
            score_key=score_key,
            score_member=score_member,
            default_score=default_score,
            min_score=min_score,
            max_score=max_score,
            handler=handler,
            increment_script=redis.register_script(
                INCREMENT_LUA_SCRIPT,
            ),  # type: ignore
        )

    @property
    def score(self) -> float:
        score = self.redis.zscore(
            self.score_key,
            self.score_member,
        )

        if score == None:
            self.redis.zadd(
                self.score_key,
                {
                    self.score_member: self.default_score,
                },
                nx=True,
            )

            return self.default_score

        return score  # type: ignore

    def add_score(self, value: float):
        return self.increment_script(
            (self.score_key,),
            (
                self.score_member,
                value,
                self.default_score,
                self.min_score,
                self.max_score,
            ),
        )

    def set_score(self, value: float):
        self.redis.zadd(
            self.score_key,
            {
                self.score_member: value,
            },
            xx=True,
        )

        return value

    def reset_score(self):
        self.set_score(self.default_score)

        return self.default_score
