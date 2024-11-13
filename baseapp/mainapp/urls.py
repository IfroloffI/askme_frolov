from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('', views.index, name="index"),
    path('ask/', views.ask, name="ask"),
    path('hot/', views.hot, name="hot"),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('question/<int:id>/', views.question, name="question"),
    path('register/', views.register, name='register'),
    path('settings/', views.settings, name='settings'),
    path('tag/<int:id_tag>/', views.tag, name='tag'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
