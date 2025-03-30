from manga.models import UserHistory


def update_manga_history(user, manga, chapter):
    """Update or create user history for manga reading."""

    history, created = UserHistory.objects.get_or_create(
        user=user, manga=manga)

    # Update chapter progress
    history.last_read_chapter = chapter
    # history.progress_percentage = (
    #     chapter / manga.last_chapter) * 100 if manga.last_chapter else 0
    # history.is_completed = history.progress_percentage >= 100
    history.save()

    return history
