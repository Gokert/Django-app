from django.core.cache import cache
from django.core.management import BaseCommand

from app.views import get_user_rating


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = get_user_rating()
        cache.set('rating', users, 70)