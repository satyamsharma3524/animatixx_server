import redis

r = redis.StrictRedis(
    host='animatixx_server-redis-1',
    port=6379,
    db=0,
    decode_responses=True
)
