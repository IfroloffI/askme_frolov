from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import QuestionForm
from django.contrib.auth import logout
from .models import Profile, Tag, Question
from django.contrib.auth.views import LoginView


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
    paginator = Paginator(questions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
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
            return redirect('register')

    print("GET request or no POST data")
    return render(request, 'register.html', {
        'popular_users': popular_users,
        'popular_tags': popular_tags
    })


def paginate(objects_list, request, per_page=3, adjacent_pages=2):
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


def question(request, id_question):
    try:
        question_item = Question.objects.get(id=id_question)
    except Question.DoesNotExist:
        messages.error(request, "Question not found")
        return redirect('index')

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
    content = paginate(questions, request)

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
                   'avatar': request.user.profile.avatar})


def logout_view(request):
    logout(request)
    return redirect('index')
