from django.core.management.base import BaseCommand
from django.core.cache import cache
from ... import models


class Command(BaseCommand):
    help = 'Обновляет кэш пользователей и тегов'

    def handle(self, *args, **kwargs):
        popular_users = models.Profile.objects.popular_users()
        popular_tags = models.Tag.objects.popular_tags()
        cache.set('popular_users', popular_users, timeout=60 * 5)
        cache.set('popular_tags', popular_tags, timeout=60 * 5)
        self.stdout.write(self.style.SUCCESS('Кэш обновлен успешно.'))
