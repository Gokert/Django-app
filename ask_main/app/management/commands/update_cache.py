from django.core.cache import cache
from django.core.management import BaseCommand
from app.models import Profile, Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = Profile.objects.get_top_users()
        tags = Tag.objects.get_top_tags()
        cache.set('rating', users, 300)
        cache.set('rating_tags', tags, 300)