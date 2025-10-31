from rest_framework.views import APIView
# from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
# from elasticsearch_dsl.query import MultiMatch
from manga.documents import MangaDocument
import requests
from django.http import HttpResponse, JsonResponse
from urllib.parse import urlparse


class MangaSearchPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class MangaSearchView(APIView):
    def get(self, request):
        query = request.GET.get('q', '')
        tags = request.GET.getlist('tags')
        completed = request.GET.get('completed')

        search = MangaDocument.search()
        if query:
            search = search.query(
                "multi_match",
                query=query,
                fields=["title^3", "description", "tags"],
                fuzziness="auto"
            )

        if tags:
            for tag in tags:
                search = search.filter('term', tags=tag)

        if completed in ['true', 'false']:
            is_completed = completed.lower() == 'true'
            search = search.filter(
                'term', completion_status=is_completed)

        # Execute search with pagination
        paginator = MangaSearchPagination()
        results = paginator.paginate_queryset(search, request)

        serialized = [
            {
                'id': hit.meta.id,
                'title': hit.title,
                'description': hit.description,
                'tags': [str(tag) for tag in hit.tags],
                'completion_status': hit.completion_status,
                'cover_image': hit.cover_image,
            }
            for hit in results
        ]

        return paginator.get_paginated_response(serialized)


def image_proxy(request):
    """
    A view to proxy image requests from Mangadex to bypass
    hotlinking protection.
    """
    try:
        # 1. Get the target image URL from the query parameters
        image_url = request.GET.get('url')

        if not image_url:
            return JsonResponse(
                {'error': 'Image URL is required'}, status=400)

        allowed_host = 'mangadex.network'
        parsed_url = urlparse(image_url)

        if not parsed_url.hostname or (
                not parsed_url.hostname.endswith(allowed_host)):
            return JsonResponse({'error': 'Invalid host'}, status=403)

        response = requests.get(
            image_url,
            headers={
                'Referer': 'https://mangadex.org/'
            }
        )
        response.raise_for_status()

        if response.status_code == 200:
            content_type = response.headers.get(
                'Content-Type', 'image/jpeg')
            image_response = HttpResponse(
                response.content, content_type=content_type)

            # Add caching headers
            image_response[
                'Cache-Control'] = 'public, max-age=604800, immutable'
            return image_response
        else:
            return JsonResponse(
                {'error': 'Failed to fetch image from origin'},
                status=response.status_code)

    except requests.exceptions.RequestException as e:
        print(f"Image proxy error: {e}")
        return JsonResponse(
            {'error': 'Internal server error'}, status=500)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return JsonResponse(
            {'error': 'An unexpected error occurred'}, status=500)
