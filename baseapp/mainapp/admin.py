from django.contrib import admin

# Register your models here.
from .models import Question, Answer, Tag, Profile, QuestionLike, AnswerLike

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Tag)
admin.site.register(Profile)
admin.site.register(QuestionLike)
admin.site.register(AnswerLike)

# Пагинация ответов
# Кнопка правильного ответа correct
# Поправить пагинацию