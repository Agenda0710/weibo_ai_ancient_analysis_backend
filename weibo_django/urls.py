"""
URL configuration for weibo_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from Dashboard import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # 获取首页数据
    path('article_statistics/', views.get_article_statistics, name='get_article_statistics'),
    # 获取热词数据
    path('hotWords/', views.get_hot_words_statistics, name='get_hot_words_statistics'),
    # 获取第三页（微博舆情统计)
    path('articles/', views.get_articles_with_comments, name='articles_list'),
    # 获取第四页（文章分析）
    path('articleAnalysis/', views.article_analysis, name='article_analysis'),
    # 获取第五页数据（IP分析）
    path('regionAnalysis/', views.region_analysis, name='region_analysis'),
    # 获取第六页数据（评论分析）
    path('commentsAnalysis/', views.comments_analysis, name='comments_analysis')
]
