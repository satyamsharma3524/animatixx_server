from django_elasticsearch_dsl import Document, Index, fields
# from django_elasticsearch_dsl.registries import registry
from manga.models import Manga

# Define the Elasticsearch index
manga_index = Index('manga')


@manga_index.doc_type
class MangaDocument(Document):
    tags = fields.ListField(fields.TextField())

    class Django:
        model = Manga
        fields = [
            'title',
            'description',
            'original_language',
            'completion_status',
            'cover_image',
        ]

    # Custom method to serialize tags
    def prepare_tags(self, instance):
        return [tag.title for tag in instance.tags.all()]
