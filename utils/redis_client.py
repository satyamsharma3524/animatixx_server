import redis

r = redis.StrictRedis(
    host='animatrixx-redis',
    port=6379,
    db=0,
    decode_responses=True
)
