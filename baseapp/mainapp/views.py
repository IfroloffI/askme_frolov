from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib import messages
from .forms import QuestionForm
from django.contrib.auth import logout
from .models import Profile, Tag, Question
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Question, Answer, QuestionLike, AnswerLike


@login_required
def toggle_correct_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    question = answer.question

    if request.user == question.user:
        answer.is_correct = not answer.is_correct
        answer.save()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=403)


@login_required
def question_detail(request, question_id):
    question = Question.objects.get(id=question_id)
    user_vote = None
    if QuestionLike.objects.filter(profile=request.user.profile, question=question).exists():
        user_vote = QuestionLike.objects.get(profile=request.user.profile, question=question).is_like

    return render(request, 'question_detail.html', {
        'question': question,
        'user_vote': user_vote,
    })


@login_required
def vote_question(request, question_id):
    question = Question.objects.get(id=question_id)
    user = request.user
    if QuestionLike.objects.filter(profile=user.profile, question=question).exists():
        like = QuestionLike.objects.get(profile=user.profile, question=question)
        if like.is_like:
            like.delete()
            question.rating -= 1
        else:
            like.is_like = True
            like.save()
            question.rating += 2
    else:
        QuestionLike.objects.create(profile=user.profile, question=question, is_like=True)
        question.rating += 1
    question.save()
    return JsonResponse({'rating': question.rating, 'is_like': True})


@login_required
def downvote_question(request, question_id):
    question = Question.objects.get(id=question_id)
    user = request.user
    if QuestionLike.objects.filter(profile=user.profile, question=question).exists():
        like = QuestionLike.objects.get(profile=user.profile, question=question)
        if not like.is_like:
            like.delete()
            question.rating += 1
        else:
            like.is_like = False
            like.save()
            question.rating -= 2
    else:
        QuestionLike.objects.create(profile=user.profile, question=question, is_like=False)
        question.rating -= 1
    question.save()
    return JsonResponse({'rating': question.rating, 'is_like': False})


@login_required
def vote_answer(request, answer_id):
    answer = Answer.objects.get(id=answer_id)
    user = request.user
    if AnswerLike.objects.filter(profile=user.profile, answer=answer).exists():
        like = AnswerLike.objects.get(profile=user.profile, answer=answer)
        if like.is_like:
            like.delete()
            answer.rating -= 1
        else:
            like.is_like = True
            like.save()
            answer.rating += 2
    else:
        AnswerLike.objects.create(profile=user.profile, answer=answer, is_like=True)
        answer.rating += 1
    answer.save()
    return JsonResponse({'rating': answer.rating, 'is_like': True})


@login_required
def downvote_answer(request, answer_id):
    answer = Answer.objects.get(id=answer_id)
    user = request.user
    if AnswerLike.objects.filter(profile=user.profile, answer=answer).exists():
        like = AnswerLike.objects.get(profile=user.profile, answer=answer)
        if not like.is_like:
            like.delete()
            answer.rating += 1
        else:
            like.is_like = False
            like.save()
            answer.rating -= 2
    else:
        AnswerLike.objects.create(profile=user.profile, answer=answer, is_like=False)
        answer.rating -= 1
    answer.save()
    return JsonResponse({'rating': answer.rating, 'is_like': False})


class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        popular_users = Profile.objects.popular_users()
        popular_tags = Tag.objects.popular_tags()

        context['popular_users'] = popular_users
        context['popular_tags'] = popular_tags

        return context


@login_required
def ask(request):
    popular_users = Profile.objects.popular_users()
    popular_tags = Tag.objects.popular_tags()

    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            tags_data = form.cleaned_data['tags']

            question = form.save(commit=False)
            question.user = request.user
            question.profile = request.user.profile
            question.save()

            tags = [tag.strip() for tag in tags_data.split(',')]
            for tag_name in tags:
                tag, created = Tag.objects.get_or_create(tag=tag_name)
                question.tags.add(tag)

            return redirect('home')

    else:
        form = QuestionForm()

    return render(request, 'ask.html', {'popular_users': popular_users,
                                        'popular_tags': popular_tags,
                                        'form': form})


def index(request):
    questions = Question.objects.all()
    page_obj = paginate(questions, request)
    popular_users = Profile.objects.popular_users()
    popular_tags = Tag.objects.popular_tags()

    return render(request, 'index.html', {
        'popular_users': popular_users,
        'popular_tags': popular_tags,
        'content': page_obj
    })


