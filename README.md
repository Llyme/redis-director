# Redis Director
Do you want to distribute payloads between multiple Redis keys?
Here you go!

# Installation

```sh
pip install redis-director
```

# How to Use

## Publisher's Side

```py
from redis import Redis
from redis_director import Publisher, Subscriber, generic_set_handler

pub = Publisher(
    redis=Redis(),
    score_key="my_stuff:my_fancy_score",
    queue_key="my_stuff:my_amazing_queue",
)


def custom_handler(subscriber: Subscriber, payload):
    """
    You can make custom handlers
    if you have some complex stuff to do.
    """
    subscriber.add_score(-2)

    subscriber.redis.lpush(
        "super:secret:route:hehe",
        payload,
    )


pub.add_subscriber(
    # The subscriber's name.
    "route_1",
    # A generic handler.
    # You can make your own if you want to.
    handler=generic_set_handler(
        # The subscriber's Redis key.
        "route_1:queue",
        # The score added to this subscriber.
        # The scores are used as weights for distribution.
        -1,
    ),
    # The starting score.
    default_score=100,
    # The minimum score possible.
    min_score=1,
    # The maximum score possible.
    max_score=100,
).add_subscriber(
    # Make another route so
    # the payloads are distributed between them.
    "route_2",
    handler=custom_handler,
    default_score=100,
    min_score=0,
    max_score=1000,
)

# Fill up the publisher's queue.
pub.redis.sadd(pub.queue_key, *range(0, 1000))

# Distribute them to the subscribers!
pub.publish(100)
```

## Subscriber's Side

You can also play with the scores from the subscriber's side!

```py
from redis import Redis
from redis_director import Subscriber

sub = Subscriber.new(
    redis=Redis(),
    score_key="my_stuff:my_fancy_score",
    score_member="bobs_amazing_queue",
    default_score=100,
    min_score=1,
    max_score=100,
)

# Want to boost the chances of your subscriber to be chosen?
# Add some score!
sub.add_score(10)

# Set the score!
# This ignores the min/max score.
sub.set_score(500)

# Messed up the score?
# Just reset it back to its default score!
sub.reset_score()

```