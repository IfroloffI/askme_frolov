from .rabbitmq import consume_messages
from .models import Answer
from django.core.cache import cache
from django.core.serializers import serialize
from django.conf import settings


def message_handler(message):
    if message['event'] == 'new_answer':
        answer_id = message['answer_id']
        try:
            answer = Answer.objects.get(id=answer_id)
            serialized_answer = {
                'id': answer.id,
                'content': answer.content,
                'username': answer.profile.user.username,
                'is_correct': answer.is_correct,
                'profile_avatar': answer.profile.avatar.url if answer.profile.avatar else None,
                'rating': answer.rating,
            }
            cache_key = f'answers_for_question_{answer.question.id}'
            current_answers = cache.get(cache_key, [])
            current_answers.append(serialized_answer)
            cache.set(cache_key, current_answers, timeout=60 * 3)

            print(f"New answer added for question {answer.question.id}: {answer_id}")

        except Answer.DoesNotExist:
            print(f"Answer with ID {answer_id} does not exist.")


if __name__ == '__main__':
    consume_messages(message_handler)
