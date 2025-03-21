import requests
import time
import re

from manga.models import Manga


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
                time.sleep(1.5)
                get_manga_images(manga)
                print(f"Created manga and called for image: {manga}")
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

    title = re.split(r"[^a-zA-Z0-9\s]", manga.title, 1)[0]
    search_title = " ".join(title.split()[:4])
    print(f"Searching for: {search_title}")

    # Query to search for manga by name
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
