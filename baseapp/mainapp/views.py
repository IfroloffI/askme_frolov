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
from .models import Profile, Tag, Question


@login_required
def ask(request):
    if not hasattr(request.user, 'profile'):
        # Профиль не существует, создаем его
        Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            tags_data = form.cleaned_data['tags']

            # Сохраняем вопрос
            question = form.save(commit=False)
            question.user = request.user  # Устанавливаем user
            question.profile = request.user.profile  # Устанавливаем профиль пользователя в поле profile
            question.save()

            # Сохраняем теги
            tags = [tag.strip() for tag in tags_data.split(',')]
            for tag_name in tags:
                tag, created = Tag.objects.get_or_create(tag=tag_name)
                question.tags.add(tag)

            return redirect('home')  # Перенаправляем на страницу с вопросами

    else:
        form = QuestionForm()

    return render(request, 'ask.html', {'form': form})


def index(request):
    popular_users = Profile.objects.popular_users()  # Получаем популярных пользователей
    questions = Question.objects.all()
    popular_tags = Tag.objects.popular_tags()  # Получаем популярные теги

    return render(request, 'index.html', {
        'popular_users': popular_users,  # Добавляем популярных пользователей в контекст
        'questions': questions,
        'popular_tags': popular_tags,  # Добавляем популярные теги
    })


def register(request):
    if request.method == 'POST':
        print("Post request received")  # Проверим, пришел ли POST запрос

        # Получаем данные из формы
        username = request.POST.get('login')
        email = request.POST.get('email')
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        avatar = request.FILES.get('avatar')

        # Проверим, что данные пришли правильно
        print(f"Username: {username}, Email: {email}, Nickname: {nickname}")

        # Валидация: проверка совпадения паролей
        if password != confirm_password:
            print("Passwords do not match")
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Валидация: проверка, существует ли уже пользователь с таким логином или email
        if User.objects.filter(username=username).exists():
            print("Username already exists")
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            print("Email already exists")
            messages.error(request, "Email already exists.")
            return redirect('register')

        # Валидация: проверка на корректность email
        try:
            validate_email = EmailValidator()
            validate_email(email)
        except ValidationError:
            print("Invalid email address")
            messages.error(request, "Invalid email address.")
            return redirect('register')

        print("I`m here!")  # Убедитесь, что эта строка выводится в консоль

        # Создание нового пользователя
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            print(f"User {username} created successfully")

            # Если у вас есть дополнительная информация (например, nickname, avatar), сохраняем их
            # Пример для профиля пользователя:
            # profile = Profile(user=user, nickname=nickname, avatar=avatar)
            # profile.save()

            # Автоматический вход после регистрации
            login(request, user)
            print(f"User {username} logged in successfully")

            # Перенаправление на главную страницу или на страницу профиля
            return redirect('home')  # или другую нужную страницу

        except Exception as e:
            print(f"Error during user creation: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('register')

    print("GET request or no POST data")
    return render(request, 'register.html')


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
    popular_tags = Tag.objects.popular_tags()  # Получаем популярные теги

    return render(request, 'hot.html', {'popular_users': popular_users, 'popular_tags': popular_tags})


@login_required
def settings(request):
    popular_tags = Tag.objects.popular_tags()  # Получаем популярные теги
    return render(request, 'settings.html', {'user': request.user, 'popular_tags': popular_tags})
