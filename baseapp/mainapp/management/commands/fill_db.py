import random
import string
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ... import models


def generate_unique_username(existing_usernames):
    while True:
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        if username not in existing_usernames:
            return username


class Command(BaseCommand):
    help = 'Populate the database with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Scaling factor for data generation')

    def handle(self, *args, **options):
        ratio = options['ratio']

        # Удаляем существующие данные
        deleted_profiles, _ = models.Profile.objects.all().delete()
        deleted_tags, _ = models.Tag.objects.all().delete()
        deleted_questions, _ = models.Question.objects.all().delete()

        deleted_users, _ = User.objects.all().delete()
        self.stdout.write(f'Deleted {deleted_profiles} profiles and {deleted_users} users.')

        # Генерация пользователей и их профилей
        users = []
        existing_usernames = set()

        for i in range(ratio):
            username = generate_unique_username(existing_usernames)
            existing_usernames.add(username)
            email = f'user_{i}@example.com'
            password = 'password'

            user = User.objects.create_user(username=username, email=email, password=password)
            # profile = models.Profile.objects.create(user=user, nickname=f"Nickname_{i}")
            users.append(user)

        # Генерация тегов
        tags = [models.Tag.objects.create(tag=f'tag_{i}') for i in range(10)]

        # Генерация вопросов
        questions = []
        for i in range(ratio * 10):
            user = random.choice(users)
            profile = user.profile  # Теперь профиль существует
            question = models.Question.objects.create(
                title=f'Question {i}',
                content=f'Sample question content for question {i}',
                user=user,
                profile=profile,
                rating=random.randint(0, 100),
                answer_count=0
            )

            tags_cnt = random.randint(1, 5)
            question.tags.set(random.sample(tags, k=tags_cnt))

            questions.append(question)

        self.stdout.write(self.style.SUCCESS('Database populated successfully'))