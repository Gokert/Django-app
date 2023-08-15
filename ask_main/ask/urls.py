"""
URL configuration for ask project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hot/', views.hot_questions, name='hot'),
    path('new/', views.new_questions, name='new'),
    path('tag/<str:t>/', views.tag_questions, name='tag'),
    path('question/<int:qid>/', views.question_page, name='question'),
    path('ask/', views.ask_page, name='ask'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup_page, name='signup'),
    path('settings/', views.settings_page, name='settings'),
    path('like/', views.like, name='like'),
    path('dislike/', views.dislike, name='dislike'),
    path('', views.new_questions),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
