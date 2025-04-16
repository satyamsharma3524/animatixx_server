from celery import shared_task
from datetime import datetime
from utils.redis_client import r


@shared_task
def track_manga_view(user_id, manga_id):
    print(f"Tracking manga view for user {user_id} and manga {manga_id}")
    if user_id:
        key = f"user:{user_id}:recent_manga"
        r.lrem(key, 0, manga_id)
        r.lpush(key, manga_id)
        r.ltrim(key, 0, 9)

    today = datetime.utcnow().strftime("%Y-%m-%d")
    r.zincrby(f"trending:manga:{today}", 1, manga_id)
    r.zincrby("popular:manga", 1, manga_id)
    r.incr(f"manga:{manga_id}:views")
