from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .views import CustomLoginView

urlpatterns = [
                  path('', views.index, name='index'),
                  path('ask/', views.ask, name="ask"),
                  path('hot/', views.hot, name="hot"),
                  path('login/', CustomLoginView.as_view(), name='login'),
                  path('register/', views.register, name='register'),
                  path('logout/', views.logout_view, name='logout'),
                  path('question/<int:id_question>/', views.question, name="question"),
                  path('question/<int:id_question>/answer/', views.add_answer, name='add_answer'),
                  path('register/', views.register, name='register'),
                  path('settings/', views.settings, name='settings'),
                  path('tag/<int:id_tag>/', views.tag, name='tag'),
                  path('vote/question/<int:question_id>/up/', views.vote_question, name='vote_question_up'),
                  path('vote/question/<int:question_id>/down/', views.downvote_question, name='vote_question_down'),
                  path('vote/answer/<int:answer_id>/up/', views.vote_answer, name='vote_answer_up'),
                  path('vote/answer/<int:answer_id>/down/', views.downvote_answer, name='vote_answer_down'),
                  path('answer/<int:answer_id>/toggle_correct/', views.toggle_correct_answer,
                       name='toggle_correct_answer'),
                  path('search/', views.search_questions, name='search_questions'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