def register(request):
    popular_users = Profile.objects.popular_users()
    popular_tags = Tag.objects.popular_tags()

    if request.method == 'POST':
        print("Post request received")

        username = request.POST.get('login')
        email = request.POST.get('email')
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        avatar = request.FILES.get('avatar')

        if password != confirm_password:
            print("Passwords do not match")
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            print("Username already exists")
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            print("Email already exists")
            messages.error(request, "Email already exists.")
            return redirect('register')

        try:
            validate_email = EmailValidator()
            validate_email(email)
        except ValidationError:
            print("Invalid email address")
            messages.error(request, "Invalid email address.")
            return redirect('register')

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            print(f"User {username} created successfully")

            login(request, user)
            print(f"User {username} logged in successfully")

            return redirect('home')

        except Exception as e:
            print(f"Error during user creation: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('login')

    print("GET request or no POST data")
    return render(request, 'register.html', {
        'popular_users': popular_users,
        'popular_tags': popular_tags
    })


def paginate(objects_list, request, per_page=5, adjacent_pages=2):
    page_number = request.GET.get('page', 1)
    paginator = Paginator(objects_list, per_page)
    try:
        page_items = paginator.page(page_number)
    except PageNotAnInteger:
        page_items = paginator.page(1)
        page_number = 1
    except EmptyPage:
        page_items = paginator.page(paginator.num_pages)
        page_number = paginator.num_pages

    page_number = int(page_number)

    total_pages = paginator.num_pages
    start_page = max(page_number - adjacent_pages, 1)
    end_page = min(page_number + adjacent_pages, total_pages)
    rang = list(range(start_page, end_page + 1))
    return {
        'page_items': page_items,
        'page_number': page_number,
        'total_pages': total_pages,
        'rang': rang
    }


@login_required
def add_answer(request, id_question):
    if request.method == "POST":
        content = request.POST.get('content')
        question_item = get_object_or_404(Question, id=id_question)

        answer = Answer.objects.create(profile=request.user.profile, question=question_item, content=content)

        question_item.answer_count = question_item.answer_count + 1
        question_item.save()

        return redirect('question', id_question=id_question)

    return redirect('login')


@login_required
def delete_answer(request, id_answer):
    answer = get_object_or_404(Answer, id=id_answer)
    question = answer.question

    if request.method == "POST":
        answer.delete()
        question.answer_count = question.answer_count - 1
        question.save()

    return redirect('question', id_question=question.id)


def question(request, id_question):
    question_item = get_object_or_404(Question, id=id_question)
    question_item.answer_count = Answer.objects.filter(question=question_item).count()
    question_item.save()

    popular_users = Profile.objects.popular_users()
    popular_tags = Tag.objects.popular_tags()
    answers = Answer.objects.by_question(id_question)
    content = paginate(answers, request, per_page=5)

    context = {
        'content': content,
        'question': question_item,
        'popular_tags': popular_tags,
        'popular_users': popular_users,
    }

    return render(request, 'question.html', context)


def tag(request, id_tag):
    try:
        tag = Tag.objects.get(id=id_tag)
    except Tag.DoesNotExist:
        messages.error(request, "Tag not found")
        return redirect('index')

    popular_users = Profile.objects.popular_users()
    popular_tags = Tag.objects.popular_tags()
    questions = Question.objects.by_tag(tag)
    content = paginate(questions, request, per_page=5)

    context = {
        'content': content,
        'tag': tag,
        'popular_tags': popular_tags,
        'popular_users': popular_users,
    }

    return render(request, 'tag.html', context)


def hot(request):
    popular_users = Profile.objects.popular_users()
    popular_tags = Tag.objects.popular_tags()
    questions = Question.objects.hot()
    content = paginate(questions, request)

    return render(request, 'hot.html',
                  {'popular_users': popular_users, 'popular_tags': popular_tags, 'content': content})


@login_required
def settings(request):
    popular_users = Profile.objects.popular_users()
    popular_tags = Tag.objects.popular_tags()

    if request.method == 'POST':
        profile = request.user.profile
        nickname = request.POST.get('nickname')

        if not nickname:
            messages.error(request, 'Nickname cannot be empty.')
            return render(request, 'settings.html',
                          {'user': request.user, 'popular_tags': popular_tags,
                           'popular_users': popular_users,
                           'nickname': profile.nickname})

        profile.nickname = nickname

        if request.FILES.get('avatar'):
            profile.avatar = request.FILES['avatar']

        try:
            profile.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('settings')
        except ValidationError as e:
            messages.error(request, f'Error: {e}')
            return render(request, 'settings.html',
                          {'user': request.user, 'popular_tags': popular_tags,
                           'popular_users': popular_users,
                           'nickname': profile.nickname,
                           'avatar': profile.avatar})

    return render(request, 'settings.html',
                  {'user': request.user, 'popular_tags': popular_tags,
                   'popular_users': popular_users,
                   'nickname': request.user.profile.nickname,
                   'avatar': request.user.profile.avatar
                   })


def logout_view(request):
    logout(request)
    return redirect('index')
