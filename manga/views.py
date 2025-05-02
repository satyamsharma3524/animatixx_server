from rest_framework.views import APIView
# from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from elasticsearch_dsl.query import MultiMatch
from manga.documents import MangaDocument


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
                MultiMatch(
                    query=query,
                    fields=[
                        'title^3',
                        'description',
                        'tags'
                    ],
                    fuzziness='auto'
                )
            )

        if tags:
            for tag in tags:
                search = search.filter('term', tags=tag)

        if completed in ['true', 'false']:
            is_completed = completed.lower() == 'true'
            search = search.filter('term', completion_status=is_completed)

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
