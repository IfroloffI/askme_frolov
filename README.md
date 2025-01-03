# Быстрый старт на Windows:
0. Создать в директории A:\PycharmProjects\askme_frolov\baseapp\nginx папки:
    - cache
    - logs
    - temp
1. Из директории A:\PycharmProjects\askme_frolov\baseapp\nginx запустить NginX по аналогии с данным запуском (с использованием конфига):
```bash
C:\tools\nginx-1.27.3\nginx -c A:\PycharmProjects\askme_frolov\baseapp\nginx\conf\nginx.conf
```
2. В директории A:\PycharmProjects\askme_frolov\baseapp запустить:
```bash
python simple_wsgi.py
 ```
Для запуска без балансировщика:
3*. В директории A:\PycharmProjects\askme_frolov\baseapp запустить:
```bash
python manage.py runserver
```
4. В директории A:\PycharmProjects\askme_frolov\baseapp запустить
(Брокер сообщений RabitMQ):
```bash
python run_consumer.py
```
5. - Пользоваться с WSGI: localhost:80 (localhost:8081 - Waitress WSGI)
   - Django-сервер: localhost:8000
## ДЗ № 1
- [ + ] Верстка общего вида страницы
- [ + ] Верстка списка вопросов на главной странице (index)
- [ + ] Верстка страницы одного вопроса (question)
- [ + ] Верстка формы добавления вопроса (ask)
- [ + ] Верстка форм логина и регистрации (login, registration)

## ДЗ № 2
- [ + ] Создание директории проекта
- [ + ] Создание django проекта и приложения
- [ + ] Отображение данных
- [ + ] Маршрутизация URL
- [ + ] Шаблонизация
- [ + ] Функция пагинации

## ДЗ № 3
- [ + ] Проектирование модели
- [ + ] ModelManager и методы моделей
- [ + ] Наполнение данными
- [ + ] Отображение данных
- [ + ] Использование СУБД

# Промежуточное ревью
В ходе промежуточной проверки выявлены следующие недочёты, требующие исправления:
- [ + ] Поправить пагинацию вопросов, везде использовать custum`ную
- [ + ] Добавить пагинацию ответов
- [ + ] Добавить: Кнопка правильного ответа correct
## 42 / 46 Баллов

# ДЗ № 4
- [ + ] Вход на сайт
- [ + ] Регистрация на сайте
- [ + ] Выход с сайта
- [ + ] Добавление вопроса
- [ + ] Добавление ответа

# ДЗ № 5
- [ + ] Загрузка и отображение аватарок пользователей
- [ + ] Страница редактирования профиля
- [ + ] Лайки вопросов и ответов
- [ + ] Отметка “правильный ответ”
- [ + ] Проверка авторизации, csrf, метода запроса, авторства

# ДЗ № 6
- [ + ] Настройка nginx для отдачи статического контента
- [ + ] Настройка gunicorn для запуска wsgi приложений 
  ( Использую альтернативу waitress)
- [ + ] Создание WSGI-приложения
- [ ] Оценка производительности nginx и gunicorn (Работает и норм =) )

# ДЗ № 7
- [ + ] Real-time сообщения (Предпочитаю использовать брокер сообщений, например RabbitMQ)
- [ + ] Блок популярные теги
- [ + ] Блок лучшие пользователи
- [ + ] Поиск по заголовку и содержимому вопроса
