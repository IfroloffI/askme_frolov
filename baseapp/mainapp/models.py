from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta


class QuestionManager(models.Manager):
    def all(self):
        return self.order_by('-created_at')

    def by_tag(self, tag):
        return self.filter(tags__tag=tag).order_by('-rating', '-created_at')

    def hot(self):
        return self.order_by('-rating', '-created_at')


class TagManager(models.Manager):
    def popular_tags(self):
        three_months_ago = timezone.now() - timedelta(days=90)
        return self.annotate(
            question_count=Count('question', filter=Q(question__created_at__gte=three_months_ago))
        ).order_by('-question_count')[:10]


class ProfileManager(models.Manager):
    def popular_users(self):
        one_week_ago = timezone.now() - timedelta(days=7)
        return self.annotate(
            question_count=Count('question', filter=Q(question__created_at__gte=one_week_ago)),
            answer_count=Count('answer', filter=Q(answer__created_at__gte=one_week_ago))
        ).order_by('-question_count', '-answer_count')[:10]

    def get_user_profile(self, user):
        return self.get(user=user)


class AnswerManager(models.Manager):
    def by_question(self, pk):
        return self.filter(question=pk).order_by('-is_correct', '-rating', 'created_at')


class Tag(models.Model):
    tag = models.CharField(unique=True, max_length=32, verbose_name='Tag')
    rating = models.IntegerField(default=0, verbose_name='Rating')

    objects = TagManager()

    def __str__(self):
        return self.tag


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    nickname = models.CharField(max_length=30)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    followers_count = models.PositiveIntegerField(default=0)
    objects = ProfileManager()

    def __str__(self):
        return f"{self.user.username}"


class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Author')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
    rating = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)
    objects = QuestionManager()

    def __str__(self):
        return self.title


class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Question')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Author')
    is_like = models.BooleanField(default=True)

    def __str__(self):
        action = 'disliked' if not self.is_like else 'liked'
        return f'{self.profile.user.get_username()} {action} question "{self.question.title}"'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['question', 'profile'], name='unique_question_like')
        ]


class Answer(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Author')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Question')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
    is_correct = models.BooleanField(default=False)

    objects = AnswerManager()

    def __str__(self):
        return f'Answer for "{self.question.title}"'


class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, verbose_name='Answer')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Author')
    is_like = models.BooleanField(default=True)

    def __str__(self):
        action = 'disliked' if not self.is_like else 'liked'
        return f'{self.profile.user.get_username()} {action} answer "{self.answer.content}"'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['answer', 'profile'], name='unique_answer_like')
        ]
