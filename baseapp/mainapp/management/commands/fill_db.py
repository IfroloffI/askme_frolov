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
        models.Profile.objects.all().delete()
        User.objects.all().delete()

        # Генерация пользователей и профилей
        users = []
        existing_usernames = set()

        for i in range(ratio):
            username = generate_unique_username(existing_usernames)
            existing_usernames.add(username)
            email = f'user_{i}@example.com'
            password = 'password'

            user = User.objects.create_user(username=username, email=email, password=password)
            profile = models.Profile.objects.create(user=user, nickname=f"Nickname_{i}")

            users.append(user)

        # Генерация тегов
        tags = [models.Tag.objects.create(tag=f'tag_{i}') for i in range(10)]

        # Генерация вопросов
        questions = []
        for i in range(ratio * 10):
            user = random.choice(users)
            profile = user.profile
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

        # Генерация ответов и лайков на ответы
        for i in range(ratio * 10):
            random_user = random.choice(users)
            random_profile = random_user.profile
            random_question = random.choice(questions)

            answer = models.Answer.objects.create(
                profile=random_profile,
                question=random_question,
                content=f'Sample answer content for question {random_question.id}',
                rating=random.randint(0, 50)
            )

            random_question.answer_count += 1
            random_question.save()

            # Генерация лайков на ответ
            random_user = random.choice(users)
            models.AnswerLike.objects.get_or_create(
                answer=answer,
                profile=random_user.profile,
                is_like=random.choice([True, False])
            )

        # Генерация лайков на вопросы
        for i in range(ratio * 200):
            random_user = random.choice(users)
            random_profile = random_user.profile
            random_question = random.choice(questions)

            models.QuestionLike.objects.get_or_create(
                question=random_question,
                profile=random_profile,
                is_like=random.choice([True, False])
            )

            random_question.rating += 1 if random.choice([True, False]) else -1
            random_question.save()

        self.stdout.write(self.style.SUCCESS('Database populated successfully'))
