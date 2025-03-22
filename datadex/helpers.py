import requests
import time
import re
import random

from manga.models import Chapter, Manga


def fetch_manga_data(offset):
    url = ("https://api.mangadex.org/manga?"
           f"availableTranslatedLanguage[]=en&limit=100&offset={offset}")
    try:
        response = requests.get(url)
        response_data = response.json()
    except Exception as e:
        print("Error fetching manga data from Mangadex:", e)
    else:
        manga_data_list = response_data['data']
        for manga_data in manga_data_list:
            title_dict = manga_data.get('attributes', {}).get('title', {})
            first_key = next(iter(title_dict), None)
            payload = {
                'title': title_dict.get(first_key, "Unknown Title"),
                'alt_titles': manga_data['attributes']['altTitles'],
                'description': manga_data.get('attributes', {}).get(
                    'description', {}).get('en', 'No description available'),
                'alt_description': manga_data[
                    'attributes']['description'],
                'original_language': manga_data[
                    'attributes']['originalLanguage'],
                'last_chapter': manga_data[
                    'attributes']['lastChapter'],
                'completion_status': manga_data[
                    'attributes']['status'] == 'completed',
                # 'tags': manga_data['attributes']['tags'],
                'latest_chapter': manga_data[
                    'attributes']['latestUploadedChapter'],
            }
            manga, created = Manga.objects.update_or_create(
                dex_id=manga_data['id'], defaults=payload)
            if created:
                time.sleep(2)
                print(f"Created manga and called for image: {manga}")
                get_manga_images(manga)
                print(f"Called for manga Chapters: {manga}")
                get_manga_chapters(manga)
            else:
                print(f"Updated manga: {manga}")


def fetch_anilist_data(query, variables):
    """Fetch data from AniList API with rate limiting."""
    url = "https://graphql.anilist.co"

    while True:
        response = requests.post(
            url, json={"query": query, "variables": variables})

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("Rate limit exceeded! Waiting before retrying...")
            time.sleep(2)  # Wait 2 seconds before retrying
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None


def get_manga_images(manga):
    """Fetch manga details from AniList using search queries."""

    title = re.sub(r"[^a-zA-Z0-9\s]", " ", manga.title)
    search_title = " ".join(title.split()[:4])
    print(f"Searching for: {search_title}")

    query = '''query ($search: String) {
        Media(search: $search, type: MANGA) {
            id
            title {romaji english native}
        }
    }'''

    variables = {"search": search_title}
    response_data = fetch_anilist_data(query, variables)

    if response_data and "data" in response_data and (
            response_data["data"].get("Media")):
        manga_anilist_id = response_data["data"]["Media"]["id"]

        # Query to get full manga details
        query = '''query ($id: Int) {
            Media(id: $id, type: MANGA) {
                id
                title {romaji english native}
                description
                coverImage {extraLarge}
                bannerImage
                genres
                episodes
                status
                averageScore
            }
        }'''

        variables = {"id": manga_anilist_id}
        response_data = fetch_anilist_data(query, variables)

        if response_data and "data" in response_data and (
                response_data["data"].get("Media")):
            media_data = response_data["data"]["Media"]
            manga.anilist_id = manga_anilist_id
            manga.cover_image = media_data["coverImage"]["extraLarge"]
            manga.banner_image = media_data.get("bannerImage")
            manga.save()
            print(f"Updated manga: {manga}")
        else:
            print(f"Couldn't find detailed data for {manga}, skipping.")
    else:
        print(f"Couldn't find {manga} on AniList, skipping.")


def get_manga_chapters(manga):
    """
    Fetches and stores chapters for a given Manga from MangaDex API.
    Implements rate-limiting handling using exponential backoff.
    """
    url = f"https://api.mangadex.org/manga/{manga.dex_id}/feed"
    params = {
        "translatedLanguage[]": "en",
        "order[chapter]": "asc"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching manga chapters: {e}")
        return

    for chapter_data in data.get("data", []):
        attributes = chapter_data.get("attributes", {})
        chapter_id = chapter_data["id"]
        chapter_number = attributes.get("chapter", "0")
        title = attributes.get("title", "")
        release_date = attributes.get("publishAt", None)

        # Fetch images with rate-limit handling
        chapter_images, datasaver_images, base_url, hash_code = (
            get_chapter_images_with_retry(chapter_id))
        if not chapter_images:
            print(f"Skipping Chapter {chapter_number}"
                  " due to image fetch failure")
            continue

        # Store the chapter in the database
        chapter, created = Chapter.objects.update_or_create(
            manga=manga,
            chapter_dex_id=chapter_id,
            defaults={
                "title": title,
                "chapter_number": chapter_number,
                "chapter_dex_id": chapter_id,
                "release_date": release_date,
                "images": chapter_images,
                "datasaver_images": datasaver_images,
                "base_url": base_url,
                "hash_code": hash_code
            }
        )

        if created:
            print(f"Added Chapter {chapter_number} for {manga.title}")
        else:
            print(f"Updated Chapter {chapter_number} for {manga.title}")

        # Random sleep to prevent hitting rate limits
        time.sleep(random.uniform(1, 3))


def get_chapter_images_with_retry(chapter_id, max_retries=5):
    """
    Fetches image URLs and metadata for a given chapter ID from MangaDex API.
    Implements exponential backoff and handles remote disconnections.
    """
    url = f"https://api.mangadex.org/at-home/server/{chapter_id}"

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                base_url = data["baseUrl"]
                hash_code = data["chapter"]["hash"]
                page_filenames = data["chapter"]["data"]
                datasaver_filenames = data["chapter"].get("dataSaver", [])

                # Construct full image URLs
                images = [
                    f"{base_url}/data/{hash_code}/{filename}"
                    for filename in page_filenames]
                datasaver_images = [
                    f"{base_url}/data-saver/{hash_code}/{filename}"
                    for filename in datasaver_filenames]

                return images, datasaver_images, base_url, hash_code

            elif response.status_code == 429:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limited! Retrying in {wait_time:.2f} sec...")
                time.sleep(wait_time)

            else:
                print("Error fetching chapter images (HTTP"
                      f" {response.status_code}): {response.text}")
                return [], [], None, None

        except requests.exceptions.ConnectionError as e:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"Connection error: {e}. Retrying in {wait_time:.2f} sec...")
            time.sleep(wait_time)

        except requests.exceptions.Timeout:
            print(f"Request timeout. Retrying in {(2 ** attempt):.2f} sec...")
            time.sleep(2 ** attempt)

        except requests.exceptions.RequestException as e:
            print(f"Unexpected error: {e}")
            return [], [], None, None

    print("Max retries reached, skipping chapter images")
    return [], [], None, None
